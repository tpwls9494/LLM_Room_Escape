import streamlit as st
import time
import random
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# OpenAI 클라이언트 초기화
client = None
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)

# GPT-4 방 테마 생성 요청# GPT-4 방 테마 생성 요청 - 최종 버전 (숫자 순서 단서 포함)
def get_room_theme(client):
    """GPT-4 모델을 사용하여 방 테마를 생성합니다."""
    # API 클라이언트 상태 확인
    if not client:
        print("클라이언트가 없어 더미 응답을 반환합니다.")
        return get_dummy_response()
    
    # API 키 유효성 확인
    try:
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("API 키 테스트 성공:", test_response.choices[0].message.content)
    except Exception as e:
        print(f"API 키 테스트 실패: {str(e)}")
        return get_dummy_response()
    
    # 더 상세한 프롬프트로 변경
    prompt = """방탈출 게임을 위한 방 테마를 JSON 형식으로 생성해주세요.

1. 두 개의 방(room1, room2)이 연결되어 있어야 합니다.
2. 각 방에는 특별한 퍼즐이 있어야 합니다(숫자 자물쇠, 열쇠 자물쇠, 그림 퍼즐 중 하나).
3. 각 방에는 4개의 중요한 아이템이 있습니다. 이 아이템들이 퍼즐을 풀기 위한 핵심 단서입니다.
4. 사용 가능한 테마: 고대 신전, 해적선, 비밀 연구소, 오래된 성, 버려진 병원 등 여러 흥미로운 테마를 선택하세요.
5. 모든 아이템은 자세한 단서를 포함해야 하며, 퍼즐 해결에 필요한 힌트를 명확하게 제공해야 합니다.

각 방의 포맷:
{
  "room1": {
    "name": "방 이름 (예: 고대 신전 입구, 선장의 선실 등)",
    "description": "방에 대한 자세한 설명. 분위기와 중요한 디테일을 포함.",
    "puzzle_type": "숫자 자물쇠" 또는 "열쇠 자물쇠" 또는 "그림 퍼즐",
    "solution": "숫자 자물쇠일 경우 4자리 숫자, 열쇠 자물쇠일 경우 golden_key, 그림 퍼즐일 경우 complete_image",
    "items": [
      {"name": "아이템1", "description": "자세한 설명", "clue": "명확한 단서"}
      ...나머지 3개 아이템...
    ]
  },
  "room2": {
    // 같은 구조
  }
}

숫자 자물쇠는 4개 숫자로 된 코드(예: 1234)를 필요로 합니다. 각 아이템은 각 숫자와 그 순서에 대한 명확한 힌트를 제공해야 합니다.
열쇠 자물쇠는 아이템 중 하나가 작은 열쇠(is_key: true)이고, 다른 아이템이 그 열쇠로 열 수 있는 상자(requires_key: true)로, 그 안에 황금 열쇠(gives_golden_key: true)가 있어야 합니다.
그림 퍼즐은 4개의 아이템이 모두 퍼즐 조각(is_puzzle_piece: true)이어야 합니다.

반드시 각 방마다 4개의 아이템만 생성해주세요. 더 많은 아이템은 시스템에서 자동으로 추가됩니다.

주의: 반드시 room1과 room2 둘 다 완전히 작성해주세요. 각 방은 모든 필수 필드(name, description, puzzle_type, solution, items)를 포함해야 합니다."""

    print("API 요청 시작...")
    try:
        # GPT-4 사용
        response = client.chat.completions.create(
            model="gpt-4",  # GPT-4 사용
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1500,
        )
        result = response.choices[0].message.content
        print("API 응답 길이:", len(result))
        print("API 응답 일부:", result[:100] + "...")
        
        try:
            theme_data = json.loads(result)
            print("JSON 파싱 성공")
            
            # 기본 구조 검증 및 수정
            room1_valid = "room1" in theme_data
            room2_valid = "room2" in theme_data
            
            if not room1_valid or not room2_valid:
                print("필수 방이 없습니다. 더미 응답으로 대체합니다.")
                return get_dummy_response()
            
            # 각 방의 필수 필드 및 데이터 품질 검증
            for room_key in ["room1", "room2"]:
                room = theme_data[room_key]
                
                # 필수 필드 검증
                required_fields = ["name", "description", "puzzle_type", "solution", "items"]
                missing_fields = [field for field in required_fields if field not in room]
                
                if missing_fields:
                    print(f"{room_key}에 {', '.join(missing_fields)} 필드가 없습니다.")
                    
                    # 누락된 필드 자동 추가
                    for field in missing_fields:
                        if field == "name":
                            room["name"] = f"방 {1 if room_key == 'room1' else 2}"
                        elif field == "description":
                            room["description"] = "이 방에서 단서를 찾아 퍼즐을 풀어야 합니다."
                        elif field == "puzzle_type":
                            room["puzzle_type"] = "숫자 자물쇠"
                        elif field == "solution":
                            room["solution"] = str(random.randint(1000, 9999))
                        elif field == "items":
                            # 기본 아이템 4개 생성
                            room["items"] = [
                                {"name": "책상", "description": "오래된 책상입니다.", "clue": f"책상 위에 '{room['solution'][0]}' 숫자가 적혀 있습니다."},
                                {"name": "의자", "description": "낡은 의자입니다.", "clue": f"의자 밑에 '{room['solution'][1]}' 숫자가 새겨져 있습니다."},
                                {"name": "책장", "description": "먼지 쌓인 책장입니다.", "clue": f"책장 한쪽에 '{room['solution'][2]}' 숫자가 보입니다."},
                                {"name": "창문", "description": "흐릿한 창문입니다.", "clue": f"창문에 성에로 '{room['solution'][3]}' 숫자가 그려져 있습니다."}
                            ]
                
                # 방 정보 검증
                if len(room["name"]) < 3:
                    print(f"{room_key}의 이름이 너무 짧습니다. 보완합니다.")
                    room["name"] = f"{room['name']} {1 if room_key == 'room1' else 2}번 방"
                
                if len(room["description"]) < 20:
                    print(f"{room_key}의 설명이 너무 짧습니다. 보완합니다.")
                    room["description"] += " 이 방에서는 주변을 잘 살펴 단서를 찾아 퍼즐을 풀어야 합니다."
                
                # 퍼즐 유형 검증 및 수정
                valid_puzzle_types = ["숫자 자물쇠", "열쇠 자물쇠", "그림 퍼즐"]
                if room["puzzle_type"] not in valid_puzzle_types:
                    print(f"{room_key}의 퍼즐 유형이 올바르지 않습니다. 숫자 자물쇠로 변경합니다.")
                    room["puzzle_type"] = "숫자 자물쇠"
                    room["solution"] = str(random.randint(1000, 9999))
                
                # 아이템 수 검증 및 수정
                if "items" not in room or not isinstance(room["items"], list):
                    print(f"{room_key}의 아이템 목록이 없거나 올바르지 않습니다. 기본 아이템을 생성합니다.")
                    room["items"] = []
                
                # 아이템이 4개 미만이면 추가
                if len(room["items"]) < 4:
                    print(f"{room_key}의 아이템이 부족합니다. 추가 아이템을 생성합니다.")
                    solution = room["solution"]
                    missing_count = 4 - len(room["items"])
                    
                    default_items = [
                        {"name": "책상", "description": "오래된 책상입니다.", "clue": f"책상 위에 '{solution[0]}' 숫자가 적혀 있습니다."},
                        {"name": "의자", "description": "낡은 의자입니다.", "clue": f"의자 밑에 '{solution[1]}' 숫자가 새겨져 있습니다."},
                        {"name": "책장", "description": "먼지 쌓인 책장입니다.", "clue": f"책장 한쪽에 '{solution[2]}' 숫자가 보입니다."},
                        {"name": "창문", "description": "흐릿한 창문입니다.", "clue": f"창문에 성에로 '{solution[3]}' 숫자가 그려져 있습니다."}
                    ]
                    
                    # 필요한 만큼만 추가
                    for i in range(missing_count):
                        room["items"].append(default_items[i])
                
                # 아이템 상세 정보 검증 및 수정
                for i, item in enumerate(room["items"]):
                    # 필수 필드 확인
                    for field in ["name", "description", "clue"]:
                        if field not in item or not item[field]:
                            print(f"{room_key}의 아이템 {i+1}에 {field}가 없습니다. 추가합니다.")
                            if field == "name":
                                item["name"] = f"아이템 {i+1}"
                            elif field == "description":
                                item["description"] = "자세한 설명이 없는 물건입니다."
                            elif field == "clue":
                                # 퍼즐 유형에 따라 적절한 단서 생성
                                if room["puzzle_type"] == "숫자 자물쇠":
                                    # 숫자와 함께 순서 정보도 제공
                                    positions = ["첫 번째", "두 번째", "세 번째", "네 번째"]
                                    item["clue"] = f"이 물건에서 '{room['solution'][i]}'이라는 숫자를 발견했습니다. 이는 비밀번호의 {positions[i]} 숫자로 보입니다."
                                elif room["puzzle_type"] == "열쇠 자물쇠":
                                    if i == 0:
                                        item["clue"] = "이 물건 안에 작은 열쇠가 숨겨져 있습니다."
                                        item["is_key"] = True
                                    elif i == 1:
                                        item["clue"] = "이 물건은 열쇠로 열어야 합니다. 안에 황금 열쇠가 있을 것 같습니다."
                                        item["requires_key"] = True
                                        item["gives_golden_key"] = True
                                    else:
                                        item["clue"] = "이 물건에서 퍼즐에 관한 단서를 찾았습니다."
                                elif room["puzzle_type"] == "그림 퍼즐":
                                    item["clue"] = f"이 물건에서 퍼즐 조각 {i+1}을 발견했습니다!"
                                    item["is_puzzle_piece"] = True
                    
                    # 숫자 자물쇠의 경우 순서 정보가 포함되어 있는지 확인하고 보완
                    if room["puzzle_type"] == "숫자 자물쇠":
                        positions = ["첫 번째", "두 번째", "세 번째", "네 번째"]
                        digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                        
                        # 단서에 숫자가 있는지 확인
                        has_digit = any(digit in item["clue"] for digit in digits)
                        # 단서에 순서 정보가 있는지 확인
                        has_position = any(position in item["clue"] for position in positions)
                        
                        # 숫자는 있지만 순서 정보가 없는 경우
                        if has_digit and not has_position:
                            # 적절한 숫자 찾기
                            current_digit = None
                            for digit in digits:
                                if digit in item["clue"]:
                                    current_digit = digit
                                    break
                            
                            # 이 아이템이 몇 번째 숫자를 나타내는지 확인
                            target_index = i
                            # 솔루션에서 같은 숫자가 여러 개 있을 경우 해당 위치 확인
                            if current_digit in room["solution"]:
                                for idx, sol_digit in enumerate(room["solution"]):
                                    if sol_digit == current_digit:
                                        target_index = idx
                                        break
                            
                            # 순서 정보 추가
                            item["clue"] += f" 이는 비밀번호의 {positions[target_index]} 숫자입니다."
                        
                        # 숫자가 없는 경우 (상당히 잘못된 단서)
                        elif not has_digit:
                            item["clue"] = f"이 물건에서 '{room['solution'][i]}'이라는 숫자를 발견했습니다. 이는 비밀번호의 {positions[i]} 숫자입니다."
                
                # 퍼즐 유형 및 솔루션 최종 검증
                if room["puzzle_type"] == "숫자 자물쇠":
                    # 숫자 형식 검증
                    if not (isinstance(room["solution"], str) and room["solution"].isdigit() and len(room["solution"]) == 4):
                        print(f"{room_key}의 숫자 자물쇠 솔루션이 올바르지 않습니다. 임의의 4자리 숫자로 수정합니다.")
                        room["solution"] = str(random.randint(1000, 9999))
                elif room["puzzle_type"] == "열쇠 자물쇠":
                    if room["solution"] != "golden_key":
                        print(f"{room_key}의 열쇠 자물쇠 솔루션이 올바르지 않습니다. 'golden_key'로 수정합니다.")
                        room["solution"] = "golden_key"
                    
                    # 열쇠 아이템 검증
                    has_key = False
                    has_box = False
                    has_golden_key = False
                    
                    for item in room["items"]:
                        if item.get("is_key"):
                            has_key = True
                        if item.get("requires_key"):
                            has_box = True
                        if item.get("gives_golden_key"):
                            has_golden_key = True
                    
                    # 필요한 속성 추가
                    if not has_key:
                        print(f"{room_key}에 열쇠 아이템이 없습니다. 첫 번째 아이템에 추가합니다.")
                        room["items"][0]["is_key"] = True
                        room["items"][0]["clue"] = "이 물건에서 작은 열쇠를 발견했습니다!"
                    
                    if not has_box:
                        print(f"{room_key}에 열쇠로 여는 상자가 없습니다. 두 번째 아이템에 추가합니다.")
                        room["items"][1]["requires_key"] = True
                        room["items"][1]["clue"] = "이 물건은 열쇠로 열어야 합니다."
                    
                    if not has_golden_key:
                        print(f"{room_key}에 황금 열쇠를 주는 아이템이 없습니다. 열쇠로 여는 상자에 추가합니다.")
                        for item in room["items"]:
                            if item.get("requires_key"):
                                item["gives_golden_key"] = True
                                item["clue"] += " 안에 황금 열쇠가 있습니다!"
                                break
                
                elif room["puzzle_type"] == "그림 퍼즐":
                    if room["solution"] != "complete_image":
                        print(f"{room_key}의 그림 퍼즐 솔루션이 올바르지 않습니다. 'complete_image'로 수정합니다.")
                        room["solution"] = "complete_image"
                    
                    # 퍼즐 조각 검증
                    puzzle_pieces = 0
                    for item in room["items"]:
                        if item.get("is_puzzle_piece"):
                            puzzle_pieces += 1
                    
                    if puzzle_pieces < 4:
                        print(f"{room_key}의 퍼즐 조각이 부족합니다. 추가합니다.")
                        for i in range(4):
                            if i < len(room["items"]):
                                room["items"][i]["is_puzzle_piece"] = True
                                if "이 물건에서 퍼즐 조각" not in room["items"][i]["clue"]:
                                    room["items"][i]["clue"] = f"이 물건에서 퍼즐 조각 {i+1}을 발견했습니다!"
                
                # 숫자 자물쇠인 경우 단서를 최종 검토하여 모든 숫자와 순서 정보가 제공되었는지 확인
                if room["puzzle_type"] == "숫자 자물쇠":
                    digits_covered = [False, False, False, False]  # 4자리 각 숫자에 대한 단서 존재 여부
                    
                    for i, item in enumerate(room["items"][:4]):
                        # 각 숫자가 단서에 포함되어 있는지 확인
                        for j, digit in enumerate(room["solution"]):
                            if digit in item["clue"] and f"비밀번호의 {['첫 번째', '두 번째', '세 번째', '네 번째'][j]}" in item["clue"]:
                                digits_covered[j] = True
                    
                    # 누락된 숫자 단서가 있는지 확인하고 보완
                    for j, covered in enumerate(digits_covered):
                        if not covered:
                            print(f"{room_key}의 {j+1}번째 숫자에 대한 단서가 명확하지 않습니다. 보완합니다.")
                            
                            # 어떤 아이템을 수정할지 선택 (가능하면 기존 숫자와 관련 있는 아이템)
                            target_item = j % 4  # 기본 아이템 인덱스
                            
                            # 해당 아이템 단서 수정
                            room["items"][target_item]["clue"] = f"{room['items'][target_item]['name']}을(를) 자세히 살펴보니 '{room['solution'][j]}'라는 숫자가 있습니다. 이는 분명히 비밀번호의 {['첫 번째', '두 번째', '세 번째', '네 번째'][j]} 숫자입니다."
                
                # 아이템 수를 4개로 제한
                room["items"] = room["items"][:4]
            
            # 일반 물건 추가
            common_items = get_common_items()
            
            for room_key in theme_data:
                important_items = theme_data[room_key]["items"]
                random_items = random.sample(common_items, 26)
                theme_data[room_key]["items"] = important_items + random_items
            
            print("테마 데이터 준비 완료")
            return theme_data
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {str(e)}")
            print("원본 응답:", result)
            
            # 미리 정의된 테마 중 하나를 임의로 선택
            predefined_themes = get_predefined_themes()
            return random.choice(predefined_themes)
            
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        
        # 미리 정의된 테마 중 하나를 임의로 선택
        predefined_themes = get_predefined_themes()
        return random.choice(predefined_themes)

# 일반 물건 목록 함수
def get_common_items():
    """일반 물건 목록을 반환합니다."""
    return [
        {"name": "먼지 묻은 화분", "description": "시든 식물이 들어있는 화분입니다.", "clue": "흙 속에 작은 쪽지가 있지만 중요해 보이지는 않습니다."},
        {"name": "깨진 유리컵", "description": "누군가 깨뜨린 유리컵입니다.", "clue": "위험해 보이니 조심해서 다루세요."},
        {"name": "녹슨 열쇠", "description": "오래된 열쇠입니다. 많이 녹슬어 있습니다.", "clue": "이 열쇠로 열 수 있는 자물쇠는 이미 망가진 것 같습니다."},
        {"name": "연필과 메모지", "description": "누군가 남긴 필기구입니다.", "clue": "메모지에는 낙서만 있습니다."},
        {"name": "더러운 양말", "description": "누군가 벗어둔 양말입니다.", "clue": "역겨운 냄새가 납니다."},
        {"name": "빈 물병", "description": "누군가 마시다 버린 물병입니다.", "clue": "특별한 것은 없지만 갈증을 느낍니다."},
        {"name": "고장난 시계", "description": "배터리가 다 된 벽시계입니다.", "clue": "시간이 멈춘지 오래된 것 같습니다."},
        {"name": "작은 거울", "description": "벽에 걸린 작은 거울입니다.", "clue": "당신의 지친 얼굴이 비춰집니다."},
        {"name": "찢어진 종이", "description": "반으로 찢어진 종이 조각입니다.", "clue": "내용을 알아볼 수 없습니다."},
        {"name": "깨진 안경", "description": "한쪽 렌즈가 깨진 안경입니다.", "clue": "누군가는 이것이 없으면 잘 보지 못할텐데..."},
        {"name": "머리카락 묶음", "description": "바닥에 떨어진 머리카락 뭉치입니다.", "clue": "누군가 이곳에 있었던 증거입니다."},
        {"name": "카드 한 장", "description": "바닥에 떨어진 트럼프 카드입니다.", "clue": "스페이드 7이지만 특별한 의미는 없어 보입니다."},
        {"name": "곰팡이 핀 빵", "description": "오래된 빵 조각입니다.", "clue": "먹을 수 없을 정도로 곰팡이가 피었습니다."},
        {"name": "낡은 신발", "description": "누군가 벗어둔 신발입니다.", "clue": "가죽이 낡아 거의 다 헤진 상태입니다."},
        {"name": "빈 캔", "description": "내용물을 다 마신 캔입니다.", "clue": "라벨이 벗겨져 무슨 음료였는지 알 수 없습니다."},
        {"name": "찌그러진 모자", "description": "누군가가 쓰던 모자입니다.", "clue": "심하게 찌그러져 있습니다."},
        {"name": "접힌 포스터", "description": "말려있는 포스터입니다.", "clue": "오래되어 거의 바스러집니다."},
        {"name": "플라스틱 인형", "description": "작은 플라스틱 인형입니다.", "clue": "특별한 의미는 없어 보입니다."},
        {"name": "구겨진 영수증", "description": "바닥에 떨어진 영수증입니다.", "clue": "글씨가 바래서 잘 보이지 않습니다."},
        {"name": "마스크", "description": "사용한 마스크입니다.", "clue": "위생상 만지지 않는 것이 좋을 것 같습니다."},
        {"name": "종이 클립", "description": "구부러진 종이 클립입니다.", "clue": "무언가를 따는 데 쓸 수는 있겠지만 여기서는 소용없어 보입니다."},
        {"name": "전선 조각", "description": "잘린 전선 조각입니다.", "clue": "위험해 보이니 만지지 않는 것이 좋겠습니다."},
        {"name": "빈 약병", "description": "약이 다 떨어진 약병입니다.", "clue": "라벨에는 '진정제'라고 적혀있습니다."},
        {"name": "담배 꽁초", "description": "바닥에 버려진 담배 꽁초입니다.", "clue": "최근에 누군가 이곳에 있었다는 증거입니다."},
        {"name": "누군가의 사진", "description": "찢어진 사진 조각입니다.", "clue": "알 수 없는 남자의 얼굴이 보입니다."},
        {"name": "미끄러운 비누", "description": "사용한 흔적이 있는 비누입니다.", "clue": "미끄러워서 잡기 어렵습니다."}
    ]

# 미리 준비된 테마 목록
def get_predefined_themes():
    """미리 준비된 방 테마 목록을 반환합니다."""
    
    # 일반 물건은 재사용
    common_items = get_common_items()
    
    themes = [
        # 테마 1: 오래된 연구실
        {
            "room1": {
                "name": "오래된 연구실",
                "description": "먼지가 쌓인 오래된 연구실에 들어왔습니다. 어딘가 불안한 기운이 감돕니다. 실험 장비와 책들이 어지럽게 널려있습니다.",
                "puzzle_type": "숫자 자물쇠",
                "solution": "5821",
                "items": [
                    {"name": "먼지 쌓인 책장", "description": "수십 권의 책이 꽂혀있지만 한 책이 특별히 눈에 띕니다.", "clue": "책 표지에 '5'라는 숫자가 적혀있습니다. 이는 비밀번호의 첫 번째 숫자입니다."},
                    {"name": "실험 노트", "description": "누군가의 실험 기록이 적혀있습니다.", "clue": "페이지 하단에 '8'이라는 숫자가 있습니다. 이는 비밀번호의 두 번째 숫자로 보입니다."},
                    {"name": "깨진 시계", "description": "작동이 멈춘 벽시계입니다.", "clue": "시계 바늘이 '2'시를 가리키고 있습니다. 이는 비밀번호의 세 번째 숫자입니다."},
                    {"name": "화학 실험 세트", "description": "다양한 화학 용액들이 있습니다.", "clue": "용액 라벨에 '1'이라는 숫자가 보입니다. 이는 비밀번호의 네 번째 숫자입니다."}
                ]
            },
            "room2": {
                "name": "비밀 보관실",
                "description": "연구실 뒤편에 숨겨진 비밀 보관실을 발견했습니다. 이곳에는 중요한 자료들이 보관되어 있는 것 같습니다.",
                "puzzle_type": "그림 퍼즐",
                "solution": "complete_image",
                "items": [
                    {"name": "찢어진 설계도 조각1", "description": "커다란 설계도의 한 조각입니다.", "clue": "이미지 조각1", "is_puzzle_piece": True},
                    {"name": "금고 뒤편", "description": "무거운 금고 뒤편에 무언가 있습니다.", "clue": "설계도의 오른쪽 상단 조각을 발견했습니다!", "is_puzzle_piece": True},
                    {"name": "책상 서랍", "description": "잠겨있지 않은 서랍입니다.", "clue": "설계도의 왼쪽 하단 조각이 발견되었습니다!", "is_puzzle_piece": True},
                    {"name": "액자 뒤", "description": "벽에 걸린 액자 뒤에 숨겨진 공간이 있습니다.", "clue": "설계도의 오른쪽 하단 조각이 발견되었습니다!", "is_puzzle_piece": True}
                ]
            }
        },
        
        # 테마 2: 해적선
        {
            "room1": {
                "name": "해적선 선실",
                "description": "당신은 해저 깊은 곳에 침몰한 해적선 안에 갇히게 되었습니다. 선실은 물이 새어 들어와 바닥이 축축합니다.",
                "puzzle_type": "열쇠 자물쇠",
                "solution": "golden_key",
                "items": [
                    {"name": "선장의 책상", "description": "오래된 목재 책상입니다. 바닷물에 불어 있지만 서랍은 멀쩡합니다.", "clue": "서랍에 작은 상자가 있지만 열쇠가 필요합니다."},
                    {"name": "웃고 있는 해골", "description": "선실 한쪽에 놓인 해골입니다. 해적 선장의 것으로 보입니다.", "clue": "해골 이빨 사이에 작은 열쇠가 끼워져 있습니다.", "is_key": True},
                    {"name": "작은 상자", "description": "선장의 책상에서 찾은 상자입니다.", "clue": "상자 안에 황금 열쇠가 있습니다!", "requires_key": True, "gives_golden_key": True},
                    {"name": "찢어진 지도", "description": "선실 바닥에 떨어진 지도입니다.", "clue": "보물이 묻힌 위치를 표시한 것 같지만, 지금은 탈출이 우선입니다."}
                ]
            },
            "room2": {
                "name": "보물 저장고",
                "description": "선실을 통과하자 보물 저장고로 보이는 공간이 나타났습니다. 황금과 보석이 가득하지만, 아직 탈출구를 찾아야 합니다.",
                "puzzle_type": "숫자 자물쇠",
                "solution": "3746",
                "items": [
                    {"name": "금화 더미", "description": "반짝이는 금화가 쌓여있습니다.", "clue": "금화 중 하나에 '3'이라는 숫자가 새겨져 있습니다. 이는 비밀번호의 첫 번째 숫자입니다."},
                    {"name": "보석함", "description": "화려한 보석들이 담긴 상자입니다.", "clue": "보석함 바닥에 '7'이라는 숫자가 보입니다. 이는 비밀번호의 두 번째 숫자입니다."},
                    {"name": "깨진 나침반", "description": "선원들이 사용했을 나침반입니다.", "clue": "나침반 뒷면에 '4'라는 숫자가 적혀있습니다. 이는 비밀번호의 세 번째 숫자입니다."},
                    {"name": "선장의 일기장", "description": "해적 선장의 일기입니다.", "clue": "마지막 페이지에 '6'이라는 숫자가 적혀있습니다. 이는 비밀번호의 네 번째 숫자입니다."}
                ]
            }
        },
        
        # 테마 3: 고대 신전
        {
            "room1": {
                "name": "고대 신전 입구",
                "description": "거대한 고대 신전의 입구에 들어왔습니다. 벽에는 알 수 없는 상형문자와 조각상들이 있습니다.",
                "puzzle_type": "숫자 자물쇠",
                "solution": "1492",
                "items": [
                    {"name": "떨어진 돌판", "description": "바닥에 떨어진 돌판입니다.", "clue": "돌판에 숫자 '1'이 새겨져 있습니다. 이는 비밀번호의 첫 번째 숫자입니다."},
                    {"name": "태양신 석상", "description": "중앙에 있는 태양신 석상입니다.", "clue": "받침대에 '4'라는 숫자가 희미하게 보입니다. 이는 비밀번호의 두 번째 숫자입니다."},
                    {"name": "제단", "description": "제물을 바치는 제단입니다.", "clue": "제단 측면에 '9'라는 숫자가 조각되어 있습니다. 이는 비밀번호의 세 번째 숫자입니다."},
                    {"name": "벽화", "description": "신전 벽에 그려진 고대 벽화입니다.", "clue": "벽화 하단에 '2'라는 숫자가 그려져 있습니다. 이는 비밀번호의 네 번째 숫자입니다."}
                ]
            },
            "room2": {
                "name": "보물 방",
                "description": "신전 안쪽의 보물 방입니다. 금과 보석이 가득하지만, 출구가 잠겨 있습니다.",
                "puzzle_type": "열쇠 자물쇠",
                "solution": "golden_key",
                "items": [
                    {"name": "황금 왕관", "description": "화려한 황금 왕관입니다.", "clue": "왕관 내부에 작은 열쇠 모양의 홈이 있습니다."},
                    {"name": "뱀 석상", "description": "방 한편에 있는 뱀 모양 석상입니다.", "clue": "뱀의 입에서 작은 열쇠가 나왔습니다.", "is_key": True},
                    {"name": "보석 상자", "description": "보석이 가득한 금속 상자입니다.", "clue": "상자 안에 황금 열쇠가 있습니다!", "requires_key": True, "gives_golden_key": True},
                    {"name": "고대 지도", "description": "신전의 지도로 보이는 양피지입니다.", "clue": "탈출구가 표시되어 있지만, 열쇠가 필요합니다."}
                ]
            }
        },
        
        # 테마 4: 버려진 병원
        {
            "room1": {
                "name": "응급실",
                "description": "버려진 병원의 응급실입니다. 침대와 의료 장비들이 어지럽게 널려있고 불길한 기운이 감돕니다.",
                "puzzle_type": "그림 퍼즐",
                "solution": "complete_image",
                "items": [
                    {"name": "환자 차트", "description": "바닥에 떨어진 환자 차트입니다.", "clue": "차트 뒷면에 X선 사진의 일부가 붙어있습니다.", "is_puzzle_piece": True},
                    {"name": "의사 가운", "description": "걸려있는 의사 가운입니다.", "clue": "주머니에서 X선 사진의 일부를 발견했습니다!", "is_puzzle_piece": True},
                    {"name": "약품 캐비닛", "description": "의약품이 보관된 캐비닛입니다.", "clue": "캐비닛 안쪽에 X선 사진의 일부가 숨겨져 있습니다!", "is_puzzle_piece": True},
                    {"name": "깨진 모니터", "description": "깨진 컴퓨터 모니터입니다.", "clue": "모니터 틈 사이에 X선 사진의 마지막 조각이 있습니다!", "is_puzzle_piece": True}
                ]
            },
            "room2": {
                "name": "수술실",
                "description": "병원의 수술실입니다. 수술대와 의료 도구들이 있으며, 어딘가 불안한 기운이 감돕니다.",
                "puzzle_type": "숫자 자물쇠",
                "solution": "6284",
                "items": [
                    {"name": "수술 도구", "description": "일련의 수술 도구들입니다.", "clue": "도구 케이스에 '6'이라는 숫자가 적혀 있습니다. 이는 비밀번호의 첫 번째 숫자입니다."},
                    {"name": "환자 기록", "description": "환자의 의료 기록입니다.", "clue": "기록에 '2'라는 숫자가 적혀 있습니다. 이는 비밀번호의 두 번째 숫자입니다."},
                    {"name": "의사 메모", "description": "의사가 남긴 메모입니다.", "clue": "메모에 '8'이라는 숫자가 적혀 있습니다. 이는 비밀번호의 세 번째 숫자입니다."},
                    {"name": "마취제 병", "description": "텅 빈 마취제 병입니다.", "clue": "병 바닥에 '4'라는 숫자가 적혀 있습니다. 이는 비밀번호의 네 번째 숫자입니다."}
                ]
            }
        },
        
        # 테마 5: 비밀 연구소
        {
            "room1": {
                "name": "보안 구역",
                "description": "비밀 연구소의 보안 구역입니다. 첨단 장비와 모니터가 있지만 전원이 꺼져 있습니다.",
                "puzzle_type": "숫자 자물쇠",
                "solution": "2580",
                "items": [
                    {"name": "보안 카드", "description": "직원 보안 카드입니다.", "clue": "카드 뒷면에 '2'라는 숫자가 적혀 있습니다. 이는 비밀번호의 첫 번째 숫자입니다."},
                    {"name": "키패드", "description": "문 옆의 보안 키패드입니다.", "clue": "자주 사용된 버튼은 '5'로 보입니다. 이는 비밀번호의 두 번째 숫자입니다."},
                    {"name": "메모지", "description": "책상에 붙어있는 메모지입니다.", "clue": "메모에 '8'이라고 적혀 있습니다. 이는 비밀번호의 세 번째 숫자입니다."},
                    {"name": "휴대폰", "description": "버려진 휴대폰입니다.", "clue": "화면에 '0'이라는 숫자가 보입니다. 이는 비밀번호의 네 번째 숫자입니다."}
                ]
            },
            "room2": {
                "name": "실험실",
                "description": "최첨단 실험 장비가 가득한 실험실입니다. 무언가 위험한 실험이 진행되었던 것 같습니다.",
                "puzzle_type": "열쇠 자물쇠",
                "solution": "golden_key",
                "items": [
                    {"name": "현미경", "description": "고급 전자 현미경입니다.", "clue": "접안렌즈 아래에 작은 열쇠가 있습니다.", "is_key": True},
                    {"name": "샘플 보관함", "description": "냉동 샘플이 보관된 캐비닛입니다.", "clue": "보관함은 잠겨 있고 열쇠가 필요합니다."},
                    {"name": "금속 상자", "description": "실험실 한쪽에 있는 금속 상자입니다.", "clue": "상자 안에 황금 열쇠가 있습니다!", "requires_key": True, "gives_golden_key": True},
                    {"name": "연구 노트", "description": "연구원의 노트입니다.", "clue": "마지막 페이지에 '탈출구는 B섹터에 있음'이라고 적혀 있습니다."}
                ]
            }
        }
    ]
    
    # 각 방 테마에 일반 물건 추가
    for theme in themes:
        for room_key in theme:
            # 중요 아이템 4개 유지
            important_items = theme[room_key]["items"][:4]
            
            # 일반 물건 추가 (랜덤으로 선택)
            random_items = random.sample(common_items, 26)
            
            # 최종 아이템 목록 구성
            theme[room_key]["items"] = important_items + random_items
    
    return themes

# 더미 응답 생성 함수 수정
def get_dummy_response():
    """API 연결 없을 때 사용할 더미 데이터를 반환합니다."""
    # 미리 정의된 테마 중 하나를 임의로 선택
    predefined_themes = get_predefined_themes()
    return random.choice(predefined_themes)

# 세션 상태 초기화
def init_session_state():
    """게임 관련 세션 상태를 초기화합니다."""
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'current_room' not in st.session_state:
        st.session_state.current_room = 1
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'end_time' not in st.session_state:
        st.session_state.end_time = None
    if 'rooms_data' not in st.session_state:
        st.session_state.rooms_data = None
    if 'inventory' not in st.session_state:
        st.session_state.inventory = []
    if 'has_key' not in st.session_state:
        st.session_state.has_key = False
    if 'has_golden_key' not in st.session_state:
        st.session_state.has_golden_key = False
    if 'puzzle_pieces' not in st.session_state:
        st.session_state.puzzle_pieces = []
    if 'visited_items' not in st.session_state:
        st.session_state.visited_items = []
    if 'last_response' not in st.session_state:
        st.session_state.last_response = ""

# 게임 시작 함수

def start_game():
    """게임을 시작하고 방 테마를 생성합니다."""
    st.session_state.game_started = True
    st.session_state.current_room = 1
    st.session_state.start_time = time.time()
    st.session_state.inventory = []
    st.session_state.inventory_details = {}
    st.session_state.has_key = False
    st.session_state.has_golden_key = False
    st.session_state.puzzle_pieces = []
    st.session_state.visited_items = []
    
    # 디버깅을 위한 로그 추가
    print("게임 시작 - API 클라이언트 상태:", "있음" if client else "없음")
    if client:
        try:
            # API 키 유효성 테스트
            api_key = os.environ.get("OPENAI_API_KEY", "")
            print(f"API 키 길이: {len(api_key)}")
            print(f"API 키 프리픽스: {api_key[:4]}...")
        except Exception as e:
            print(f"API 키 확인 중 오류: {str(e)}")
    
    # 방 테마 생성
    st.session_state.rooms_data = get_room_theme(client)
    print("생성된 방 테마 유형:", "더미" if "room1" in st.session_state.rooms_data else "GPT 생성")
    
    # 아이템 위치 설정
    st.session_state.item_positions = {}
    positions = list(range(30))
    random.shuffle(positions)
    st.session_state.item_positions["room1"] = positions
    positions = list(range(30))
    random.shuffle(positions)
    st.session_state.item_positions["room2"] = positions

# 물건 들여다보기 함수
def examine_item(item_index):
    """물건을 들여다보고 결과를 반환합니다."""
    current_room_key = f"room{st.session_state.current_room}"
    room_data = st.session_state.rooms_data[current_room_key]
    item = room_data["items"][item_index]

    if item["name"] not in st.session_state.visited_items:
        st.session_state.visited_items.append(item["name"])

    response = f"{item['name']}을(를) 들여다 보셨습니다.\n\n{item['description']}"

    if "clue" in item and item["clue"]:
        response += f"\n\n{item['clue']}"
    
    # 강제 획득 아이템들은 바로 인벤토리에 추가
    auto_add = False
    
    # 열쇠 획득
    if "is_key" in item and item["is_key"] and not st.session_state.has_key:
        st.session_state.has_key = True
        response += "\n\n**열쇠를 획득하셨습니다!**"
        auto_add = True

    # 열쇠가 필요한 아이템
    if "requires_key" in item and item["requires_key"]:
        if st.session_state.has_key:
            response += "\n\n열쇠로 열었습니다!"
            if "gives_golden_key" in item and item["gives_golden_key"]:
                st.session_state.has_golden_key = True
                response += "\n\n**황금 열쇠를 획득하셨습니다!**"
                if "황금 열쇠" not in st.session_state.inventory:
                    st.session_state.inventory.append("황금 열쇠")
                    st.session_state.inventory_details["황금 열쇠"] = {
                        "description": "빛나는 황금 열쇠입니다. 중요한 문을 열 수 있을 것 같습니다.",
                        "clue": "황금 열쇠로 다음 방으로 이동할 수 있습니다."
                    }
        else:
            response += "\n\n이 아이템을 열려면 열쇠가 필요합니다."

    # 퍼즐 조각 획득
    if "is_puzzle_piece" in item and item["is_puzzle_piece"]:
        if item["name"] not in st.session_state.puzzle_pieces:
            st.session_state.puzzle_pieces.append(item["name"])
            response += f"\n\n**퍼즐 조각을 획득하셨습니다! ({len(st.session_state.puzzle_pieces)}/4)**"
            auto_add = True

    # 일반 아이템 - 인벤토리 추가 여부 확인 (중요 아이템은 자동 추가)
    if item["name"] not in st.session_state.inventory:
        if auto_add:
            st.session_state.inventory.append(item["name"])
            st.session_state.inventory_details[item["name"]] = {
                "description": item["description"],
                "clue": item.get("clue", "")
            }
            return response
        
        # 퍼즐 관련 중요 단서가 있는 경우에만 인벤토리 추가 여부 확인
        if "clue" in item and item["clue"]:
            response += "\n\n이 아이템을 인벤토리에 추가하시겠습니까?"
            return response
    
    return response

# 인벤토리에 아이템 추가 함수
def add_to_inventory(item_name, item_data):
    """아이템을 인벤토리에 추가합니다."""
    if item_name not in st.session_state.inventory:
        st.session_state.inventory.append(item_name)
        st.session_state.inventory_details[item_name] = {
            "description": item_data["description"],
            "clue": item_data.get("clue", "")
        }

# 퍼즐 풀기 시도 함수
def try_solve_puzzle(answer=""):
    """퍼즐 해결을 시도하고 결과를 반환합니다."""
    current_room_key = f"room{st.session_state.current_room}"
    room_data = st.session_state.rooms_data[current_room_key]
    puzzle_type = room_data["puzzle_type"]
    solution = room_data["solution"]

    if puzzle_type == "숫자 자물쇠":
        if answer == solution:
            move_to_next_room()
            return True, "정답입니다! 문이 열렸습니다."
        else:
            return False, "틀렸습니다. 다시 시도해보세요."

    elif puzzle_type == "열쇠 자물쇠":
        if st.session_state.has_golden_key:
            move_to_next_room()
            return True, "황금 열쇠로 문을 열었습니다!"
        else:
            return False, "문을 열려면 황금 열쇠가 필요합니다."

    elif puzzle_type == "그림 퍼즐":
        if len(st.session_state.puzzle_pieces) == 4:
            move_to_next_room()
            return True, "그림 퍼즐을 완성했습니다! 문이 열렸습니다."
        else:
            return False, f"아직 모든 퍼즐 조각을 찾지 못했습니다. ({len(st.session_state.puzzle_pieces)}/4)"

    return False, "알 수 없는 퍼즐 유형입니다."

# 다음 방으로 이동 함수
def move_to_next_room():
    """다음 방으로 이동하고 상태를 업데이트합니다."""
    st.session_state.current_room += 1
    st.session_state.has_key = False
    st.session_state.visited_items = []

    # 게임 종료 확인
    if st.session_state.current_room > 2:
        st.session_state.end_time = time.time()
        st.session_state.elapsed_time = st.session_state.end_time - st.session_state.start_time

# 아이템 이모티콘 매핑
def get_item_emoji(item_name):
    """아이템 이름에 적절한 이모티콘을 반환합니다."""
    emoji_map = {
        # 일반적인 물건들
        "책장": "📚", "책": "📖", "노트": "📝", "시계": "🕰️", "실험 세트": "🧪",
        "설계도": "📐", "금고": "🔒", "서랍": "🗄️", "액자": "🖼️", "책상": "🪑",
        "해골": "💀", "상자": "📦", "지도": "🗺️", "금화": "💰", "보석": "💎",
        "나침반": "🧭", "일기장": "📔", "열쇠": "🔑", "황금 열쇠": "🔑",
        
        # 일반 물건들
        "화분": "🪴", "유리컵": "🥛", "연필": "✏️", "메모지": "📜", "양말": "🧦",
        "물병": "🧴", "거울": "🪞", "종이": "📄", "안경": "👓", "머리카락": "💇‍♀️",
        "카드": "🃏", "빵": "🍞", "신발": "👞", "캔": "🥫", "모자": "🧢",
        "포스터": "📃", "인형": "🧸", "영수증": "🧾", "마스크": "😷", "클립": "📎",
        "전선": "🔌", "약병": "💊", "담배": "🚬", "사진": "📷", "비누": "🧼"
    }
    
    # 이름에 부분적으로 일치하는 이모티콘 찾기
    for key, emoji in emoji_map.items():
        if key in item_name.lower():
            return emoji
    
    # 기본 이모티콘
    return "🔍"

# 세션 상태 초기화 함수 업데이트
def init_session_state():
    """게임 관련 세션 상태를 초기화합니다."""
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'current_room' not in st.session_state:
        st.session_state.current_room = 1
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'end_time' not in st.session_state:
        st.session_state.end_time = None
    if 'rooms_data' not in st.session_state:
        st.session_state.rooms_data = None
    if 'inventory' not in st.session_state:
        st.session_state.inventory = []
    if 'has_key' not in st.session_state:
        st.session_state.has_key = False
    if 'has_golden_key' not in st.session_state:
        st.session_state.has_golden_key = False
    if 'puzzle_pieces' not in st.session_state:
        st.session_state.puzzle_pieces = []
    if 'visited_items' not in st.session_state:
        st.session_state.visited_items = []
    if 'last_response' not in st.session_state:
        st.session_state.last_response = ""
    if 'item_positions' not in st.session_state:
        st.session_state.item_positions = {}

# 게임 시작 함수 업데이트
def start_game():
    """게임을 시작하고 방 테마를 생성합니다."""
    st.session_state.game_started = True
    st.session_state.current_room = 1
    st.session_state.start_time = time.time()
    st.session_state.inventory = []
    st.session_state.inventory_details = {}
    st.session_state.has_key = False
    st.session_state.has_golden_key = False
    st.session_state.puzzle_pieces = []
    st.session_state.visited_items = []
    st.session_state.rooms_data = get_room_theme(client)
    
    # 각 방의 물건들 위치를 랜덤하게 배치
    st.session_state.item_positions = {}
    
    # 방 1 물건 위치 설정
    positions = list(range(30))
    random.shuffle(positions)
    st.session_state.item_positions["room1"] = positions
    
    # 방 2 물건 위치 설정
    positions = list(range(30))
    random.shuffle(positions)
    st.session_state.item_positions["room2"] = positions

# 메인 UI 함수
def main():
    st.set_page_config(page_title="방탈출 게임", page_icon="🚪", layout="wide")
    
    # CSS 스타일 추가
    st.markdown("""
    <style>
    .room-container {
        background-color: #1e2a3a;
        color: #e0e7ff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 2px solid #384766;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .room-title {
        color: #93c5fd;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    
    .item-container {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 15px;
        margin-top: 20px;
    }
    
    .item-card {
        background-color: #334155;
        color: #f8fafc;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100px;
    }
    
    .item-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        background-color: #475569;
    }
    
    .item-card.visited {
        background-color: #1f2937;
        opacity: 0.7;
    }
    
    .emoji {
        font-size: 28px;
        margin-bottom: 5px;
    }
    
    .name {
        font-size: 14px;
        text-align: center;
        font-weight: 500;
        color: #e2e8f0;
    }
    
    .inventory-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        background-color: #1e3a8a;
        color: #f0f9ff;
        padding: 5px 10px;
        border-radius: 5px;
    }
    
    .inventory-emoji {
        margin-right: 8px;
        font-size: 18px;
    }
    
    .response-box {
        background-color: #0f172a;
        color: #e2e8f0;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        margin: 15px 0;
        border-radius: 0 5px 5px 0;
    }
    
    .puzzle-section {
        background-color: #1e293b;
        color: #e2e8f0;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        border: 1px solid #3b82f6;
    }
    
    .timer-box {
        background-color: #1e3a8a;
        color: #e0f2fe;
        padding: 10px 15px;
        border-radius: 6px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    .game-over-container {
        text-align: center;
        padding: 40px;
        background-color: #0f172a;
        color: #f8fafc;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    
    .success-message {
        font-size: 32px;
        color: #4ade80;
        margin-bottom: 20px;
    }
    
    .time-result {
        font-size: 24px;
        color: #93c5fd;
        margin-bottom: 30px;
    }
    
    /* 스트림릿 기본 배경 및 색상 변경 */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* 스트림릿 사이드바 색상 변경 */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #1e293b;
    }
    
    /* 버튼 색상 변경 */
    .stButton>button[data-baseweb="button"] {
        background-color: #3b82f6;
        color: white;
    }
    
    .stButton>button[data-baseweb="button"]:hover {
        background-color: #2563eb;
    }
    
    /* 입력 필드 색상 변경 */
    .stTextInput>div>div>input {
        color: #f8fafc;
        background-color: #334155;
        border: 1px solid #475569;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #93c5fd;
    }
    
    /* 버튼 스타일 업데이트 */
    .stButton>button[data-baseweb="button"][type="secondary"] {
        background-color: #475569;
        color: #cbd5e1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 세션 상태 초기화
    init_session_state()
    
    # API 키 설정
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        api_key = st.sidebar.text_input("OpenAI API 키 입력", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    
    api_key_set = bool(os.environ.get("OPENAI_API_KEY"))
    
    st.title("🚪 방탈출 게임")
    st.write("GPT-4로 생성된 방탈출 게임을 플레이해보세요!")

    # 게임 시작 전 화면
    if not st.session_state.game_started:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            ### 🎮 게임 방법
            1. '게임 시작' 버튼을 누르면 두 개의 방이 생성됩니다.
            2. 각 방에는 30개의 물건이 있으며, 물건을 클릭하여 조사할 수 있습니다.
            3. 방 안의 퍼즐을 풀어 다음 방으로 이동하세요.
            4. 두 개의 방을 모두 통과하면 게임 클리어!
            
            ### 🧩 퍼즐 유형
            - **숫자 자물쇠**: 4자리 비밀번호를 찾아 입력해야 합니다.
            - **열쇠 자물쇠**: 황금 열쇠를 찾아야 합니다.
            - **그림 퍼즐**: 4개의 그림 조각을 모두 찾아야 합니다.
            """)


        with col2:
            if st.button("🎲 게임 시작", use_container_width=True, disabled=not api_key_set):
                start_game()
                st.rerun()
            
            if not api_key_set:
                st.warning("OpenAI API 키를 입력해야 게임을 시작할 수 있습니다.")

    # 게임 종료 화면
    elif st.session_state.current_room > 2:
        minutes, seconds = divmod(int(st.session_state.elapsed_time), 60)
        
        st.markdown(f"""
        <div class="game-over-container">
            <div class="success-message">🎉 축하합니다! 모든 방을 탈출했습니다! 🎉</div>
            <div class="time-result">⏱️ 소요 시간: {minutes}분 {seconds}초</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 다시 시작", use_container_width=True):
            start_game()
            st.rerun()

    # 게임 진행 화면
    else:
        current_room_key = f"room{st.session_state.current_room}"
        room_data = st.session_state.rooms_data[current_room_key]
        
        # 사이드바 정보
        with st.sidebar:
            # 경과 시간 표시
            current_time = time.time()
            elapsed = current_time - st.session_state.start_time
            minutes, seconds = divmod(int(elapsed), 60)
            
            st.markdown(f"""
            <div class="timer-box">
                ⏱️ 경과 시간: {minutes}분 {seconds}초
            </div>
            """, unsafe_allow_html=True)
            
            # 인벤토리 표시
            st.markdown("### 🎒 인벤토리")
            if st.session_state.inventory:
                for idx, item in enumerate(st.session_state.inventory):
                    emoji = get_item_emoji(item)
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"<div class='inventory-emoji' style='font-size:24px;text-align:center;'>{emoji}</div>", unsafe_allow_html=True)
                    with col2:
                        if st.button(f"{item}", key=f"inv_{idx}", use_container_width=True):
                            if item in st.session_state.inventory_details:
                                details = st.session_state.inventory_details[item]
                                st.info(f"**{item}**\n\n{details['description']}\n\n{details.get('clue', '')}")
            else:
                st.markdown("아직 획득한 아이템이 없습니다.")

        # 방 정보 표시
        st.markdown(f"""
        <div class="room-container">
            <h2 class="room-title">방 {st.session_state.current_room}: {room_data['name']}</h2>
            <p><em>{room_data['description']}</em></p>
            <p><strong>퍼즐 유형:</strong> {room_data['puzzle_type']}</p>
        </div>
        """, unsafe_allow_html=True)

        # 물건 조사 결과 표시
        if st.session_state.last_response:
            st.markdown(f"""
            <div class="response-box">
                {st.session_state.last_response}
            </div>
            """, unsafe_allow_html=True)
            
            # 인벤토리 추가 여부 확인
            if "인벤토리에 추가하시겠습니까?" in st.session_state.last_response and 'last_examined_item' in st.session_state:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("인벤토리에 추가", use_container_width=True):
                        current_room_key = f"room{st.session_state.current_room}"
                        room_data = st.session_state.rooms_data[current_room_key]
                        item = room_data["items"][st.session_state.last_examined_item]
                        add_to_inventory(item["name"], item)
                        st.session_state.last_response = f"{item['name']}을(를) 인벤토리에 추가했습니다."
                        st.rerun()
                with col2:
                    if st.button("무시하기", use_container_width=True):
                        st.session_state.last_response = "아이템을 무시했습니다."
                        st.rerun()

        # 물건 목록 표시 (랜덤 위치로 표시)
        st.markdown("<h3>🔍 방 안의 물건들</h3>", unsafe_allow_html=True)
        
        # 물건 컨테이너 시작
        st.markdown('<div class="item-container">', unsafe_allow_html=True)
        
        # 랜덤하게 위치한 물건들 보여주기
        item_positions = st.session_state.item_positions[current_room_key]
        
        # 물건 그리드 (6개씩 5줄)
        col_count = 6
        rows = [st.columns(col_count) for _ in range(5)]
        
        for i in range(30):
            row_idx = i // col_count
            col_idx = i % col_count
            
            item_idx = item_positions[i]
            item = room_data["items"][item_idx]
            is_visited = item["name"] in st.session_state.visited_items
            
            with rows[row_idx][col_idx]:
                emoji = get_item_emoji(item["name"])
                button_color = "secondary" if is_visited else "primary"
                button_label = f"{emoji} {item['name']}"
                
                if st.button(button_label, key=f"item_{item_idx}", use_container_width=True, type=button_color):
                    st.session_state.last_response = examine_item(item_idx)
                    st.session_state.last_examined_item = item_idx
                    st.rerun()
        
        # 물건 컨테이너 닫기
        st.markdown('</div>', unsafe_allow_html=True)

        # 퍼즐 풀기 UI
        st.markdown("""
        <div class="puzzle-section">
            <h3>🧩 퍼즐 풀기</h3>
        """, unsafe_allow_html=True)
        
        puzzle_type = room_data["puzzle_type"]
        col1, col2 = st.columns(2)
        
        with col1:
            if puzzle_type == "숫자 자물쇠":
                passcode = st.text_input("🔢 4자리 비밀번호를 입력하세요:", max_chars=4)
                if st.button("🔓 확인", use_container_width=True):
                    success, message = try_solve_puzzle(passcode)
                    if success:
                        st.success(message)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)

            elif puzzle_type == "열쇠 자물쇠":
                if st.button("🔑 황금 열쇠로 문 열기", use_container_width=True):
                    success, message = try_solve_puzzle()
                    if success:
                        st.success(message)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)

            elif puzzle_type == "그림 퍼즐":
                if st.button("🧩 그림 퍼즐 맞추기", use_container_width=True):
                    success, message = try_solve_puzzle()
                    if success:
                        st.success(message)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown("</div>", unsafe_allow_html=True)

# 앱 실행
if __name__ == "__main__":
    main()