"""
한글 <-> 점자 유니코드 변환 (표준 braille_table.py 연동)
"""

from braille.braille_table import (
    INITIAL_TO_BRAILLE, MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE,
    BRAILLE_TO_INITIAL, BRAILLE_TO_MEDIAL, BRAILLE_TO_FINAL
)

def decompose_hangul(syllable):
    code = ord(syllable)
    if 0xAC00 <= code <= 0xD7A3:
        syllable_index = code - 0xAC00
        initial = syllable_index // 588
        medial = (syllable_index % 588) // 28
        final = syllable_index % 28
        cho_list = [
            'ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
            'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
        ]
        jung_list = [
            'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ',
            'ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'
        ]
        jong_list = [
            '', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ',
            'ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
        ]
        return cho_list[initial], jung_list[medial], jong_list[final]
    else:
        return None, None, None

def assemble_braille_cell(bits):
    """6비트(리스트) -> 유니코드 점자"""
    code = 0
    for i, bit in enumerate(bits):
        if bit:
            code |= (1 << i)
    return chr(0x2800 + code)

def text_to_braille(text):
    result = []
    for ch in text:
        cho, jung, jong = decompose_hangul(ch)
        if cho and jung is not None:
            cells = []
            if cho in INITIAL_TO_BRAILLE:
                cells.append(assemble_braille_cell(INITIAL_TO_BRAILLE[cho]))
            if jung in MEDIAL_TO_BRAILLE:
                cells.append(assemble_braille_cell(MEDIAL_TO_BRAILLE[jung]))
            if jong and jong in FINAL_TO_BRAILLE:
                bits = FINAL_TO_BRAILLE[jong]
                if isinstance(bits[0], list):  # 겹받침
                    for b in bits:
                        cells.append(assemble_braille_cell(b))
                else:
                    cells.append(assemble_braille_cell(bits))
            result.append(''.join(cells))
        else:
            result.append(ch)
    return ' '.join(result)

def braille_to_text(braille_str):
    result = []
    for cell_str in braille_str.split():
        cells = [ord(c) - 0x2800 for c in cell_str]
        def code_to_bits(code):
            return [(code >> i) & 1 for i in range(6)]
        bits_list = [code_to_bits(code) for code in cells]
        cho = BRAILLE_TO_INITIAL.get(tuple(bits_list[0]), '')
        jung = BRAILLE_TO_MEDIAL.get(tuple(bits_list[1]), '') if len(bits_list) > 1 else ''
        jong = ''
        if len(bits_list) > 2:
            if tuple(bits_list[2:4]) in BRAILLE_TO_FINAL:
                jong = BRAILLE_TO_FINAL[tuple(bits_list[2:4])]
            else:
                jong = BRAILLE_TO_FINAL.get(tuple(bits_list[2]), '')
        try:
            cho_list = [
                'ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
                'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
            ]
            jung_list = [
                'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ',
                'ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'
            ]
            jong_list = [
                '', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ',
                'ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
            ]
            cho_idx = cho_list.index(cho) if cho in cho_list else 11
            jung_idx = jung_list.index(jung) if jung in jung_list else 0
            jong_idx = jong_list.index(jong) if jong in jong_list else 0
            code = 0xAC00 + (cho_idx * 21 * 28) + (jung_idx * 28) + jong_idx
            result.append(chr(code))
        except Exception:
            result.append('?')
    return ''.join(result)

if __name__ == "__main__":
    sample = "가나다"
    braille = text_to_braille(sample)
    print(f"[한글] {sample} -> [점자] {braille}")
    text = braille_to_text(braille)
    print(f"[점자] {braille} -> [한글] {text}")