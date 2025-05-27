"""
텍스트(한글/영문/숫자/특수/약자) → 점자 6비트 패턴/이미지 변환 (풀스펙 braille_table.py 연동)
"""

import hgtk
import numpy as np
import cv2
import re
from .braille_table import (
    INITIAL_TO_BRAILLE, MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE,
    HANGUL_BRAILLE_ABBREVIATION, ENGLISH_TO_BRAILLE,
    CAPITAL_PREFIX, NUMBER_PREFIX, NUM_TO_BRAILLE_LETTER,
    SPECIAL_TO_BRAILLE
)

def sanitize_filename(text):
    filename = re.sub(r'[^가-힣a-zA-Z0-9]', '_', text).strip('_')
    return filename[:30] + "_dot.png"

def parse_to_braille_cells(text):
    """텍스트를 점자 6비트 리스트(셀 단위) 시퀀스로 변환"""
    cells = []
    i = 0
    while i < len(text):
        matched = False
        # 한글 약자(최장매칭)
        for key in sorted(HANGUL_BRAILLE_ABBREVIATION.keys(), key=len, reverse=True):
            if text.startswith(key, i):
                bits = HANGUL_BRAILLE_ABBREVIATION[key]
                # 약자값이 셀 2개 이상(겹/복합)인지 체크
                if isinstance(bits[0], list):
                    for b in bits:
                        cells.append(list(b))
                else:
                    cells.append(list(bits))
                i += len(key)
                matched = True
                break
        if matched:
            continue
        ch = text[i]
        # 한글 음절
        if hgtk.checker.is_hangul(ch):
            try:
                cho, jung, jong = hgtk.letter.decompose(ch)
                cells.append(list(INITIAL_TO_BRAILLE.get(cho, [0]*6)))
                cells.append(list(MEDIAL_TO_BRAILLE.get(jung, [0]*6)))
                fin = FINAL_TO_BRAILLE.get(jong, [0]*6)
                if isinstance(fin[0], list):  # 겹받침(2셀)
                    for b in fin:
                        cells.append(list(b))
                else:
                    cells.append(list(fin))
            except Exception:
                cells.append([0]*6)
            i += 1
            continue
        # 영문자
        if ch.isalpha():
            if ch.isupper():
                cells.append(list(CAPITAL_PREFIX))
            lower = ch.lower()
            b = ENGLISH_TO_BRAILLE.get(lower, [0]*6)
            cells.append(list(b))
            i += 1
            continue
        # 숫자
        if ch.isdigit():
            cells.append(list(NUMBER_PREFIX))
            for digit in ch:
                letter = NUM_TO_BRAILLE_LETTER[digit]
                b = ENGLISH_TO_BRAILLE.get(letter, [0]*6)
                cells.append(list(b))
            i += 1
            continue
        # 특수문자
        if ch in SPECIAL_TO_BRAILLE:
            b = SPECIAL_TO_BRAILLE[ch]
            cells.append(list(b))
            i += 1
            continue
        # 공백
        if ch.isspace():
            cells.append([0]*6)
            i += 1
            continue
        # 미정의 문자
        cells.append([0]*6)
        i += 1
    return cells

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

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import platform
    text = input('한글/영문/숫자/특수/축약 입력: ')
    path, cell_count = make_braille_image(text)
    img = cv2.imread(path)
    # 한글 폰트 설정(플랫폼별)
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