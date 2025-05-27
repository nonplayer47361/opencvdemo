import json
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor
from braille.braille_translator import parse_to_braille_cells  # 반드시 풀스펙 매핑 테이블에 의존하는 braille_translator 사용!
from datetime import datetime
import os
import re
from typing import Tuple, Any

def sanitize_filename(text: str, prefix: str = "braille") -> str:
    """
    텍스트를 안전한 파일명으로 변환
    """
    safe_text = re.sub(r'[^가-힣a-zA-Z0-9]', '_', text)
    safe_text = safe_text.strip('_') or "braille"
    safe_text = safe_text[:30]
    dt = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{dt}_{safe_text}_dot.png"

def draw_braille_cell(
    img: np.ndarray,
    x0: int,
    y0: int,
    pattern: list,
    point_r: int,
    xgap: int,
    ygap: int,
    dot_color: Tuple[int, int, int] = (0,0,0)
) -> None:
    """
    6점 점자 셀을 이미지에 그림
    """
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

def make_braille_image_and_saveinfo(
    text: str,
    dpi: int = 300,
    max_cols: int = 20,
    save_dir: str = "data",
    n_workers: int = 4
) -> Tuple[str, np.ndarray, str, Any]:
    """
    텍스트 → 점자 셀 → 이미지, 변환 정보(json) 저장
    Returns: (img_path, numpy_image, info_path, info_dict)
    """
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

    def draw_cell_worker(args):
        k, pattern = args
        row = k // max_cols
        col = k % max_cols
        x0 = cell_x_px * col + cell_x_px // 2 - xgap_px // 2
        y0 = cell_y_px * row + cell_y_px // 2 - ygap_px
        draw_braille_cell(img, x0, y0, pattern, point_r_px, xgap_px, ygap_px, dot_color=(0,0,0))

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        list(executor.map(draw_cell_worker, enumerate(braille_cells)))

    os.makedirs(save_dir, exist_ok=True)
    img_filename = sanitize_filename(text)
    img_path = os.path.join(save_dir, img_filename)
    cv2.imwrite(img_path, img)

    # 변환 정보 json 저장
    info = {
        "text": text,
        "braille_cells": braille_cells,
        "image_path": img_filename,
        "created_at": datetime.now().isoformat()
    }
    info_filename = img_filename.replace('_dot.png', '.json')
    info_path = os.path.join(save_dir, info_filename)
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    return img_path, img, info_path, info