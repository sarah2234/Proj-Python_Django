from selenium import webdriver
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains

import datetime

# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome('') #본인 컴퓨터에서 chromedrive가 있는 경로 입력
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')


# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome('/Users/이승현/chromedriver/chromedriver') #본인 컴퓨터에서 chromedrive가 있는 경로 입력
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')


days=['월요일', '화요일','수요일','목요일','금요일','토요일','일요일']
today=datetime.datetime.today().weekday() #오늘의 요일 출력: print(days[a])

# 로그인
driver.get('https://cbnu.blackboard.com/')
driver.find_element_by_name('uid').send_keys('') #학번 작성
driver.find_element_by_name('pswd').send_keys('') #Blackboard 비밀번호 작성
driver.find_element_by_xpath('//*[@id="entry-login"]').click()

driver.get('https://cbnu.blackboard.com/ultra/stream')

# 내가 원하는 element가 load 될때까지 기다리기
try:
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'activity-group-title'))) #활동 스트림 '오늘'
finally:
    pass

soup = bs(driver.page_source, 'html.parser')

driver.implicitly_wait(3)
#각 수업의 실강 시간을 입력받을 것
#하단의 3 과목은 예시
dangerous=input("자료구조/선형대수학/오픈소스기초프로젝트/객체지향 프로그래밍인가요? >> ") #페이지 아래에 과목명이 있을 경우 스크롤 다운 해야함

if dangerous=='오픈소스기초프로젝트': #한 개의 줌 링크로 계속 수업이 진행되는 경우 (해당 과목의 공지사항에 들어가야 함)
    course = driver.find_element_by_partial_link_text('오픈소스기초프로젝트').click()
    driver.switch_to.frame('classic-learn-iframe')
    # 내가 원하는 element가 load 될때까지 기다리기
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
    try: #필독!! 스크롤 다운해서 최상단에 있는 줌 링크 갖고 올 것!
        zoom = driver.find_element_by_partial_link_text(
            'zoom.us')
        action=ActionChains(driver)
        action.move_to_element(zoom).perform() #zoom이 있는 곳까지 스크롤 다운
        zoom.click() # zoom 링크가 있을 때 'zoom.us' 텍스트를 가진 최상단의 링크 클릭하기
    except NoSuchElementException: #존재하지 않을 경우
        pass

elif dangerous=='자료구조' or dangerous=='선형대수학': #줌 링크가 미리 올라와있는 경우 #공지 사항 낱개의 class:'element-details'
    if days[today]=='월요일':
        try:
            recent_notice = driver.find_element_by_xpath('//*[@id="activity-stream"]/div[3]/ul')  # 최근 공지
            notice_of_today = driver.find_element_by_xpath('//*[@id="activity-stream"]/div[2]/ul')  # 오늘자 공지
            recent_announcement_list = recent_notice.find_elements_by_class_name('element-details') #최근 공지 사항들의 class
            todays_announcement_list=notice_of_today.find_elements_by_class_name('element-details') #오늘자 공지 사항들의 class
            #스크롤 다운하면서 announcement 리스트 생성하는 방법 모색
            for announcement in todays_announcement_list:
                course_name = announcement.find_element_by_tag_name('a')  # 과목명의 태그는 'a'
                if course_name == '자료구조':
                    break
            zoom = course_name.find_element_by_partial_link_text(
                'zoom.us')  # https://zoom.us를 하려고 했으나 https://us숫자web.zoom.us인 경우가 존재
            action = ActionChains(driver)
            action.move_to_element(zoom).perform()
            zoom.click()  # zoom 링크가 있을 때 'zoom.us' 텍스트를 가진 최상단의 링크 클릭하기
        except NoSuchElementException:
            pass
        finally:
            print("실시간 수업 링크로 연결")  # 실행 확인 문구 (나중에 수정)
    else:
        print(days[today]) # 실행 확인 문구 (나중에 수정)

else: #일반적인 경우 (당일에 줌 링크 올라옴)
    try:
        notice_of_today=driver.find_element_by_xpath('//*[@id="activity-stream"]/div[2]/ul') #오늘자 공지:2 / 최근 공지:3
        zoom=notice_of_today.find_element_by_partial_link_text("객체지향").find_element_by_partial_link_text(
                    'zoom.us') #https://zoom.us를 하려고 했으나 https://us숫자web.zoom.us인 경우가 존재
        action=ActionChains(driver)
        action.move_to_element(zoom).perform
        zoom.click()
    except NoSuchElementException:
        print("no") # 실행 확인 문구 (나중에 수정)
        pass
    finally:
        print("실시간 수업 링크로 연결")  # 실행 확인 문구 (나중에 수정)
