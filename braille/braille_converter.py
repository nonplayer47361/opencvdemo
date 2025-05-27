"""
한글/영문/숫자/특수/약자 텍스트 <-> 점자(6점식 유니코드 및 6비트) <-> 점자 이미지 변환 통합 모듈
- 표준(국립국어원 등) 점자 매핑 내장
- 외부 의존성: hgtk, numpy, opencv-python, matplotlib (이미지 시각화시)
"""

import hgtk
import numpy as np
import cv2
import re
import os

# ---------------------- 점자 매핑 테이블 (국립국어원 + 국제관습) ----------------------

INITIAL_TO_BRAILLE = {
    'ㄱ': [1,0,0,0,0,0], 'ㄴ': [1,1,0,0,0,0], 'ㄷ': [1,0,0,1,0,0],
    'ㄹ': [1,1,0,1,0,0], 'ㅁ': [1,0,1,0,0,0], 'ㅂ': [1,1,1,0,0,0],
    'ㅅ': [0,1,0,1,0,0], 'ㅇ': [0,1,1,1,0,0], 'ㅈ': [0,1,0,1,1,0],
    'ㅊ': [0,1,0,1,0,1], 'ㅋ': [1,0,1,1,0,0], 'ㅌ': [1,1,1,1,0,0],
    'ㅍ': [1,0,1,1,1,0], 'ㅎ': [0,1,1,1,1,0], 'ㄲ': [1,0,0,0,1,0],
    'ㄸ': [1,0,0,1,1,0], 'ㅃ': [1,1,1,0,1,0], 'ㅆ': [0,1,0,1,1,0],
    'ㅉ': [0,1,0,1,1,1],
}
MEDIAL_TO_BRAILLE = {
    'ㅏ': [0,1,1,0,0,0], 'ㅑ': [0,1,1,0,1,0], 'ㅓ': [0,1,0,0,1,0],
    'ㅕ': [0,1,0,0,1,1], 'ㅗ': [0,0,1,0,1,0], 'ㅛ': [1,1,0,1,1,0],
    'ㅜ': [1,0,0,1,1,0], 'ㅠ': [1,1,0,0,1,1], 'ㅡ': [0,1,0,1,1,0],
    'ㅣ': [0,0,1,0,0,0], 'ㅐ': [0,1,1,1,0,0], 'ㅒ': [0,1,1,1,1,0],
    'ㅔ': [0,1,1,1,1,1], 'ㅖ': [0,1,1,1,1,1], 'ㅚ': [0,0,1,1,1,0],
    'ㅟ': [1,1,0,0,0,1], 'ㅢ': [0,1,0,1,0,1], 'ㅙ': [0,1,1,1,0,1],
    'ㅞ': [1,1,0,1,1,1], 'ㅝ': [1,0,0,1,1,1], 'ㅘ': [0,1,1,0,1,1],
}
FINAL_TO_BRAILLE = {
    '':   [0,0,0,0,0,0],
    'ㄱ': [1,0,0,0,0,0], 'ㄲ': [1,0,0,0,1,0],
    'ㄴ': [1,1,0,0,0,0], 'ㄷ': [1,0,0,1,0,0],
    'ㄹ': [1,1,0,1,0,0], 'ㅁ': [1,0,1,0,0,0],
    'ㅂ': [1,1,1,0,0,0], 'ㅅ': [0,1,0,1,0,0],
    'ㅇ': [0,1,1,1,0,0], 'ㅈ': [0,1,0,1,1,0],
    'ㅊ': [0,1,0,1,0,1], 'ㅋ': [1,0,1,1,0,0],
    'ㅌ': [1,1,1,1,0,0], 'ㅍ': [1,0,1,1,1,0],
    'ㅎ': [0,1,1,1,1,0],
    # 겹받침 (셀 2개 이상)
    'ㄳ': [[1,0,0,0,0,0], [0,1,0,1,0,0]],
    'ㄵ': [[1,1,0,0,0,0], [0,1,0,1,1,0]], 'ㄶ': [[1,1,0,0,0,0], [0,1,1,1,1,0]],
    'ㄺ': [[1,1,0,1,0,0], [1,0,0,0,0,0]], 'ㄻ': [[1,1,0,1,0,0], [1,0,1,0,0,0]],
    'ㄼ': [[1,1,0,1,0,0], [1,1,1,0,0,0]], 'ㄽ': [[1,1,0,1,0,0], [0,1,0,1,0,0]],
    'ㄾ': [[1,1,0,1,0,0], [1,1,1,1,0,0]], 'ㄿ': [[1,1,0,1,0,0], [1,0,1,1,1,0]],
    'ㅀ': [[1,1,0,1,0,0], [0,1,1,1,1,0]], 'ㅄ': [[1,1,1,0,0,0], [0,1,0,1,0,0]],
}
HANGUL_BRAILLE_ABBREVIATION = {
    "그래서":     [1,1,1,1,0,1],
    "그러나":     [1,1,1,0,0,0],
    "그러면":     [1,1,1,0,0,1],
    "그러므로":   [1,1,1,1,0,0],
    "그러니까":   [1,1,1,1,1,0],
    "그런데":     [1,1,1,0,1,0],
    "그런즉":     [1,1,1,0,1,1],
    "그리고":     [1,1,0,0,0,1],
    "그리하여":   [1,1,1,1,1,1],
    "하지만":     [0,1,1,1,1,0],
    "하지만은":   [0,1,1,1,1,1],
}
ENGLISH_TO_BRAILLE = {
    'a': [1,0,0,0,0,0], 'b': [1,1,0,0,0,0], 'c': [1,0,0,1,0,0],
    'd': [1,0,0,1,1,0], 'e': [1,0,0,0,1,0], 'f': [1,1,0,1,0,0],
    'g': [1,1,0,1,1,0], 'h': [1,1,0,0,1,0], 'i': [0,1,0,1,0,0],
    'j': [0,1,0,1,1,0], 'k': [1,0,1,0,0,0], 'l': [1,1,1,0,0,0],
    'm': [1,0,1,1,0,0], 'n': [1,0,1,1,1,0], 'o': [1,0,1,0,1,0],
    'p': [1,1,1,1,0,0], 'q': [1,1,1,1,1,0], 'r': [1,1,1,0,1,0],
    's': [0,1,1,1,0,0], 't': [0,1,1,1,1,0], 'u': [1,0,1,0,0,1],
    'v': [1,1,1,0,0,1], 'w': [0,1,0,1,1,1], 'x': [1,0,1,1,0,1],
    'y': [1,0,1,1,1,1], 'z': [1,0,1,0,1,1],
}
CAPITAL_PREFIX = [0,0,0,0,0,1]
NUMBER_PREFIX = [0,1,1,1,1,1]
NUM_TO_BRAILLE_LETTER = {'0':'j','1':'a','2':'b','3':'c','4':'d','5':'e','6':'f','7':'g','8':'h','9':'i'}
SPECIAL_TO_BRAILLE = {
    '.': [0,1,0,0,1,1], ',': [0,1,0,0,0,0], ';': [0,1,1,0,0,0], ':': [0,1,0,0,1,0],
    '?': [0,1,1,0,0,1], '!': [0,1,1,0,1,0], '-': [0,0,1,0,0,1], "'": [0,0,1,0,0,0],
    '"': [0,1,1,0,0,0], '“': [0,1,1,0,0,0], '”': [0,1,1,0,0,0],
    '(': [0,1,1,1,1,0], ')': [0,1,1,1,1,0], '/': [0,0,1,0,1,0], '_': [0,0,1,0,1,1],
    '@': [0,1,0,1,1,1], '#': [0,1,1,1,1,1], '*': [0,1,1,0,1,1], '&': [1,1,1,0,1,1],
    '%': [1,0,1,1,1,1], '=': [1,1,1,1,0,1], '+': [1,1,1,1,1,0], '<': [0,1,1,1,0,0],
    '>': [0,1,1,0,1,1], '[': [0,1,1,1,0,1], ']': [0,1,1,1,0,1], '{': [1,1,1,0,0,1],
    '}': [1,1,1,0,0,1], '\\': [0,0,1,1,0,1], '^': [0,0,1,1,1,0], '`': [0,0,1,1,1,1],
    '~': [0,1,1,1,1,1], '$': [1,0,1,0,1,1], '|': [0,0,1,1,0,0],
}

# ---------------------- 변환 함수 ----------------------

def decompose_hangul(syllable):
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
    """텍스트 -> 점자(유니코드 or 6비트 리스트)"""
    result = []
    i = 0
    while i < len(text):
        matched = False
        for key in sorted(HANGUL_BRAILLE_ABBREVIATION.keys(), key=len, reverse=True):
            if text.startswith(key, i):
                bits = HANGUL_BRAILLE_ABBREVIATION[key]
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
                if isinstance(bits[0], list):
                    for b in bits:
                        result.append(assemble_braille_cell(b) if use_unicode else b)
                else:
                    result.append(assemble_braille_cell(bits) if use_unicode else bits)
            i += 1
            continue
        if ch.isalpha():
            if ch.isupper():
                result.append(assemble_braille_cell(CAPITAL_PREFIX) if use_unicode else CAPITAL_PREFIX)
            lower = ch.lower()
            b = ENGLISH_TO_BRAILLE.get(lower, [0]*6)
            result.append(assemble_braille_cell(b) if use_unicode else b)
            i += 1
            continue
        if ch.isdigit():
            result.append(assemble_braille_cell(NUMBER_PREFIX) if use_unicode else NUMBER_PREFIX)
            for digit in ch:
                letter = NUM_TO_BRAILLE_LETTER[digit]
                b = ENGLISH_TO_BRAILLE.get(letter, [0]*6)
                result.append(assemble_braille_cell(b) if use_unicode else b)
            i += 1
            continue
        if ch in SPECIAL_TO_BRAILLE:
            b = SPECIAL_TO_BRAILLE[ch]
            result.append(assemble_braille_cell(b) if use_unicode else b)
            i += 1
            continue
        if ch.isspace():
            result.append(assemble_braille_cell([0]*6) if use_unicode else [0]*6)
            i += 1
            continue
        result.append(assemble_braille_cell([0]*6) if use_unicode else [0]*6)
        i += 1
    return ''.join(result) if use_unicode else result

def parse_to_braille_cells(text):
    """텍스트를 점자 6비트 배열 리스트로 변환 (이미지화 등 공용)"""
    return text_to_braille(text, use_unicode=False)

def sanitize_filename(text, prefix="braille"):
    safe_text = re.sub(r'[^가-힣a-zA-Z0-9]', '_', text).strip('_') or "braille"
    safe_text = safe_text[:30]
    return f"{prefix}_{safe_text}_dot.png"

def draw_braille_cell(img, x0, y0, pattern, point_r, xgap, ygap, dot_color=(0,0,0)):
    coords = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    for idx, dot in enumerate(pattern):
        if dot:
            dx, dy = coords[idx]
            cx = int(round(x0 + dx * xgap))
            cy = int(round(y0 + dy * ygap))
            cv2.circle(img, (cx, cy), point_r, dot_color, -1, lineType=cv2.LINE_AA)

def make_braille_image(
    text,
    dpi=300,
    max_cols=20,
    save_path=None
):
    mm2px = lambda mm: int(round(mm * dpi / 25.4))
    point_r = max(mm2px(1.5) // 2, 2)
    xgap = mm2px(2.5)
    ygap = mm2px(2.5)
    cell_w = mm2px(6.0)
    cell_h = mm2px(10.0)
    cells = parse_to_braille_cells(text)
    ncol = min(len(cells), max_cols)
    nrow = (len(cells) + max_cols - 1) // max_cols
    img = np.ones((cell_h * nrow, cell_w * ncol, 3), dtype=np.uint8) * 255
    for i, pattern in enumerate(cells):
        row, col = divmod(i, max_cols)
        x0 = col * cell_w + cell_w // 2 - xgap // 2
        y0 = row * cell_h + cell_h // 2 - ygap
        draw_braille_cell(img, x0, y0, pattern, point_r, xgap, ygap)
    filename = sanitize_filename(text) if not save_path else save_path
    cv2.imwrite(filename, img)
    return filename, len(cells)

def decode_braille_image(
    img_path,
    dpi=300,
    max_cols=20,
    cell_height_mm=10.0,
    cell_width_mm=6.0,
    dot_diameter_mm=1.5,
    verbose=False
):
    mm2px = lambda mm: int(round(mm * dpi / 25.4))
    cell_h = mm2px(cell_height_mm)
    cell_w = mm2px(cell_width_mm)
    dot_r = max(mm2px(dot_diameter_mm)//2, 2)
    xgap = mm2px(2.5)
    ygap = mm2px(2.5)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"이미지 파일을 읽을 수 없습니다: {img_path}")
    blur = cv2.GaussianBlur(img, (5,5), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    for cnt in contours:
        (x, y), r = cv2.minEnclosingCircle(cnt)
        if r >= dot_r * 0.7:
            centers.append((int(round(x)), int(round(y))))
    if verbose: print(f"[DEBUG] 검출된 점 개수: {len(centers)}")
    img_h, img_w = img.shape
    ncol = min(max_cols, img_w // cell_w)
    nrow = img_h // cell_h
    ncell = nrow * ncol
    patterns = []
    cell_count = 0
    coords = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    for row in range(nrow):
        for col in range(ncol):
            if cell_count >= ncell:
                break
            x0 = col * cell_w + cell_w // 2 - xgap // 2
            y0 = row * cell_h + cell_h // 2 - ygap
            bits = []
            for dx, dy in coords:
                cx = int(round(x0 + dx * xgap))
                cy = int(round(y0 + dy * ygap))
                found = any(abs(cx - x) <= dot_r and abs(cy - y) <= dot_r for (x, y) in centers)
                bits.append(1 if found else 0)
            patterns.append(bits)
            cell_count += 1
        if cell_count >= ncell:
            break
    while patterns and patterns[-1] == [0]*6:
        patterns.pop()
    if verbose:
        print("[DEBUG] 점자 6비트 패턴 리스트:")
        for i, p in enumerate(patterns):
            print(f"{i}: {p}")
    return braille_to_text(patterns, is_unicode=False)

def braille_to_text(braille, is_unicode=True):
    """점자(유니코드 문자열 or 6비트 리스트) -> 원문 텍스트 복원"""
    # (간단화: 복원 알고리즘 샘플, 실제 적용시 약자/복합 등 커버 필요)
    result = []
    cells = []
    if is_unicode:
        for c in braille:
            code = ord(c) - 0x2800
            bits = [(code>>i)&1 for i in range(6)]
            cells.append(bits)
    else:
        cells = braille
    # 아래는 예시, 실제 역매핑은 braille_table.py의 역딕셔너리 활용 필요
    for bits in cells:
        # 한글/영문/숫자/특수 복원 로직을 실제 역매핑 딕셔너리로 구현 필요
        result.append('?')  # (예시: 실제 역변환 구현 필요)
    return ''.join(result)

# ---------------------- 예제 main ----------------------

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import platform
    text = input('한글/영문/숫자/특수/약자 입력: ')
    print("[텍스트] ", text)
    braille_unicode = text_to_braille(text, use_unicode=True)
    print("[점자(유니코드)]", braille_unicode)
    braille_bits = parse_to_braille_cells(text)
    print("[점자(6비트리스트)]", braille_bits)
    path, cell_count = make_braille_image(text)
    img = cv2.imread(path)
    if platform.system() == 'Darwin':
        plt.rcParams['font.family'] = 'AppleGothic'
    elif platform.system() == 'Windows':
        plt.rcParams['font.family'] = 'Malgun Gothic'
    else:
        plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.title(f"Braille: {text}")
    plt.show()
    print(f"[✔] 점자 이미지 저장 ({path}), 셀 개수: {cell_count}")
    # 복원 예시 (실제 역변환 구현 필요)
    restored = decode_braille_image(path, verbose=True)
    print("[복원 결과]", restored)