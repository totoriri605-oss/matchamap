"""템플릿의 한국어 고정 문구를 {% trans "..." %} 로 감싼다(일회성 보조 도구).

실행: python scripts/wrap_trans.py <템플릿 경로> [...]
- <style>, <script> 블록은 건드리지 않는다.
- 태그 사이의 순수 텍스트와 aria-label/placeholder/alt/title 속성만 감싼다.
- {{ }} 나 {% %} 가 섞인 문구, 큰따옴표가 들어간 문구는 감싸지 않고 목록으로 알려준다(직접 처리).
"""
import re
import sys
from pathlib import Path

HANGUL = re.compile(r'[가-힣]')
SKIP_BLOCK = re.compile(r'(<style\b.*?</style>|<script\b.*?</script>)', re.S | re.I)
ATTR = re.compile(r'(\b(?:aria-label|placeholder|alt|title)=")([^"{}]*[가-힣][^"{}]*)(")')
TEXT = re.compile(r'>([^<>{}]*[가-힣][^<>{}]*)<')


def wrap_text(match, manual):
    raw = match.group(1)
    text = raw.strip()
    if '"' in text:
        manual.append(text)
        return match.group(0)
    lead = raw[: len(raw) - len(raw.lstrip())]
    trail = raw[len(raw.rstrip()):]
    return f'>{lead}{{% trans "{text}" %}}{trail}<'


def wrap_attr(match):
    return f'{match.group(1)}{{% trans "{match.group(2).strip()}" %}}{match.group(3)}'


def process(path):
    source = Path(path).read_text(encoding='utf-8')
    newline = '\r\n' if '\r\n' in source else '\n'
    source = source.replace('\r\n', '\n')
    manual = []
    parts = SKIP_BLOCK.split(source)
    for i, part in enumerate(parts):
        if i % 2:
            continue
        part = ATTR.sub(wrap_attr, part)
        part = TEXT.sub(lambda m: wrap_text(m, manual), part)
        parts[i] = part
    result = ''.join(parts)
    if '{% load' not in result or 'i18n' not in re.findall(r'{% load[^%]*%}', result).__str__():
        manual.append('(i18n load 확인 필요)')
    Path(path).write_text(result.replace('\n', newline), encoding='utf-8', newline='')
    left = []
    for i, part in enumerate(SKIP_BLOCK.split(result)):
        if i % 2:
            continue
        for line in part.split('\n'):
            stripped = re.sub(r'{%\s*trans\s+"[^"]*"\s*%}', '', line)
            stripped = re.sub(r'{%\s*blocktrans.*?{%\s*endblocktrans\s*%}', '', stripped)
            if HANGUL.search(stripped):
                left.append(line.strip()[:200])
    return manual, left


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for target in sys.argv[1:]:
        manual, left = process(target)
        print(f'== {target}')
        for item in manual:
            print('  [직접 처리]', item)
        for line in left:
            print('  [남은 한국어]', line)
