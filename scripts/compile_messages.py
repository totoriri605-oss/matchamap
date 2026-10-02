"""locale/*/LC_MESSAGES/django.po 를 django.mo 로 컴파일한다(gettext 설치 불필요).

실행: python scripts/compile_messages.py
Django의 `manage.py compilemessages`는 msgfmt(gettext)가 필요한데, 이 PC에는 없어서 대신 쓴다.
복수형(msgid_plural)과 여러 줄 문자열, 'fuzzy' 표시를 처리한다.
"""
import ast
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_po(path):
    messages = {}
    msgid = msgid_plural = None
    msgstrs = {}
    section = None
    fuzzy = False
    skip_next = False

    def flush():
        nonlocal msgid, msgid_plural, msgstrs, skip_next
        if msgid is not None and not skip_next:
            if msgid_plural is not None:
                key = msgid + '\0' + msgid_plural
                value = '\0'.join(msgstrs[i] for i in sorted(msgstrs))
            else:
                key, value = msgid, msgstrs.get(0, '')
            if value.replace('\0', '') or key == '':
                messages[key] = value
        msgid = msgid_plural = None
        msgstrs = {}
        skip_next = False

    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if line.startswith('#,'):
            fuzzy = 'fuzzy' in line
            continue
        if line.startswith('#') or not line:
            continue
        if line.startswith('msgid_plural'):
            msgid_plural = ast.literal_eval(line[len('msgid_plural'):].strip())
            section = 'plural'
        elif line.startswith('msgid'):
            flush()
            skip_next = fuzzy and line != 'msgid ""'
            fuzzy = False
            msgid = ast.literal_eval(line[len('msgid'):].strip())
            section = 'id'
        elif line.startswith('msgstr['):
            index = int(line[line.index('[') + 1:line.index(']')])
            msgstrs[index] = ast.literal_eval(line[line.index(']') + 1:].strip())
            section = index
        elif line.startswith('msgstr'):
            msgstrs[0] = ast.literal_eval(line[len('msgstr'):].strip())
            section = 0
        elif line.startswith('"'):
            text = ast.literal_eval(line)
            if section == 'id':
                msgid += text
            elif section == 'plural':
                msgid_plural += text
            else:
                msgstrs[section] += text
    flush()
    return messages


def write_mo(messages, path):
    keys = sorted(messages)
    ids = strs = b''
    offsets = []
    for key in keys:
        k, v = key.encode('utf-8'), messages[key].encode('utf-8')
        offsets.append((len(ids), len(k), len(strs), len(v)))
        ids += k + b'\0'
        strs += v + b'\0'
    n = len(keys)
    keystart = 7 * 4 + 16 * n
    valuestart = keystart + len(ids)
    koffsets, voffsets = [], []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    header = struct.pack('Iiiiiii', 0x950412DE, 0, n, 7 * 4, 7 * 4 + n * 8, 0, 0)
    path.write_bytes(header + struct.pack(f'{len(koffsets)}i', *koffsets)
                     + struct.pack(f'{len(voffsets)}i', *voffsets) + ids + strs)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for po in sorted((ROOT / 'locale').glob('*/LC_MESSAGES/django.po')):
        messages = parse_po(po)
        mo = po.with_suffix('.mo')
        write_mo(messages, mo)
        print(f'{po.relative_to(ROOT)} -> {mo.name}: {len(messages) - 1} messages')
