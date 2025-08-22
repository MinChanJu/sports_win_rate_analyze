# sports_win_rate_analyze

## 시작하기
- step1 git 설치
  - 아래 내용 터미널애서 실행
  - git -v
  - git config --global user.name "[깃허브 닉네임]"
  - git config --global user.email "[깃허브 가입 이메일]"
- step2 python 설치
- step3 vsc 설치
  - [korean], [python extension pack] 확장 설치
- step4 터미널 열기
- step5 원하는 디렉토리 이동 (`cd [원하는 디렉토리]`)
- step6 `git clone https://github.com/MinChanJu/sports_win_rate_analyze.git` 실행
- step7 `cd sports_win_rate_analyze` 실행
- step8 확인

## 계획서
### 주민찬
- [ ] 웹크롤링 모든 경기에 대한 데이터 기록 툴

### 김승준, 황성현
- [ ] [kbl_quarters_data.json](kbl_quarters_data.json)의 Q1, Q2, Q3, Q4 데이터를 가지고 쿼터별 누적 기록표 함수 작성
  - [ ] 매개변수로는 이전까지의 누적 표와 다음 쿼터 정보가 들어감
  - [ ] 김승준 kim.py
  - [ ] 황성현 hwang.py