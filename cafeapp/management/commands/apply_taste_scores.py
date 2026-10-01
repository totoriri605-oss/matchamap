"""Apply reviewed taste scores only to NULL fields; preview by default."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.utils import timezone

from cafeapp.models import Cafe


TASTE_FIELDS = {'matcha_strength', 'bitterness', 'sweetness', 'milkiness', 'matcha_aroma'}
IDENTITY_FIELDS = {'name', 'country', 'city', 'address', 'menu_name'}
GUARD_FIELDS = IDENTITY_FIELDS | {'description', 'matchayojung_comment'}


class Command(BaseCommand):
    help = 'Preview a reviewed JSON plan. --apply requires a new --backup file; never replaces existing scores.'

    def add_arguments(self, parser):
        parser.add_argument('plan', type=Path)
        parser.add_argument('--apply', action='store_true')
        parser.add_argument('--backup', type=Path)

    def handle(self, *args, **options):
        try:
            plan = json.loads(options['plan'].read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise CommandError(f'Cannot read plan: {exc}') from exc
        if not isinstance(plan, dict) or plan.get('version') != 1 or not isinstance(plan.get('entries'), list):
            raise CommandError('Expected version 1 and an entries list.')
        seen = set()
        for entry in plan['entries']:
            if not isinstance(entry, dict) or type(entry.get('id')) is not int or entry['id'] in seen:
                raise CommandError('Every entry needs a unique integer Cafe id.')
            seen.add(entry['id'])
            guards, scores = entry.get('expected'), entry.get('scores')
            if not isinstance(guards, dict) or not IDENTITY_FIELDS <= guards.keys() or not guards.keys() <= GUARD_FIELDS:
                raise CommandError('Expected identity must include name, country, city, address and menu_name.')
            if not all(isinstance(value, str) for value in guards.values()):
                raise CommandError('Identity values must be strings.')
            if not isinstance(scores, dict) or not scores or not scores.keys() <= TASTE_FIELDS:
                raise CommandError('Only the five taste fields can be updated.')
            if any(type(value) is not int or not 1 <= value <= 5 for value in scores.values()):
                raise CommandError('Scores must be integers from 1 to 5.')
            if not entry.get('reason') or not entry.get('sources'):
                raise CommandError('Every entry needs a reason and sources.')
        if options['apply'] and not options['backup']:
            raise CommandError('--apply requires --backup; existing files are never overwritten.')

        # A single transaction prevents partially-applied plans. Identity checks
        # protect deployments where ids or representative menus differ.
        with transaction.atomic():
            before = list(Cafe.objects.order_by('id').values())
            by_id = {row['id']: row for row in before}
            expected_after = {pk: dict(row) for pk, row in by_id.items()}
            changes = []
            for entry in plan['entries']:
                row = by_id.get(entry['id'])
                if row is None or any(row[key] != value for key, value in entry['expected'].items()):
                    raise CommandError(f"Cafe {entry['id']}: identity/evidence changed. Nothing applied.")
                for field, value in entry['scores'].items():
                    if row[field] is not None:
                        self.stdout.write(f"SKIP {row['id']} {field}: existing value {row[field]}")
                        continue
                    changes.append((entry, field, value))
                    expected_after[row['id']][field] = value
                    self.stdout.write(f"PLAN {row['id']} {row['name']} {field}: NULL -> {value}")

            if not options['apply']:
                self.stdout.write(f'PREVIEW: {len(changes)} fields. Database unchanged.')
                return
            if not changes:
                self.stdout.write('No changes needed. Database unchanged.')
                return

            backup = options['backup']
            try:
                backup.parent.mkdir(parents=True, exist_ok=True)
                with backup.open('x', encoding='utf-8') as handle:
                    json.dump({'created_at': timezone.now(), 'plan': plan, 'cafes_before': before},
                              handle, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2)
            except OSError as exc:
                raise CommandError(f'Backup failed; database unchanged: {exc}') from exc

            for entry, field, value in changes:
                updated = Cafe.objects.filter(pk=entry['id'], **entry['expected'],
                                              **{f'{field}__isnull': True}).update(**{field: value})
                if updated != 1:
                    raise CommandError('Concurrent change detected. All score updates rolled back.')
            after = {row['id']: row for row in Cafe.objects.order_by('id').values()}
            if after != expected_after:
                raise CommandError('Unexpected Cafe changes detected. All updates rolled back.')
        self.stdout.write(self.style.SUCCESS(f'APPLIED: {len(changes)} fields; all other Cafe fields preserved. Backup: {backup}'))
