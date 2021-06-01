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
>django, bs4, selenium, pandas, datetime, schedule, openpyxl, (이후 3개는 heroku용)gunicorn, django-heroku, psycopg2  
>(자세한 건 requirements.txt)      
4. 가상 환경에서 벗어나기
>cd <가상 환경 디렉터리 경로>\\<가상환경이름>\\Scripts
deactivate

pycharm - 가상환경 설정방법
------
1. File 메뉴 -> open -> Open-Source-Project-03(클론받은프로젝트폴더) 선택해서 열기
2. File 메뉴 -> setting -> Project:~ 들어가서 Python Interpreter 선택

3. 우측 상단 톱니바퀴 -> add 클릭
4. Virtulaenv Environment 탭 선택
5. New enviroment -> Location: 현재 프로젝트 폴더\venv (예시: C:\Open-Source-Project-03\venv)
   Base interpreter 설정: python.exe가 들어있는 경로(파이썬이 설치되어있는 폴더)
6. 체크박스 2개 선택할 필요 X
7. OK 선택
8. Python Interpreter가 방금 추가한 가상환경으로 바뀌면 완료. 바뀌지 않으면
   add -> Existing environment에서 방금 만든 가상환경 선택해서 OK
9. 왼쪽 상단 +버튼 눌러서 필요한 라이브러리(django, bs4, selenium 등) 설치

3~8번 과정: 새로운 가상환경 추가 / 만들지 않고 사전에 이미 만들어 놓은 가상환경을 선택해서 사용해도 무방

프로젝트 실행
-------
가상환경에 진입되어 있는 상태에서 Open-Source-Project-03\website 폴더 안에 들어가서
python manage.py runserver 터미널에 입력


webdriver 설치 for 웹크롤링
-------------
1. chromedrive 설치
https://chromedriver.chromium.org/
2. clone 받은 프로젝트에서 website/time_table/views.py에서 38번째줄에 chromedrive가 설치되어 있는 경로 입력
(37번째줄 주석참고)


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
----
Heroku 서버 구축 방법
====================
루트 디렉토리 내에서 추가해야할 사항들 (새로 생성한 파일들은 반드시 루트 디렉토리에 위치시켜야 함)
------------------------------------------------------------------------------------------
* Procfile
  * vs code와 같은 텍스트 편집기를 사용하여 web: gunicorn (프로젝트 이름).wsgi 입력
  * 확장자는 없음 (.txt를 붙이면 안됨)
  * 제대로 생성하지 않으면 heroku에서 dyno가 생성되지 않아 web이 실행되지 않음
* requirements.txt
  * cmd에서 pip freeze>requirements.txt 커맨드 입력
  * 필요한 라이브러리 모두 포함
* runtime.txt
  * 사용하고 있는 python의 버전에 대한 정보 기입 (python-3.9.4)
* Pipfile
  * https://www.caxy.com/blog/starting-scratch-creating-and-installing-python-app-heroku
* setup.py
  * https://www.jetbrains.com/help/pycharm/creating-and-running-setup-py.html
* views.py
  * chromedriver options 중에서 --no-sandbox를 반드시 추가해야함 (해당 옵션은 크롬의 보안과 관련된 옵션)   
  * import os 한 후 os.environ.get("GOOGLE_CHROME_BIN"), os.environ.get("CHROMEDRIVER_PATH")로 크롬과 크롬 드라이버 경로 지정
* settings.py
  * ALLOWED_HOSTS, STATIC_ROOT, 마지막 줄에 django_heroku.settings(locals()) 추가 (https://www.youtube.com/watch?v=6DI_7Zja8Zc&t=2723s)  
 
 Heroku Commands (Heroku CLI 설치 필수)
 --------------------------------------------------
 * 헤로쿠 로그인: heroku login
 * git remote에 헤로쿠 추가: heroku git:remote -a (name of your app)
 * 데이터베이스 구축: heroku run python manage.py migrate
 * 관리자 계정 생성: heroku run python manage.py createsuperuser
 * 페이지 오픈: heroku open
 * dyno  연결: heroku ps:scale web=1
 * git heroku push master로 heroku에 바로 푸쉬가 가능하지만 빈번한 에러로 추천하지 않음
   * 대신 GitHub와  연동하여 자동/수동으로 deploy할 수 있는 기능 > heroku의 deploy 탭에서 설정 가능
 * 에러 확인: heroku logs --tail (ctrl+c로 종료)   
 
 그 외 Heroku 설정 사항
 --------------------------------------------------
 * heroku의 setting 탭에서 config vars & buildpack 추가 (https://eunjin3786.tistory.com/361)
 * admin 페이지: https://opensourceproject03.herokuapp.com/admin/
