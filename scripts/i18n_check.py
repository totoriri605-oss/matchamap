"""템플릿의 번역 대상 문구와 locale/en/LC_MESSAGES/django.po를 비교한다.

실행: python scripts/i18n_check.py
- MISSING : 템플릿에 있는데 .po에 없거나 번역문이 비어 있는 문구(영어 화면에 한국어로 보임)
- OBSOLETE: .po에는 있는데 템플릿에서 더 이상 쓰지 않는 문구
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PO = ROOT / 'locale' / 'en' / 'LC_MESSAGES' / 'django.po'

TRANS_RE = re.compile(r'{%\s*trans\s+"((?:[^"\\]|\\.)*)"')
BLOCK_RE = re.compile(r'{%\s*blocktrans\b[^%]*%}(.*?){%\s*(?:plural|endblocktrans)', re.S)
VAR_RE = re.compile(r'{{\s*(\w+)\s*}}')
PY_RE = re.compile(r"\b_\('((?:[^'\\]|\\.)*)'\)")


def template_msgids():
    found = {}
    for path in (ROOT / 'cafeapp' / 'templates').rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        for m in TRANS_RE.finditer(text):
            found.setdefault(m.group(1), path.name)
        for m in BLOCK_RE.finditer(text):
            body = VAR_RE.sub(r'%(\1)s', m.group(1)).strip()
            found.setdefault(' '.join(body.split()), path.name)
    # 파이썬 코드의 _('...') (gettext / gettext_lazy 별칭)
    for path in (ROOT / 'cafeapp').glob('*.py'):
        if path.name.startswith('test') or path.name.startswith('import_'):
            continue
        for m in PY_RE.finditer(path.read_text(encoding='utf-8')):
            found.setdefault(m.group(1), path.name)
    return found


def unescape(text):
    return text.replace('\\"', '"').replace('\\\\', '\\')


def po_entries():
    entries, msgid, msgstr, cur = {}, None, None, None
    for line in PO.read_text(encoding='utf-8').splitlines():
        if line.startswith('msgid_plural'):
            cur = None
        elif line.startswith('msgid '):
            if msgid is not None:
                entries[msgid] = msgstr
            msgid, msgstr, cur = line[6:].strip()[1:-1], '', 'id'
        elif line.startswith('msgstr'):
            cur = 'str'
            msgstr = line.split('"', 1)[1].rsplit('"', 1)[0] if '"' in line else ''
        elif line.startswith('"') and cur == 'id':
            msgid += line.strip()[1:-1]
        elif line.startswith('"') and cur == 'str':
            msgstr += line.strip()[1:-1]
    if msgid is not None:
        entries[msgid] = msgstr
    entries.pop('', None)
    return {unescape(k): v for k, v in entries.items()}


def dynamic_msgids():
    """'#. dynamic' 표시가 붙은 항목은 템플릿 변수로 번역하므로 낡은 문구로 보지 않는다."""
    ids, flag = set(), False
    for line in PO.read_text(encoding='utf-8').splitlines():
        if line.startswith('#. dynamic'):
            flag = True
        elif line.startswith('msgid ') and flag:
            ids.add(line[6:].strip()[1:-1])
            flag = False
    return ids


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    tpl, po = template_msgids(), po_entries()
    missing = [(k, f) for k, f in tpl.items() if not po.get(k)]
    dynamic = dynamic_msgids()
    obsolete = [k for k in po if k not in tpl and k not in dynamic]
    print(f'templates: {len(tpl)}  po: {len(po)}')
    print(f'\nMISSING ({len(missing)})')
    for k, f in missing:
        print(f'  [{f}] {k}')
    print(f'\nOBSOLETE ({len(obsolete)})')
    for k in obsolete:
        print(f'  {k}')
