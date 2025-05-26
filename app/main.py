"""
Braille Web Demo 메인 진입점

- CLI 및 웹 서버 등 확장 가능
- 간단한 예시: 텍스트→점자 변환, 이미지 저장, 복원 결과 출력
"""

import sys
import os

# 점자 변환 함수 임포트 (구현체에 따라 아래 import 경로 확인 필요)
from braille.text_to_braille_bits import make_braille_image_verbose, decode_image_to_text

def main():
    print("=== Braille Web Demo ===")
    print("1: 한글/숫자/특수/축약/음절→점자 이미지 생성")
    print("2: 점자 이미지→텍스트 복원")
    mode = input("모드 선택 (1/2): ").strip()

    if mode == "1":
        text = input("변환할 텍스트 입력: ").strip()
        path, cell_count = make_braille_image_verbose(text)
        print(f"[✔] 점자 이미지 저장: {path} (셀 개수: {cell_count})")
        # 추가: 이미지 직접 보기 등은 웹/GUI에서 구현 권장
    elif mode == "2":
        img_path = input("점자 이미지 경로 입력 (.png): ").strip()
        if not os.path.isfile(img_path):
            print("이미지 파일이 존재하지 않습니다.")
            sys.exit(1)
        # 셀 개수 정보 파일 읽기(선택)
        len_path = img_path + ".len"
        cell_count = None
        if os.path.isfile(len_path):
            with open(len_path, encoding="utf-8") as f:
                cell_count = int(f.read().strip())
        else:
            cell_in = input("셀 개수(글자수×3, 엔터시 20): ").strip()
            cell_count = int(cell_in) if cell_in.isdigit() else 20
        result = decode_image_to_text(img_path, ncell=cell_count)
        print(f"[복원 결과] {result}")
    else:
        print("잘못된 입력입니다.")

if __name__ == "__main__":
    main()