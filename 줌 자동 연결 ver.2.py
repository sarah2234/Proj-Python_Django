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

# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome('') #본인 컴퓨터에서 chromedrive가 있는 경로 입력
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')

class Student:
    __days = ['월', '화', '수', '목', '금', '토', '일']
    __today = datetime.datetime.today().weekday()  # 오늘의 요일 출력: print(days[a])


    def zoom_link(self,current_lecture):
        # 로그인
        driver.get('https://cbnu.blackboard.com/')
        driver.find_element_by_name('uid').send_keys('')  # 학번 작성
        driver.find_element_by_name('pswd').send_keys('')  # Blackboard 비밀번호 작성
        driver.find_element_by_xpath('//*[@id="entry-login"]').click()

        # 페이지 아래에 과목명이 있을 경우 스크롤 다운 해야함

        self.link_thru_notice(current_lecture)

    def link_thru_notice(self,current_lecture): #해당 과목 내 공지 사항으로 들어가서 링크 받는 경우
        try:
            course = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="base_tools"]/bb-base-navigation-button[4]/div/li/a')))
        finally:
            pass
        driver.get('https://cbnu.blackboard.com/ultra/course')
        time.sleep(3)

        try:
            print(current_lecture)
            scroll = driver.find_element_by_tag_name('body')
            scroll.click()
            for num in range(0, 20):
                scroll.click()
                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1) #페이지 로딩 시간을 준다
                course = driver.find_element_by_partial_link_text(current_lecture) #교과목명 검색
                course.click()
                break
            try:
                course = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.NAME, 'classic-learn-iframe')))
            finally:
                pass
            driver.switch_to.frame('classic-learn-iframe') #블랙보드 과제란은 iframe 사용

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
            try:  # 필독!! 스크롤 다운할 때 최상단에 있는 줌 링크 갖고 올 것!
                zoom = driver.find_element_by_partial_link_text(
                    'zoom.us')
                action = ActionChains(driver)
                action.move_to_element(zoom).perform()  # zoom이 있는 곳까지 스크롤 다운
                zoom.click()  # zoom 링크가 있을 때 'zoom.us' 텍스트를 가진 최상단의 링크 클릭하기
            except NoSuchElementException:  # 존재하지 않을 경우
                print("줌 링크가 존재하지 않습니다.")
        except NoSuchElementException:  # 존재하지 않을 경우
            print("줌 링크가 존재하지 않습니다.")


student1=Student()
print("1 : 동일한 줌 링크로 계속 수업을 진행하는 경우 >> 오픈소스기초프로젝트")
print("2 : 수업마다 올려주시는 경우 (정각에서 10분 정도 차이 고려) >> 나머지")
subject=input("줌 수업 스타일 선택 (과목명 입력) >> ")
student1.zoom_link(subject)