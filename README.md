# 점자 변환/복원 웹 데모

## 주요 구조

- `app/main.py` : Flask API 서버 (텍스트-점자 변환/복원, 변환 정보 자동 저장)
- `braille/` : 점자 관련 공용 모듈 및 유틸리티
    - `braille_image_utils.py` : 텍스트→점자 이미지+변환정보(json) 동시 저장 (딥러닝 학습 데이터 활용 가능)
- `static/index.html` : 웹 UI
- `data/` : 변환 정보(json)와 점자 이미지 자동 저장 (학습 데이터셋으로 사용)
- `uploads/` : 업로드된 점자 이미지 임시 저장

## 예시
- 텍스트→점자 이미지 변환 시,  
  - `data/` 폴더에  
    - `braille_20240527_120000_안녕하세요_dot.png`  
    - `braille_20240527_120000_안녕하세요.json`  
  가 동시에 생성됩니다.
- 점자 이미지→텍스트 복원 시에도 복원 결과가 `data/restore_YYYYMMDD_HHMMSS.json`에 저장됩니다.

## 기타 참고
- `requirements.txt`에 flask, opencv-python, hgtk 등 필요 라이브러리 명시
- .gitignore로 venv, __pycache__, uploads, data 등 관리