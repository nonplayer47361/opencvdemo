"""
한글/영문/숫자/약자/특수문자 텍스트 <-> 점자(6점식 유니코드/비트) 변환
- 표준 braille_table.py (풀스펙) 연동
"""

import hgtk
from .braille_table import (
    INITIAL_TO_BRAILLE, MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE,
    HANGUL_BRAILLE_ABBREVIATION, ENGLISH_TO_BRAILLE,
    CAPITAL_PREFIX, NUMBER_PREFIX, NUM_TO_BRAILLE_LETTER,
    SPECIAL_TO_BRAILLE,
    BRAILLE_TO_INITIAL, BRAILLE_TO_MEDIAL, BRAILLE_TO_FINAL,
    BRAILLE_TO_HANGUL_ABBREVIATION, BRAILLE_TO_ENGLISH, BRAILLE_TO_SPECIAL,
    BRAILLE_TO_CAPITAL_PREFIX, BRAILLE_TO_NUMBER_PREFIX
)

def decompose_hangul(syllable):
    """한글 음절을 (초성, 중성, 종성) 분해. 아니면 (None, None, None) 반환."""
    try:
        cho, jung, jong = hgtk.letter.decompose(syllable)
        return cho, jung, jong
    except hgtk.exception.NotHangulException:
        return None, None, None

def assemble_braille_cell(bits):
    """6비트 리스트 -> 유니코드 점자 문자"""
    code = 0
    for i, bit in enumerate(bits):
        if bit:
            code |= (1 << i)
    return chr(0x2800 + code)

def text_to_braille(text, use_unicode=True):
    """모든 한글/영문/숫자/특수/약자 텍스트 -> 점자(유니코드 or 비트 리스트) 변환"""
    result = []
    i = 0
    while i < len(text):
        matched = False
        # 한글 약자(최장매칭)
        for key in sorted(HANGUL_BRAILLE_ABBREVIATION.keys(), key=len, reverse=True):
            if text[i:i+len(key)] == key:
                bits = HANGUL_BRAILLE_ABBREVIATION[key]
                # 약자값이 셀 2개 이상(겹받침/복합)일 경우
                if isinstance(bits[0], list):
                    for b in bits:
                        result.append(assemble_braille_cell(b) if use_unicode else b)
                else:
                    result.append(assemble_braille_cell(bits) if use_unicode else bits)
                i += len(key)
                matched = True
                break
        if matched:
            continue

        ch = text[i]
        cho, jung, jong = decompose_hangul(ch)
        if cho is not None:
            if cho in INITIAL_TO_BRAILLE:
                b = INITIAL_TO_BRAILLE[cho]
                result.append(assemble_braille_cell(b) if use_unicode else b)
            if jung in MEDIAL_TO_BRAILLE:
                b = MEDIAL_TO_BRAILLE[jung]
                result.append(assemble_braille_cell(b) if use_unicode else b)
            if jong is not None and jong in FINAL_TO_BRAILLE:
                bits = FINAL_TO_BRAILLE[jong]
                # 겹받침(2셀 이상)
                if isinstance(bits[0], list):
                    for b in bits:
                        result.append(assemble_braille_cell(b) if use_unicode else b)
                else:
                    result.append(assemble_braille_cell(bits) if use_unicode else bits)
            i += 1
            continue

        # 영문자 (대소문자/숫자 구분)
        if ch.isalpha():
            if ch.isupper():
                if use_unicode:
                    result.append(assemble_braille_cell(CAPITAL_PREFIX))
                else:
                    result.append(CAPITAL_PREFIX)
            lower = ch.lower()
            if lower in ENGLISH_TO_BRAILLE:
                b = ENGLISH_TO_BRAILLE[lower]
                result.append(assemble_braille_cell(b) if use_unicode else b)
            else:
                result.append(assemble_braille_cell([0,0,0,0,0,0]) if use_unicode else [0]*6)
            i += 1
            continue

        # 숫자
        if ch.isdigit():
            if use_unicode:
                result.append(assemble_braille_cell(NUMBER_PREFIX))
            else:
                result.append(NUMBER_PREFIX)
            for digit in ch:
                letter = NUM_TO_BRAILLE_LETTER[digit]
                b = ENGLISH_TO_BRAILLE[letter]
                result.append(assemble_braille_cell(b) if use_unicode else b)
            i += 1
            continue

        # 특수문자
        if ch in SPECIAL_TO_BRAILLE:
            b = SPECIAL_TO_BRAILLE[ch]
            result.append(assemble_braille_cell(b) if use_unicode else b)
            i += 1
            continue

        # 공백
        if ch.isspace():
            result.append(assemble_braille_cell([0,0,0,0,0,0]) if use_unicode else [0]*6)
            i += 1
            continue

        # 정의되지 않은 문자
        result.append(assemble_braille_cell([0,0,0,0,0,0]) if use_unicode else [0]*6)
        i += 1
    # Unicode 점자일 경우, 셀 사이를 공백 없이 반환
    if use_unicode:
        return ''.join(result)
    return result

def parse_to_braille_cells(text):
    """텍스트를 점자 6비트 배열 리스트로 변환"""
    return text_to_braille(text, use_unicode=False)

def braille_to_text(braille, is_unicode=True):
    """점자(유니코드 문자열 or 6비트 리스트) -> 원문 텍스트 복원"""
    result = []
    cells = []
    # 유니코드 점자라면 문자별 6비트 추출
    if is_unicode:
        for c in braille:
            code = ord(c) - 0x2800
            bits = [(code>>i)&1 for i in range(6)]
            cells.append(bits)
    else:
        cells = braille

    i = 0
    n = len(cells)
    while i < n:
        # 1. 한글 약자/약어(최장매칭)
        abbr_matched = False
        for k, v in BRAILLE_TO_HANGUL_ABBREVIATION.items():
            abbr_len = len(k) if isinstance(k, tuple) and isinstance(k[0], tuple) else 1
            if abbr_len == 1 and tuple(cells[i]) == k:
                result.append(v)
                i += 1
                abbr_matched = True
                break
            elif abbr_len > 1 and tuple(cells[i:i+abbr_len]) == k:
                result.append(v)
                i += abbr_len
                abbr_matched = True
                break
        if abbr_matched:
            continue

        # 2. 한글(초/중/종)
        if i+2 < n:
            ini = BRAILLE_TO_INITIAL.get(tuple(cells[i]), None)
            med = BRAILLE_TO_MEDIAL.get(tuple(cells[i+1]), None)
            jong = ''
            next_is_complex = False
            for key, val in BRAILLE_TO_FINAL.items():
                if isinstance(key, tuple) and isinstance(key[0], tuple) and tuple(cells[i+2:i+2+len(key)]) == key:
                    jong = val
                    next_is_complex = True
                    break
            if not next_is_complex:
                jong = BRAILLE_TO_FINAL.get(tuple(cells[i+2]), '')
            if ini and med is not None:
                try:
                    char = hgtk.letter.compose(ini, med, jong)
                except Exception:
                    char = '?'
                result.append(char)
                i += 2 + (len(key) if next_is_complex else 1)
                continue

        # 3. 영문 대문자 prefix
        if tuple(cells[i]) == BRAILLE_TO_CAPITAL_PREFIX:
            if i+1 < n:
                ch = BRAILLE_TO_ENGLISH.get(tuple(cells[i+1]), '?')
                result.append(ch.upper())
                i += 2
                continue

        # 4. 숫자 prefix
        if tuple(cells[i]) == BRAILLE_TO_NUMBER_PREFIX:
            num = []
            idx = i + 1
            while idx < n:
                digit_ch = BRAILLE_TO_ENGLISH.get(tuple(cells[idx]), None)
                if digit_ch and digit_ch in NUM_TO_BRAILLE_LETTER.values():
                    for k, v in NUM_TO_BRAILLE_LETTER.items():
                        if v == digit_ch:
                            num.append(k)
                            break
                else:
                    break
                idx += 1
            result.append(''.join(num))
            i = idx
            continue

        # 5. 영문자
        ch = BRAILLE_TO_ENGLISH.get(tuple(cells[i]), None)
        if ch:
            result.append(ch)
            i += 1
            continue

        # 6. 특수문자
        spec = BRAILLE_TO_SPECIAL.get(tuple(cells[i]), None)
        if spec:
            result.append(spec)
            i += 1
            continue

        # 7. 공백
        if cells[i] == [0,0,0,0,0,0]:
            result.append(' ')
            i += 1
            continue

        # 8. 기타
        result.append('?')
        i += 1
    return ''.join(result)

if __name__ == "__main__":
    sample = "가나다 abc 123 그럼!"
    print(f"[입력] {sample}")
    braille = text_to_braille(sample, use_unicode=True)
    print(f"[점자(unicode)] {braille}")
    restored = braille_to_text(braille, is_unicode=True)
    print(f"[복원] {restored}")