개발 환경 초기 설정&도움말
=====
가상환경 설정
-------
https://wikidocs.net/70588 사이트 참고
명령프롬프트 이용
1. 가상 환경 디렉터리 생성하기
>mkdir <디렉터리명>
>cd <디렉터리명>
2. 가상 환경 만들기
>python -m venv <가상환경이름>
3. 가상 환경 진입하기
>cd <가상 환경 디렉터리 경로>\\<가상환경이름>\\Scripts
activate

필요한 라이브러리 설치
>django, bs4, selenium 
4. 가상 환경에서 벗어나기
>cd <가상 환경 디렉터리 경로>\\<가상환경이름>\\Scripts
deactivate





webdriver 설치 for 웹크롤링
-------------
1. chromedrive 설치
https://chromedriver.chromium.org/
2. clone 받은 프로젝트에서 website/time_table/views.py에서 35번째줄에 chromedrive가 설치되어 있는 경로 입력



git/github 관련 안내
-------
#### 기본 개발 단계
1. 메인저장소에서 fork버튼 눌러서 내 원격저장소로 fork해오기
2. 내 원격저장소로 이동해서 원격저장소의 주소 복사, 로컬 저장소에 clone 받기
> \$git clone <클론할 주소 - 내 원격 저장소의 주소>
3. 새로운 브랜치 만들어서 개발 진행
> \$git checkout -b <브랜치명>
4. 변경사항 로컬 저장소에 업데이트
> \$git status 
> \$git add <업데이트할 파일명>
> \$git commit
##### * 주의사항: 커밋해서는 안되는 파일들이 있음. 예를 들어 가상환경 폴더
> https://www.toptal.com/developers/gitignore
> 위 사이트에서 django, python, venv, 개발툴(ex. pycharm, vscode) 입력해서 .gitignore 파일 만들어서 사용

5. 로컬 저장소 변경사항 내 원격 저장소에 반영
> \$git push origin <브랜치명>
6. github에서 메인저장소에 merge 요청하기.
----
#### 내 로컬 저장소 메인 저장소의 최신버전으로 업데이트하기
1. remote 저장소 확인
>\$git remote -v
2. upstream 주소 추가
>\$git remote add upstream <메인저장소주소>
3. 메인저장소에서 내용 복사해오기
>\$git fetch upstream
5. 복사해 온 내용 로컬 저장소에 merge
>\$git merge upstream/main
----
#### 기타
- 커밋 취소
>\$git reset HEAD^
- 커밋 메시지 수정
>\$git commit -amend
- 브랜치 제거
>\$git branch -d <브랜치명>##### Online Educational Program for University Students