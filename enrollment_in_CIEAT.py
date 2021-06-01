from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException

import time
import get_schedule  # test

# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument('--start-fullscreen')

driver=webdriver.Chrome('/Users/이승현/chromedriver/chromedriver', options=options)  # 본인 컴퓨터에서 chromedrive가 있는 경로 입력

def interesting_CIEAT_activities_by_major(id, password, operating_department):  # 과 이름으로 비교과 활동 찾기
    if operating_department == '-':  # 없는 경우
        return
    driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')
    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/header/div[2]/div/a')))
        # 로그인
        # get_schedule을 통해 이미 로그인 된 상태면 pass
        driver.find_element_by_xpath('/html/body/div[3]/header/div[2]/div/a').send_keys(Keys.ENTER)  # 로그인 버튼 클릭
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'loginForm')))
        driver.find_element_by_name('userId').send_keys(id)  # 입력받은 학번으로 로그인
        driver.find_element_by_name('userPw').send_keys(password)  # 입력받은 비밀번호로 로그인
        driver.find_element_by_class_name('btn_login_submit').click()
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/header/div[2]/h1/a/img')))  # logo xpath
    except TimeoutException:
        # 이미 로그인 되어있는 상태
        pass
    except UnexpectedAlertPresentException:
        print("현재 서비스가 원활하지 않습니다.")
        print("잠시 후 다시 이용해 주십시오.")
        return

    # 비교과 목록
    driver.get('https://cieat.chungbuk.ac.kr/ncrProgramAppl/a/m/goProgramApplList.do')  # 비교과 신청 주소
    page_num=1 # 현재 페이지

    time.sleep(2)
    afford=driver.find_element_by_xpath('//*[@id="program_chk1"]')  # 신청 가능 체크 박스
    # <a herf= ~~>에서 herf 속성에 url이 아닌 자바스크립트가 들어간 경우 click()로 주소에 들어갈 수 없음
    # 이럴 땐 onclick 내부 명령어가 실행되도록 하든가 (send_key('\n') 또는 send_key(Keys.ENTER)) 아니면 자바스크립트 명령어 실행
    driver.execute_script("arguments[0].click();", afford)

    # 신청 가능한 것만 찾기
    scroll = driver.find_element_by_tag_name('body').click()
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

    while True:
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        activities = driver.find_elements_by_class_name('program_lisbox')  # 비교과 활동들 전부 찾기
        for index, activity in enumerate(activities):
            try:
                department=activity.find_elements_by_tag_name('dd')[2].find_elements_by_tag_name('span')[1].text.strip()  # 운영부서, (부서이름)
                if operating_department in department:
                    name=activity.find_element_by_tag_name('dt').find_element_by_tag_name('a').text.strip()  # 활동명
                    activity_detail=activity.find_elements_by_tag_name('dd')
                    registration_date=activity_detail[0].find_elements_by_tag_name('span')[1].text.strip()  # 모집 기간
                    activity_date=activity_detail[1].find_elements_by_tag_name('span')[1].text.strip()  # 활동 기간
                    department  # 운영 부서
                    print(name)
                    print("모집기간:", registration_date)
                    print("활동기간:", activity_date)
                    print("운영부서:",department)
                    print()

            except NoSuchElementException or TimeoutException:
                print("현재 신청할 수 있는 비교과 활동이 존재하지 않습니다.\n")
                pass

        page_num+=1
        try:  # 신청 가능한 모든 페이지에 대해 조사
            driver.find_element_by_xpath('//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a['+str(page_num)+']').send_keys(Keys.ENTER)
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
        except NoSuchElementException:
            break

def interesting_CIEAT_activities_by_keyword(id, password, keyword):  # 과 이름으로 비교과 활동 찾기
    if keyword == '-':  # 없는 경우
        return
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
            EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_skip"]/ul/li[9]/ul')))  # logo xpath
    except TimeoutException:
        # 이미 로그인 되어있는 상태
        pass
    except UnexpectedAlertPresentException:
        print("현재 서비스가 원활하지 않습니다.")
        print("잠시 후 다시 이용해 주십시오.")
        return

    # 비교과 목록
    driver.get('https://cieat.chungbuk.ac.kr/ncrProgramAppl/a/m/goProgramApplList.do')  # 비교과 신청 주소
    page_num=1 # 현재 페이지

    time.sleep(2)
    afford=driver.find_element_by_xpath('//*[@id="program_chk1"]')  # 신청 가능 체크 박스
    # <a herf= ~~>에서 herf 속성에 url이 아닌 자바스크립트가 들어간 경우 click()로 주소에 들어갈 수 없음
    # 이럴 땐 onclick 내부 명령어가 실행되도록 하든가 (send_key('\n') 또는 send_key(Keys.ENTER)) 아니면 자바스크립트 명령어 실행
    driver.execute_script("arguments[0].click();", afford)

    # 세 페이지로 한정하여 찾기
    scroll = driver.find_element_by_tag_name('body').click()
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

    while True:
        time.sleep(1)
        activities = driver.find_elements_by_class_name('program_lisbox')  # 비교과 활동들 전부 찾기
        for index, activity in enumerate(activities):
            try:
                name = activity.find_element_by_tag_name('dt').text.strip()  # 활동명
                if keyword in name:
                    activity_detail = activity.find_elements_by_tag_name('dd')
                    registration_date=activity_detail[0].find_elements_by_tag_name('span')[1].text.strip()  # 모집 기간
                    activity_date=activity_detail[1].find_elements_by_tag_name('span')[1].text.strip()  # 활동 기간
                    department=activity.find_elements_by_tag_name('dd')[2].find_elements_by_tag_name('span')[1].text.strip()  # 운영부서, (부서이름)  # 운영 부서
                    print(name)
                    print("모집기간:", registration_date)
                    print("활동기간:", activity_date)
                    print("운영부서:",department)
                    print()

            except NoSuchElementException or TimeoutException:
                pass

        page_num+=1
        try:  # 신청 가능한 모든 페이지에 대해 조사
            driver.find_element_by_xpath('//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a['+str(page_num)+']').send_keys(Keys.ENTER)
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
        except NoSuchElementException:
            break

def go_to_CIEAT_activity_page(id, password, name_of_interesting_activity):  # 활동명 찾아서 해당 씨앗 페이지로 가기
    driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')
    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/header/div[2]/div/a')))
        # 로그인
        # get_schedule을 통해 이미 로그인 된 상태면 pass
        driver.find_element_by_xpath('/html/body/div[3]/header/div[2]/div/a').send_keys(Keys.ENTER)  # 로그인 버튼 클릭
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'loginForm')))
        driver.find_element_by_name('userId').send_keys(id)  # 입력받은 학번으로 로그인
        driver.find_element_by_name('userPw').send_keys(password)  # 입력받은 비밀번호로 로그인
        driver.find_element_by_class_name('btn_login_submit').click()
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/header/div[2]/h1/a/img')))  # logo xpath
    except TimeoutException:
        # 이미 로그인 되어있는 상태
        pass
    except UnexpectedAlertPresentException:
        print("현재 서비스가 원활하지 않습니다.")
        print("잠시 후 다시 이용해 주십시오.")
        return

    # 비교과 목록
    driver.get('https://cieat.chungbuk.ac.kr/ncrProgramAppl/a/m/goProgramApplList.do')  # 비교과 신청 주소
    page_num=1 # 현재 페이지

    time.sleep(2)
    afford=driver.find_element_by_xpath('//*[@id="program_chk1"]')  # 신청 가능 체크 박스
    # <a herf= ~~>에서 herf 속성에 url이 아닌 자바스크립트가 들어간 경우 click()로 주소에 들어갈 수 없음
    # 이럴 땐 onclick 내부 명령어가 실행되도록 하든가 (send_key('\n') 또는 send_key(Keys.ENTER)) 아니면 자바스크립트 명령어 실행
    driver.execute_script("arguments[0].click();", afford)

    # 신청 가능한 것만 찾기
    scroll = driver.find_element_by_tag_name('body').click()
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

    while True:
        # 페이지의 윗 부분
        time.sleep(1)
        activities = driver.find_elements_by_class_name('program_lisbox')  # 비교과 활동들 전부 찾기
        for index, activity in enumerate(activities):
            try:
                name = activity.find_element_by_tag_name('dt')  # 활동명
                if name_of_interesting_activity in name.text.strip():
                    activity.find_element_by_tag_name('a').send_keys(Keys.ENTER)  # 전공과 관련있는 비교과 활동일 때

                    # 스크롤 높이 가져옴
                    last_height = driver.execute_script("return document.body.scrollHeight")
                    while True:
                        # 끝까지 스크롤 다운
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        # 스크롤 다운 후 스크롤 높이 다시 가져옴
                        new_height = driver.execute_script("return document.body.scrollHeight")
                        if new_height == last_height:
                            break
                        last_height = new_height


                    driver.find_element_by_xpath('//*[@id="container_skip"]/div[2]/button[1]').send_keys(
                        Keys.ENTER)  # 신청접수 버튼
                    WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                                    '신청하시겠습니까?')
                    alert=driver.switch_to_alert()
                    alert.accept()
                    print("신청 접수되었습니다.\n")
                    return

            except NoSuchElementException:
                pass

        # 페이지의 아랫 부분
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        activities = driver.find_elements_by_class_name('program_lisbox')  # 비교과 활동들 전부 찾기
        for index, activity in enumerate(activities):
            try:
                name = activity.find_element_by_tag_name('dt')  # 활동명
                if name_of_interesting_activity in name.text.strip():
                    activity.find_element_by_tag_name('a').send_keys(Keys.ENTER)  # 전공과 관련있는 비교과 활동일 때

                    # 스크롤 높이 가져옴
                    last_height = driver.execute_script("return document.body.scrollHeight")
                    while True:
                        # 끝까지 스크롤 다운
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        # 스크롤 다운 후 스크롤 높이 다시 가져옴
                        new_height = driver.execute_script("return document.body.scrollHeight")
                        if new_height == last_height:
                            break
                        last_height = new_height

                    driver.find_element_by_xpath('//*[@id="container_skip"]/div[2]/button[1]').send_keys(
                        Keys.ENTER)  # 신청접수 버튼
                    WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                                   '신청하시겠습니까?')
                    alert = driver.switch_to_alert()
                    alert.accept()
                    print("신청 접수되었습니다.\n")
                    return

            except NoSuchElementException:
                pass

        page_num+=1
        try:
            driver.find_element_by_xpath('//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a['+str(page_num)+']').send_keys(Keys.ENTER)
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
        except NoSuchElementException:
            print("해당 비교과 활동이 존재하지 않습니다.\n")
            break