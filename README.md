# 🟡 점자 변환/복원 웹 데모 (Braille Web Demo)

한글/영문/숫자/특수문자/약자(축약) 텍스트를 **점자(6점식) 이미지·유니코드로 변환**하고,  
점자 이미지를 **텍스트로 복원**하는 Python + Flask + JS 기반의 오픈소스 데모입니다.

---

## 💡 주요 기능

- **텍스트 → 점자 이미지 변환**
    - 한글, 영문, 숫자, 특수문자, 약자(축약어) 지원
    - 점자 6점식 표준 매핑(`braille_table.py`) 기반
    - PNG 이미지로 변환 및 다운로드
- **텍스트 → 점자 유니코드 변환**
    - 점자 유니코드 문자열로 바로 변환 (복사 가능)
- **점자 이미지 → 텍스트 복원**
    - 업로드한 점자 이미지를 OCR하여 원문 텍스트 복원 (알파/베타)
- **웹 데모 제공**
    - `/index.html` 또는 `/` 접속 시 바로 사용 가능
    - API 별도 제공

---

## 🚀 데모 실행 방법

### 1. 환경 준비

```bash
python -m venv venv
source venv/bin/activate   # (윈도우: venv\Scripts\activate)
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
python main.py
```

### 3. 웹 접근

- 브라우저에서 [http://localhost:5000/index.html](http://localhost:5000/index.html) 접속

---

## 🛠️ 주요 파일 구조

```
braille.web_demo/
├── main.py                    # Flask 진입점(API 서버)
├── index.html                 # 웹 프론트엔드 데모
├── requirements.txt
├── app/                       # (Flask 앱 디렉토리, 필요시)
├── braille/
│   ├── braille_table.py           # 점자 매핑 테이블(풀스펙)
│   ├── braille_translator.py      # 텍스트↔점자(유니코드/비트) 변환
│   ├── braille_image_utils.py     # 점자 이미지 생성/복원 유틸
│   ├── braille_converter.py       # 변환 통합(이미지+유니코드+역변환)
│   ├── braille_image_restore.py   # 이미지→텍스트 복원
│   └── text_to_braille_bits.py    # 텍스트→점자 비트 변환 서브
├── scripts/
│   └── save_braile_parallel.py    # 점자 이미지 병렬 생성 스크립트
└── data/                      # 변환 결과(이미지, json 등) 저장 폴더
```

---

## 🌐 API 엔드포인트

- **POST `/api/text-to-braille-image`**  
    - 입력: `{ "text": "안녕하세요" }`
    - 출력: PNG 이미지(blob)
- **POST `/api/text-to-braille-unicode`**  
    - 입력: `{ "text": "hi123" }`
    - 출력: `{ "braille_unicode": "⠓⠊⠼⠁⠃⠉" }`
- **POST `/api/braille-image-to-text`**
    - 입력: 파일 업로드(`file`)
    - 출력: `{ "text": "복원된 텍스트" }`

---

## 📝 기여 및 문의

- Pull Request 환영!
- 점자 매핑/복원 알고리즘, 웹UI, 기타 개선 제안은 Issue로 남겨주세요.
- (c) 2024-2025 [프로젝트 팀/작성자]
