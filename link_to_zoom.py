import selenium.common.exceptions
from selenium import webdriver
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

import datetime
import time
import schedule #특정 시간에 수행
import get_schedule #기존의 '수강 과목 시간표(CIEAT+Excel)을 get_schedule로 변경

def zoom_link(id, password, current_lecture):  # 해당 과목 내 공지 사항으로 들어가서 링크 받음
    # 창 띄우지 않는 설정. background에서 동작.
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')

    # chrome driver를 불러오고 위의 option을 적용시킴
    driver = webdriver.Chrome('/Users/이승현/chromedriver/chromedriver', options=options)  # 본인 컴퓨터에서 chromedrive가 있는 경로 입력
    # driver = webdriver.Chrome(
    #     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')
    driver.get('https://cbnu.blackboard.com/')
    try:  # 블랙보드 로그인
        driver.find_element_by_name('uid').send_keys(id)  # 학번 작성
        driver.find_element_by_name('pswd').send_keys(password)  # Blackboard 비밀번호 작성
        driver.find_element_by_xpath('//*[@id="entry-login"]').click()
    except NoSuchElementException:  # 이미 로그인 되어있음
        pass
    finally:
        driver.get('https://cbnu.blackboard.com/ultra/course')

    try:
        find = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'course-columns-current')))
    finally:
        pass

    # 페이지 아래에 과목명이 있을 경우 스크롤 다운 해야함
    # zoom 주소로 연결했을 때 밑에 zoom 다운 경고 표시
    scroll = driver.find_element_by_tag_name('body')
    for num in range(0, 20):
        try:  # 페이지 로딩 시간을 준다
            scroll.click()
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            find = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, current_lecture)))
        except selenium.common.exceptions.TimeoutException:
            continue

        try:
            course = driver.find_element_by_partial_link_text(current_lecture)  # 교과목명 검색
            course.click()
            break  # break 안 걸면 엉뚱한 곳으로 감
        except NoSuchElementException:
            pass

        if num == 19:  # 모두 탐색 완료
            print("해당 교과목이 존재하지 않습니다.")
            return

# 과목 발견 후
    try:
        course = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, 'classic-learn-iframe')))
    finally:
        pass
    driver.switch_to.frame('classic-learn-iframe')  # 블랙보드 과제란은 iframe 사용

    try:
        course = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'button-6')))
    finally:
        pass
    notice = driver.find_element_by_class_name('button-6')  # button-6: '나의 공지 사항' 란의 '더보기' 버튼
    notice.click()

    try:
        course = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.ID, 'pageTitleText')))  # 공지 사항 페이지에서 페이지의 제목 '공지 사항'의 id인 pageTitleText
    finally:
        pass

# 스크롤 다운할 때 최상단에 있는 줌 링크 갖고 올 것!
    scroll = driver.find_element_by_tag_name('body')
    scroll.click()
    for num in range(0, 20):
        time.sleep(1)  # 페이지 로딩 시간을 준다

# TA 링크에 대해서도 테스트 해보고 싶은데 테스트를 할 수가 없다. 그래도 기존에 작동하던 최상단의 줌 링크를 가져오는 건 잘 실행된다.
# 괜히 정밀하게 하겠답시고 driver.find_element_by_class_name('clearfix') (<<공지사항의 클래스) 하면 공지사항 먼저 찾은 다음 .find를 수행하므로 위로 올라갔다 밑으로 내려갔다 반복함
        try:
            TA = driver.find_element_by_partial_link_text('TA')  # TA라고 적혀있는 공지사항일 경우 그 공지는 넘김

        except NoSuchElementException:  # TA 공지사항 아닌 것들에 대해서만 조사
            try:
                course = driver.find_element_by_partial_link_text('zoom.us')  # 줌 링크가 있는 요소 발견
                go_to_zoom(course.text.strip())  # 줌 실행 화면을 창을 띄워서 보여주기 위함
                return # driver 설정이 다른 파일이 해당 링크를 입력받기

                # coure.click()를 쓰지 않고 새 탭에서 여는 방식을 채택한 이유: 줌 링크를 열면 어떤 사람은 'zoom meetings를 여시겠습니까'가 뜸.
                # '항상 zoom.us에서 연결된 앱에 있는 이 유형의 링크를 열도록 허용' 체크박스를 표시 안 하면 생기는데, 이거는 웹의 요소가 아니라서 웹크롤링으로 해결할 수 없음.
            except NoSuchElementException:  # 줌 링크가 존재하지 않을 경우
                pass
        scroll.click()
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

        if num == 19:
            print("줌 링크가 존재하지 않습니다.")

def go_to_zoom(link_text):
    driver = webdriver.Chrome('/Users/이승현/chromedriver/chromedriver')  # 창 띄워야 함
    driver.get(link_text)  # 약 1분 정도 소요됨!! >> 따라서 수업 시작 1분 전에 줌 화면을 크롬에 띄움

def take_class_on_a_date(id, password, lectures_sorted_by_week):
    today = datetime.datetime.today()
    today = today.weekday()  # 오늘의 요일

    for lecture_info in lectures_sorted_by_week[today]:  # 오늘의 요일에 하는 강의들 리스트 [강의명, 시작 시간, 끝나는 시간]
        # 시작 시간(lecture_info[1]) 2분 전일 때 줌 링크 연결 (zoom_link는 과목명(lecture_info[0]을 인수로 받음)
        lecture_info_time=datetime.datetime.strptime(lecture_info[1],"%H:%M")
        two_minutes_earlier = lecture_info_time - datetime.timedelta(minutes=2)  # 수업 시작 2분 전
        two_minutes_earlier = str(two_minutes_earlier.hour) + ':' + str(two_minutes_earlier.minute)
        if len(two_minutes_earlier) == 4:
            two_minutes_earlier = '0' + two_minutes_earlier
        schedule.every().day.at(two_minutes_earlier).do(zoom_link, id, password, lecture_info[0])
        print(lecture_info[0] + '수업 기다리기')
        print("(시작 시간: ", lecture_info[1], ")", sep='')

def put_at_the_end():
    while True:  # 무한 루프인 만큼 맨 아래에 코드 배치
        schedule.run_pending()
        time.sleep(1)

# https://jackerlab.com/python-library-schedule/를 참고하여 작성하였습니다.

student1 = get_schedule.Student()

student1.get_schedule()
take_class_on_a_date(student1.id, student1.password, student1.lectures_sorted_by_week)
put_at_the_end()




