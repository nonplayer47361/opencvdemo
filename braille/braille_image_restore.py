"""
점자 이미지(PNG 등) → 텍스트 복원 (풀스펙 점자 매핑/변환 모듈과 호환)
"""
import numpy as np
import cv2
from braille_translator import braille_to_text  # 풀스펙 매핑이 적용된 모듈에서 import
from typing import List

# 6점좌표 (col, row) 기준
DOT_COORDS = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]

def decode_braille_image(
    img_path: str,
    dpi: int = 300,
    max_cols: int = 20,
    cell_height_mm: float = 10.0,
    cell_width_mm: float = 6.0,
    dot_diameter_mm: float = 1.5,
    verbose: bool = False
) -> str:
    """
    점자 이미지 파일을 읽어서 텍스트로 복원
    Args:
        img_path: 이미지 경로
        dpi: 이미지 해상도(Dots Per Inch)
        max_cols: 최대 열 수(한 줄의 셀 개수)
        cell_height_mm: 셀 높이(mm)
        cell_width_mm: 셀 너비(mm)
        dot_diameter_mm: 점 반지름(mm)
        verbose: 디버그 정보 출력
    Returns:
        복원된 텍스트(str)
    """
    mm2px = lambda mm: int(round(mm * dpi / 25.4))
    cell_h = mm2px(cell_height_mm)
    cell_w = mm2px(cell_width_mm)
    dot_r = max(mm2px(dot_diameter_mm)//2, 2)
    xgap = mm2px(2.5)
    ygap = mm2px(2.5)

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"이미지 파일을 읽을 수 없습니다: {img_path}")

    # 점 검출 (이진화 + 윤곽선)
    blur = cv2.GaussianBlur(img, (5,5), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    for cnt in contours:
        (x, y), r = cv2.minEnclosingCircle(cnt)
        if r >= dot_r * 0.7:  # 점 크기 필터링
            centers.append((int(round(x)), int(round(y))))
    if verbose:
        print(f"[DEBUG] 검출된 점 개수: {len(centers)}")

    # 이미지 크기와 셀 grid 추정
    img_h, img_w = img.shape
    ncol = min(max_cols, img_w // cell_w)
    nrow = img_h // cell_h
    ncell = nrow * ncol

    patterns: List[List[int]] = []
    cell_count = 0
    for row in range(nrow):
        for col in range(ncol):
            if cell_count >= ncell:
                break
            x0 = col * cell_w + cell_w // 2 - xgap // 2
            y0 = row * cell_h + cell_h // 2 - ygap
            bits = []
            for dx, dy in DOT_COORDS:
                cx = int(round(x0 + dx * xgap))
                cy = int(round(y0 + dy * ygap))
                found = any(abs(cx - x) <= dot_r and abs(cy - y) <= dot_r for (x, y) in centers)
                bits.append(1 if found else 0)
            patterns.append(bits)
            cell_count += 1
        if cell_count >= ncell:
            break

    # trailing blank cell(빈 셀) 제거
    while patterns and patterns[-1] == [0,0,0,0,0,0]:
        patterns.pop()

    if verbose:
        print("[DEBUG] 점자 6비트 패턴 리스트:")
        for i, p in enumerate(patterns):
            print(f"{i}: {p}")

    # 6비트 리스트 → 텍스트
    restored_text = braille_to_text(patterns, is_unicode=False)
    return restored_text

# 메인 실행부는 별도 스크립트에서 import해서 사용 권장
if __name__ == "__main__":
    import sys
    import os
    img_path = input("복원할 점자 이미지 파일 경로: ").strip()
    if not os.path.isfile(img_path):
        print("파일이 존재하지 않습니다.")
        sys.exit(1)
    text = decode_braille_image(img_path, verbose=True)
    print(f"\n[복원 결과] {repr(text)}")