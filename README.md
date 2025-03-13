# 🚪 GPT-4 기반 방탈출 게임

GPT-4 API를 활용한 무한한 테마의 방탈출(이스케이프 룸) 게임입니다. 매번 다른 테마와 퍼즐을 생성하여 새로운 경험을 제공합니다.

## 📋 기능

- **동적 테마 생성**: GPT-4 API를 통해 다양한 테마(해적선, 고대 신전, 연구실, 병원 등)의 방탈출 시나리오를 자동 생성합니다.
- **다양한 퍼즐 유형**: 숫자 자물쇠, 열쇠 자물쇠, 그림 퍼즐 등 다양한 유형의 퍼즐을 제공합니다.
- **시각적 UI**: Streamlit을 사용한 직관적이고 상호작용이 가능한 사용자 인터페이스를 제공합니다.
- **인벤토리 시스템**: 아이템을 수집하고 관리할 수 있는 인벤토리 시스템을 구현했습니다.
- **오프라인 모드**: API 키가 없어도 미리 준비된 고품질 테마로 게임을 즐길 수 있습니다.

## 🎮 게임 방법

1. 게임을 시작하면 두 개의 연결된 방이 생성됩니다.
2. 각 방에는 30개의 물건이 있으며, 이 중 4개는 퍼즐 해결에 중요한 단서를 가지고 있습니다.
3. 물건을 클릭하여 조사하고, 단서를 모아 퍼즐을 해결해야 합니다.
4. 첫 번째 방의 퍼즐을 풀면 두 번째 방으로 이동할 수 있습니다.
5. 두 번째 방의 퍼즐까지 해결하면 게임 클리어!

## 🖥️ 게임 화면
<img width="1440" alt="image" src="https://github.com/user-attachments/assets/38d3f8c6-15a1-41e2-b2f6-95953d3697e3" />


## 🧩 퍼즐 유형

- **숫자 자물쇠**: 4자리 숫자 비밀번호를 찾아 입력해야 합니다. 각 아이템은 특정 숫자와 그 순서에 대한 단서를 제공합니다.
- **열쇠 자물쇠**: 작은 열쇠를 찾아 상자를 열고, 그 안에서 황금 열쇠를 획득해야 합니다.
- **그림 퍼즐**: 4개의 그림 조각을 모두 찾아서 완성해야 합니다.

## 🛠️ 설치 및 실행

### 필요 조건
- Python 3.7 이상
- OpenAI API 키 (선택 사항)

### 설치

1. 저장소 클론하기
```bash
git clone https://github.com/yourusername/room-escape-gpt.git
cd room-escape-gpt
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. API 키 설정 (선택 사항)
```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. 실행
```bash
streamlit run room_escape.py
```

## 🔧 기술 스택

- **Python**: 주요 프로그래밍 언어
- **Streamlit**: 웹 인터페이스 구현
- **OpenAI API**: GPT-4 모델을 활용한 동적 콘텐츠 생성
- **dotenv**: 환경 변수 관리

## 📝 라이선스

이 프로젝트는 MIT 라이선스에 따라 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여

이슈 제기, 기능 제안, 풀 리퀘스트 등 모든 형태의 기여를 환영합니다.

## 📸 스크린샷

_(여기에 게임 스크린샷을 추가하세요)_
