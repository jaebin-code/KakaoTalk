# KakaoTalk
FastAPI, sqlite를 이용하여 채팅 서비스 구현

채팅 앱(ChatApp)
## 프로젝트 소개:

채팅 앱(ChatApp)은 카카오톡과 유사한 사용자 경험을 제공하는 웹 기반 채팅 플랫폼입니다. 사용자들은 로그인, 회원가입, 프로필 관리, 친구 목록 관리, 1대1 채팅, 단체 채팅, 그리고 사진 공유 등 다양한 기능을 구현했습니다.

주요 기능:

로그인 및 회원가입
프로필 관리
친구 목록
채팅 기능
사진 공유

기술 스택:

FastAPI
SQLite

## 사용 방법
저장소를 클론합니다.

bash
Copy code
git clone https://github.com/your-username/ChatApp.git

pip3 install fastapi[all] -> fastapi 다운로드
pip3 install sqlalchemy -> sqlalchemy 다운로드
pip3 install fastapi-login -> 로그인 기능 다운로드

uvicorn main:app --reload 를 터미널에 입력하면 실행됩니다.

브라우저에서 http://127.0.0.1:8000으로 접속하여 서비스를 이용하세요.
