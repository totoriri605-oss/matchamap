import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from cafeapp.management.commands.apply_taste_scores import IDENTITY_FIELDS
from cafeapp.models import Cafe


class ApplyTasteScoresTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.plan_path = Path(self.tmp.name) / 'plan.json'
        self.backup_path = Path(self.tmp.name) / 'backup.json'
        self.cafe = Cafe.objects.create(name='Keep', area='성수', address='서울', menu_name='Matcha',
                                        price=6000, description='Keep description', image='cafes/keep.png',
                                        bitterness=2)
        self.plan = {'version': 1, 'entries': [{
            'id': self.cafe.pk,
            'expected': {field: getattr(self.cafe, field) for field in IDENTITY_FIELDS},
            'scores': {'matcha_strength': 4, 'bitterness': 5},
            'reason': 'Test evidence', 'sources': ['local:test'],
        }]}

    def run_plan(self, **options):
        self.plan_path.write_text(json.dumps(self.plan), encoding='utf-8')
        call_command('apply_taste_scores', str(self.plan_path), stdout=StringIO(), **options)

    def test_preview_has_no_database_or_backup_changes(self):
        before = list(Cafe.objects.values())
        self.run_plan()
        self.assertEqual(before, list(Cafe.objects.values()))
        self.assertFalse(self.backup_path.exists())

    def test_apply_only_fills_null_and_preserves_every_other_field(self):
        before = Cafe.objects.values().get(pk=self.cafe.pk)
        self.run_plan(apply=True, backup=self.backup_path)
        expected = dict(before, matcha_strength=4)
        self.assertEqual(Cafe.objects.values().get(pk=self.cafe.pk), expected)
        backup = json.loads(self.backup_path.read_text(encoding='utf-8'))
        self.assertEqual(backup['cafes_before'][0]['matcha_strength'], None)
        self.assertEqual(backup['cafes_before'][0]['bitterness'], 2)
        self.run_plan(apply=True, backup=self.backup_path)  # Idempotent, existing scores skipped.
        self.assertEqual(Cafe.objects.values().get(pk=self.cafe.pk), expected)

    def test_no_apply_without_backup(self):
        with self.assertRaises(CommandError):
            self.run_plan(apply=True)
        self.cafe.refresh_from_db()
        self.assertIsNone(self.cafe.matcha_strength)

    def test_existing_backup_is_not_overwritten(self):
        self.backup_path.write_text('keep', encoding='utf-8')
        with self.assertRaises(CommandError):
            self.run_plan(apply=True, backup=self.backup_path)
        self.assertEqual(self.backup_path.read_text(), 'keep')
        self.cafe.refresh_from_db()
        self.assertIsNone(self.cafe.matcha_strength)

    def test_changed_identity_aborts_whole_plan(self):
        second = dict(self.plan['entries'][0], id=self.cafe.pk + 999)
        self.plan['entries'].append(second)
        with self.assertRaises(CommandError):
            self.run_plan(apply=True, backup=self.backup_path)
        self.cafe.refresh_from_db()
        self.assertIsNone(self.cafe.matcha_strength)
        self.assertFalse(self.backup_path.exists())

    def test_invalid_scores_and_non_taste_fields_rejected(self):
        for scores in ({'price': 4}, {'aroma': 3}, {'sweetness': 0}, {'milkiness': 6}, {'bitterness': True}):
            with self.subTest(scores=scores):
                self.plan['entries'][0]['scores'] = scores
                with self.assertRaises(CommandError):
                    self.run_plan(apply=True, backup=self.backup_path)
        self.cafe.refresh_from_db()
        self.assertIsNone(self.cafe.matcha_strength)
