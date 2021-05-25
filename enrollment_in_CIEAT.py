from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException

import time
import get_schedule

# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument('--start-fullscreen')  # 전체 화면

driver=webdriver.Chrome('/Users/이승현/chromedriver/chromedriver')  # 본인 컴퓨터에서 chromedrive가 있는 경로 입력

soup = bs(driver.page_source, 'html.parser')


def major_related_CIEAT_activities(id, password, major):
    driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')
    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'loginForm')))
        # 로그인
        # get_schedule을 통해 이미 로그인 된 상태면 pass
        driver.find_element_by_name('userId').send_keys(id)  # 입력받은 학번으로 로그인
        driver.find_element_by_name('userPw').send_keys(password)  # 입력받은 비밀번호로 로그인
        driver.find_element_by_class_name('btn_login_submit').click()
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_skip"]/ul/li[9]/ul')))  # 마이페이지 xpath
    except TimeoutException:
        # 이미 로그인 되어있는 상태
        pass
    except UnexpectedAlertPresentException:
        print("현재 서비스가 원활하지 않습니다.")
        print("잠시 후 다시 이용해 주십시오.")
        return

    # 비교과 목록
    driver.get('https://cieat.chungbuk.ac.kr/ncrProgramAppl/a/m/goProgramApplList.do')  # 비교과 신청 주소
    page_num=1

    # 세 페이지로 한정하여 찾기
    scroll = driver.find_element_by_tag_name('body').click()
    for i in range(0,2):
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN) # 끝까지 스크롤 다운
        time.sleep(1)

    while True:

        time.sleep(2)
        activities = driver.find_elements_by_class_name('program_lisbox')  # 비교과 활동들 전부 찾기
        index=0  # for 문이 이상함
        for activity in activities:
            print(index)
            try:
                department=activity.find_elements_by_tag_name('dd')[2].find_elements_by_tag_name('span')[1]  # 운영부서, (부서이름)
                print(department.text.strip())
                if department.text.strip() == major:
                    activity.find_element_by_tag_name('a').send_keys(Keys.ENTER)  # 전공과 관련있는 비교과 활동일 때
                    # 왜 클릭은 안 된다고 하고 엔터는 되는 것인가......
                    break

            except NoSuchElementException or TimeoutException:
                pass
            finally:
                print("break문")
                index+=1
            # 자동 신청을 구현해야 하나? 아니면 이에 대한 정보를 가져오는 것으로 해야하나? 일단 후자 선택

        get_info_of_CIEAT_activity()

        if page_num == 3:
            break


        try:
            driver.find_element_by_xpath('//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a[4]') #관심있는 활동 클릭해서 버튼 없어짐
        except TimeoutException:
            break

        if page_num == 1:
            # 페이지 넘기는 부분이 javascript로 구현되어 있음
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
                (By.XPATH,'//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a[4]'))).click()  # 2번째 페이지
            print('다음 페이지로 넘어갑니다.\n')  # 추후 삭제
            page_num += 1
            continue

        elif page_num == 2:
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a[5]'))).click()  # 3번째 페이지
            print('다음 페이지로 넘어갑니다.\n')  # 추후 삭제
            page_num += 1
            continue





def get_info_of_CIEAT_activity():  # 한 비교과 활동의 정보 받아오기 (필요한 것만!)
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'insertForm')))
    finally:
        pass
    title=driver.find_element_by_xpath('//*[@id="container_skip"]/section[1]/dl/dt/p').text.strip()  # 활동명
    date=driver.find_element_by_xpath('//*[@id="container_skip"]/section[1]/dl/dd[2]/text()').text.strip()  # 활동 기간
    detail_from_CIEAT=driver.find_element_by_class_name('addit_content')  # 교육 내용 및 운영방법 (모든 행)
    detail_for_user=''  # 유저에게 문자열로서 보여줄 detail
    for sentence in detail_from_CIEAT.find_elements_by_tag_name('strong'):  # 모든 글씨의 태그가 <strong>임
        detail_for_user=detail_for_user+sentence.text.strip()
        detail_for_user=detail_for_user+'\n'  # 한 줄에 하나씩 상세 정보 받아오기

    print(title)
    print(date)
    print(detail_for_user)

#너무 피곤해서 내가 코딩 쓰고도 맞게 쓰고 있는지 판단이 전혀 안 된다.


student=get_schedule.Student()
major_related_CIEAT_activities(student.id, student.password, '대학일자리센터')