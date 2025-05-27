"""
표준 한글/영문/숫자/약자/특수문자 점자 매핑 테이블 (국립국어원 기준 + 일반적 영문/수학 점자)
- 6점식 기준
- 각 딕셔너리의 value: [점1, 점2, 점3, 점4, 점5, 점6] (1=볼록, 0=평면)
- 복합(겹받침/약자 등): [ [...], [...] ] (셀 2개 이상)
- 역변환 테이블(점자 -> 문자) 포함
"""

# --- 한글 초성, 중성, 종성 ---
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

# --- 한글 약자/약어(표준 일부) ---
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
    # ... 필요시 전체 약자 표 추가 가능
}

# --- 영문 점자(Grade 1, 소문자) ---
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

# --- 특수문자/문장부호(6점식 일부, 표준/국제 관습) ---
SPECIAL_TO_BRAILLE = {
    '.': [0,1,0,0,1,1],        # 마침표
    ',': [0,1,0,0,0,0],        # 쉼표
    ';': [0,1,1,0,0,0],        # 쌍반점
    ':': [0,1,0,0,1,0],        # 쌍점
    '?': [0,1,1,0,0,1],        # 물음표
    '!': [0,1,1,0,1,0],        # 느낌표
    '-': [0,0,1,0,0,1],        # 하이픈
    "'": [0,0,1,0,0,0],        # 따옴표(작은)
    '"': [0,1,1,0,0,0],        # 큰따옴표(시작)
    '“': [0,1,1,0,0,0],        # 큰따옴표(시작)
    '”': [0,1,1,0,0,0],        # 큰따옴표(끝)
    '(': [0,1,1,1,1,0],        # 여는 괄호
    ')': [0,1,1,1,1,0],        # 닫는 괄호
    '/': [0,0,1,0,1,0],        # 슬래시
    '_': [0,0,1,0,1,1],        # 밑줄
    '@': [0,1,0,1,1,1],        # at 기호
    '#': [0,1,1,1,1,1],        # 샵(숫자표시)
    '*': [0,1,1,0,1,1],        # 별표
    '&': [1,1,1,0,1,1],        # 앰퍼샌드
    '%': [1,0,1,1,1,1],        # 퍼센트
    '=': [1,1,1,1,0,1],        # 등호
    '+': [1,1,1,1,1,0],        # 더하기
    '<': [0,1,1,1,0,0],        # 부등호(작음)
    '>': [0,1,1,0,1,1],        # 부등호(큼)
    '[': [0,1,1,1,0,1],        # 대괄호
    ']': [0,1,1,1,0,1],        # 대괄호
    '{': [1,1,1,0,0,1],        # 중괄호
    '}': [1,1,1,0,0,1],        # 중괄호
    '\\': [0,0,1,1,0,1],       # 역슬래시
    '^': [0,0,1,1,1,0],        # 캐럿
    '`': [0,0,1,1,1,1],        # backtick
    '~': [0,1,1,1,1,1],        # 틸드
    '$': [1,0,1,0,1,1],        # 달러
    '|': [0,0,1,1,0,0],        # vertical bar
    # ... 필요시 추가
}

# --- 역변환 테이블(점자 6비트 → 문자) ---
def tupleize(bits):
    """리스트/중첩리스트를 튜플/튜플의 튜플로 변환 (딕셔너리 키용)"""
    if isinstance(bits, list):
        if bits and isinstance(bits[0], list):
            return tuple(tuple(b) for b in bits)
        return tuple(bits)
    return bits

# 한글 초성, 중성, 종성 역변환
BRAILLE_TO_INITIAL = {tupleize(v): k for k, v in INITIAL_TO_BRAILLE.items()}
BRAILLE_TO_MEDIAL = {tupleize(v): k for k, v in MEDIAL_TO_BRAILLE.items()}
BRAILLE_TO_FINAL = {tupleize(v): k for k, v in FINAL_TO_BRAILLE.items()}

# 약자/약어 역변환
BRAILLE_TO_HANGUL_ABBREVIATION = {tupleize(v): k for k, v in HANGUL_BRAILLE_ABBREVIATION.items()}

# 영문자 역변환
BRAILLE_TO_ENGLISH = {tupleize(v): k for k, v in ENGLISH_TO_BRAILLE.items()}

# 특수문자 역변환
BRAILLE_TO_SPECIAL = {tupleize(v): k for k, v in SPECIAL_TO_BRAILLE.items()}

# Prefix 역변환(대문자, 숫자)
BRAILLE_TO_CAPITAL_PREFIX = tuple(CAPITAL_PREFIX)
BRAILLE_TO_NUMBER_PREFIX = tuple(NUMBER_PREFIX)

# --- 전체 점자 6비트 → 문자/기호 통합 역변환 ---
# (중복 방지, 약자/특수/영문/한글 모두 포함)
BRAILLE_6BIT_TO_CHAR = {}
for d in [BRAILLE_TO_HANGUL_ABBREVIATION, BRAILLE_TO_SPECIAL, BRAILLE_TO_ENGLISH, BRAILLE_TO_INITIAL, BRAILLE_TO_MEDIAL, BRAILLE_TO_FINAL]:
    for k, v in d.items():
        if k not in BRAILLE_6BIT_TO_CHAR:
            BRAILLE_6BIT_TO_CHAR[k] = v

# --- export 용 (for external use) ---
BRAILLE_TABLE_EXPORT = {
    'INITIAL_TO_BRAILLE': INITIAL_TO_BRAILLE,
    'MEDIAL_TO_BRAILLE': MEDIAL_TO_BRAILLE,
    'FINAL_TO_BRAILLE': FINAL_TO_BRAILLE,
    'HANGUL_BRAILLE_ABBREVIATION': HANGUL_BRAILLE_ABBREVIATION,
    'ENGLISH_TO_BRAILLE': ENGLISH_TO_BRAILLE,
    'SPECIAL_TO_BRAILLE': SPECIAL_TO_BRAILLE,
    'CAPITAL_PREFIX': CAPITAL_PREFIX,
    'NUMBER_PREFIX': NUMBER_PREFIX,
    'NUM_TO_BRAILLE_LETTER': NUM_TO_BRAILLE_LETTER,
    'BRAILLE_TO_INITIAL': BRAILLE_TO_INITIAL,
    'BRAILLE_TO_MEDIAL': BRAILLE_TO_MEDIAL,
    'BRAILLE_TO_FINAL': BRAILLE_TO_FINAL,
    'BRAILLE_TO_HANGUL_ABBREVIATION': BRAILLE_TO_HANGUL_ABBREVIATION,
    'BRAILLE_TO_ENGLISH': BRAILLE_TO_ENGLISH,
    'BRAILLE_TO_SPECIAL': BRAILLE_TO_SPECIAL,
    'BRAILLE_6BIT_TO_CHAR': BRAILLE_6BIT_TO_CHAR,
}

if __name__ == "__main__":
    print("초성-점자:", INITIAL_TO_BRAILLE)
    print("중성-점자:", MEDIAL_TO_BRAILLE)
    print("종성-점자:", FINAL_TO_BRAILLE)
    print("한글약자:", HANGUL_BRAILLE_ABBREVIATION)
    print("영문-점자:", ENGLISH_TO_BRAILLE)
    print("특수문자:", SPECIAL_TO_BRAILLE)
    print("역변환예시(점자->초성):", BRAILLE_TO_INITIAL)
    print("통합역변환:", BRAILLE_6BIT_TO_CHAR)