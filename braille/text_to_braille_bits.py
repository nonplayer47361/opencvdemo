import hgtk
import numpy as np
import cv2

# 표준 점자 테이블 import
from braille.braille_table import (
    INITIAL_TO_BRAILLE,
    MEDIAL_TO_BRAILLE,
    FINAL_TO_BRAILLE,
    ENGLISH_TO_BRAILLE,
    CAPITAL_PREFIX,
    NUMBER_PREFIX,
    NUM_TO_BRAILLE_LETTER,
    HANGUL_BRAILLE_ABBREVIATION
)

def decompose_syllable(char):
    if not hgtk.checker.is_hangul(char):
        return None, None, None
    try:
        cho, jung, jong = hgtk.letter.decompose(char)
    except hgtk.exception.NotHangulException:
        return None, None, None
    return cho, jung, jong

def get_braille_pattern(cho, jung, jong):
    initial = INITIAL_TO_BRAILLE.get(cho, [0,0,0,0,0,0])
    medial = MEDIAL_TO_BRAILLE.get(jung, [0,0,0,0,0,0])
    finals = []
    f = FINAL_TO_BRAILLE.get(jong)
    if isinstance(f, list) and f and isinstance(f[0], list):
        finals = f
    elif jong in FINAL_TO_BRAILLE:
        finals = [FINAL_TO_BRAILLE[jong]]
    else:
        finals = [[0,0,0,0,0,0]]
    return [initial, medial] + finals

def parse_to_braille_cells(text):
    braille_cells = []
    i = 0
    while i < len(text):
        matched = False
        # 약자(축약어) 먼저 검사
        for key in sorted(HANGUL_BRAILLE_ABBREVIATION.keys(), key=len, reverse=True):
            if text[i:i+len(key)] == key:
                braille_cells.append(HANGUL_BRAILLE_ABBREVIATION[key])
                i += len(key)
                matched = True
                break
        if matched:
            continue
        ch = text[i]
        cho, jung, jong = decompose_syllable(ch)
        if cho is not None:
            patterns = get_braille_pattern(cho, jung, jong)
            braille_cells.extend(patterns)
            i += 1
            continue
        if ch.isalpha():
            if ch.isupper():
                braille_cells.append(CAPITAL_PREFIX)
            braille_cells.append(ENGLISH_TO_BRAILLE.get(ch.lower(), [0,0,0,0,0,0]))
            i += 1
            continue
        if ch.isdigit():
            braille_cells.append(NUMBER_PREFIX)
            for digit in ch:
                letter = NUM_TO_BRAILLE_LETTER[digit]
                braille_cells.append(ENGLISH_TO_BRAILLE[letter])
            i += 1
            continue
        if ch.isspace():
            braille_cells.append([0,0,0,0,0,0])  # 빈 셀(띄어쓰기)
        else:
            braille_cells.append([0,0,0,0,0,0])  # 미정의 문자는 빈 셀
        i += 1
    return braille_cells

def sanitize_filename(text):
    import re
    filename = re.sub(r'[^가-힣a-zA-Z0-9]', '_', text)
    filename = filename.strip('_')
    if not filename:
        filename = "braille"
    return filename[:30] + "_dot.png"

def draw_braille_cell(img, x0, y0, pattern, point_r, xgap, ygap, dot_color=(0,0,0)):
    coords = [
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2)
    ]
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
    point_d_mm = 1.5
    point_r_px = max(mm2px(point_d_mm) // 2, 2)
    xgap_px   = mm2px(2.5)
    ygap_px   = mm2px(2.5)
    cell_x_px = mm2px(6.0)
    cell_y_px = mm2px(10.0)

    braille_cells = parse_to_braille_cells(text)
    ncell = len(braille_cells)
    nrow = (ncell + max_cols - 1) // max_cols
    ncol = min(ncell, max_cols)

    img_w = cell_x_px * ncol
    img_h = cell_y_px * nrow
    img = np.ones((img_h, img_w, 3), dtype=np.uint8) * 255

    for k, pattern in enumerate(braille_cells):
        row = k // max_cols
        col = k % max_cols
        x0 = cell_x_px * col + cell_x_px // 2 - xgap_px // 2
        y0 = cell_y_px * row + cell_y_px // 2 - ygap_px
        draw_braille_cell(img, x0, y0, pattern, point_r_px, xgap_px, ygap_px, dot_color=(0,0,0))

    if not save_path:
        save_path = sanitize_filename(text)
    cv2.imwrite(save_path, img)
    print(f"이미지를 파일로 저장했습니다: {save_path}")
    return img

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    text = input('한글/영문/숫자/축약어 입력: ')
    img = make_braille_image(text, dpi=300, max_cols=20)
    plt.imshow(img)
    plt.axis('off')
    plt.title(f"Braille: {text}")
    plt.show()