from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException

import time
import get_schedule

# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

driver=webdriver.Chrome('/Users/이승현/chromedriver/chromedriver')  # 본인 컴퓨터에서 chromedrive가 있는 경로 입력

def major_related_CIEAT_activities(id, password, major):
    driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'loginForm')))
    finally:
        pass

    # 로그인
    driver.find_element_by_name('userId').send_keys(id)  # 입력받은 학번으로 로그인
    driver.find_element_by_name('userPw').send_keys(password)  # 입력받은 비밀번호로 로그인
    driver.find_element_by_class_name('btn_login_submit').click()
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_skip"]/ul/li[9]/ul')))  # 마이페이지 xpath
    finally:
        pass

    # 비교과 목록
    driver.find_element_by_xpath('//*[@id="gnb_skip"]/ul/li[5]/ul/li[2]/a').click()  # 비교과 신청 탭 클릭
    try:
        element=WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'program_listbox')))  # 프로그램의 클래스 로딩
    finally:
        pass

    try:
        interests=driver.find_element_by_tag_name('a').find_elements_by_partial_link_text(major)  # 자신의 학과와 관련된 비교과 활동들
        for interest in interests:
            interest.click()
            # 자동 신청을 구현해야 하나? 아니면 이에 대한 정보를 가져오는 것으로 해야하나? 일단 후자 선택
    except NoSuchElementException:
        pass
    finally:
        driver.find_element_by_class_name('page_con next_page').click()  # 다음 페이지 버튼

def get_info_of_CIEAT_activity():  # 한 비교과 활동의 정보 받아오기 (필요한 것만!)
    title=driver.find_element_by_xpath('//*[@id="container_skip"]/section[1]/dl/dt/p').text.strip()  # 활동명
    date=driver.find_element_by_xpath('//*[@id="container_skip"]/section[1]/dl/dd[2]/text()').text.strip()  # 활동 기간
    detail_from_CIEAT=driver.find_element_by_class_name('addit_content')  # 교육 내용 및 운영방법 (모든 행)
    detail_for_user=''  # 유저에게 문자열로서 보여줄 detail
    for sentence in detail_from_CIEAT.find_elements_by_tag_name('strong')  # 모든 글씨의 태그가 <strong>임
        detail=detail+sentence.text.strip()
        detail=detail+'\n'  # 한 줄에 하나씩 상세 정보 받아오기

#너무 피곤해서 내가 코딩 쓰고도 맞게 쓰고 있는지 판단이 전혀 안 된다.


student=get_schedule.Student()
major_related_CIEAT_activities(student.id, student.password, student.major)