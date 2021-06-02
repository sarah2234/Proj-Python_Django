# requests(속도가 빠르다), selenium(동적 웹페이지 수집가능, 쉬운 login)
# import requests
from selenium import webdriver
# html 코드를 Python이 이해하는 객체 구조로 변환하는 Parsing 수행
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoSuchElementException, InvalidArgumentException

from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from pytz import timezone, utc

from .models import Data, Activity
from apps.userprofile.models import Profile
from django.db.models import Q
import re
import os

import pandas as pd  # 엑셀을 다루는 라이브러리 pandas
from selenium.webdriver.common.keys import Keys
import time

# 한국 시간대 사용
kst = timezone('Asia/Seoul')

# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument('--start-fullscreen')
options.add_argument('--no-sandbox')
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

# chrome driver를 불러오고 위의 option을 적용시킴
# CHROMEDRIVER_PATH 환경 변수에 개발하면서 사용할 본인 컴퓨터 안의 chromedrive 경로 저장
os.environ["CHROMEDRIVER_PATH"] = '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe'
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)

date_list = ['월', '화', '수', '목', '금', '토', '일']


def cieat_interest(request):
    if request.user.id is None:
        return redirect('login')
    activity_list = Activity.objects.filter(user=request.user).order_by('department')
    context = {'activity_list': activity_list}
    return render(request, 'cieat.html', context)


def cieat_submit(request):
    if request.user.id is None:
        return redirect('login')
    if request.method == "GET":
        return redirect('time_table:choose_timetable')
    elif request.method == "POST":
        for data in request.POST.getlist('data'):
            d = Activity.objects.get(id=data)
            driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/header/div[2]/div/a')))
                # 로그인
                # get_schedule을 통해 이미 로그인 된 상태면 pass
                driver.find_element_by_xpath('/html/body/div[3]/header/div[2]/div/a').send_keys(Keys.ENTER)  # 로그인 버튼 클릭
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, 'loginForm')))
                driver.find_element_by_name('userId').send_keys(Profile.objects.get(user=request.user).student_ID)  # 입력받은 학번으로 로그인
                driver.find_element_by_name('userPw').send_keys(Profile.objects.get(user=request.user).CBNU_PW)  # 입력받은 비밀번호로 로그인
                driver.find_element_by_class_name('btn_login_submit').click()
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[3]/header/div[2]/h1/a/img')))  # logo xpath
            except TimeoutException:
                # 이미 로그인 되어있는 상태
                pass
            except UnexpectedAlertPresentException:
                print("현재 서비스가 원활하지 않습니다.")
                print("잠시 후 다시 이용해 주십시오.")
                return redirect('time_table:cieat_interest')

            # 비교과 목록
            driver.get('https://cieat.chungbuk.ac.kr/ncrProgramAppl/a/m/goProgramApplList.do')  # 비교과 신청 주소
            page_num = 1  # 현재 페이지

            time.sleep(2)
            afford = driver.find_element_by_xpath('//*[@id="program_chk1"]')  # 신청 가능 체크 박스
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
                        if d.name in name.text.strip():
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
                            d.delete()
                            return redirect('time_table:cieat_interest')

                    except NoSuchElementException:
                        pass

                # 페이지의 아랫 부분
                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
                activities = driver.find_elements_by_class_name('program_lisbox')  # 비교과 활동들 전부 찾기
                for index, activity in enumerate(activities):
                    try:
                        name = activity.find_element_by_tag_name('dt')  # 활동명
                        if d.name in name.text.strip():
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
                            d.delete()
                            return redirect('time_table:cieat_interest')

                    except NoSuchElementException:
                        pass

                page_num += 1
                try:
                    driver.find_element_by_xpath(
                        '//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a[' + str(page_num) + ']').send_keys(
                        Keys.ENTER)
                    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                except NoSuchElementException:
                    print("해당 비교과 활동이 존재하지 않습니다.\n")
                    break
            d.delete()
    return redirect('time_table:cieat_interest')


def load_interest(request):
    if request.user.id is None:
        return redirect('login')
    if request.method == "GET":
        return redirect('time_table:setting')
    elif request.method == "POST":
        driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')  # 씨앗 주소
        try:
            driver.find_element_by_class_name('btn_login').click()  # CIEAT 로그인 버튼
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'loginForm')))
            driver.find_element_by_name('userId').send_keys(Profile.objects.get(user=request.user).student_ID)  # 입력받은 학번으로 로그인
            driver.find_element_by_name('userPw').send_keys(Profile.objects.get(user=request.user).CBNU_PW)  # 입력받은 비밀번호로 로그인
            driver.find_element_by_class_name('btn_login_submit').click()
        except UnexpectedAlertPresentException:  # 유저 정보 오기입
            print("학번과 비밀번호를 확인해주십시오.")
            return redirect('time_table:setting')
        except TimeoutException:
            pass
        except NoSuchElementException:
            pass  # 이미 로그인 되어있는 상태
        finally:
            driver.get('https://cieat.chungbuk.ac.kr/mileageHis/a/m/goMileageHisList.do')  # 마이페이지 주소

        # 내가 원하는 element가 load 될때까지 기다리기
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="mileageRcrHistList"]/div')))  # 마이페이지 내 교과 이수 현황
        except UnexpectedAlertPresentException: # 아주가끔 서버 다운 있음
            print("현재 서비스가 원활하지 않습니다.")
            print("잠시 후 다시 이용해 주십시오.")
            return redirect('time_table:setting')

# ------------------------- CIEAT의 마이페이지에서 전공 가져오기 ---------------------------

        major = driver.find_element_by_xpath(
            '//*[@id="container_skip"]/div/section[1]/div/table/tbody/tr[1]/td[1]').text.strip()  # 마이페이지의 학과/학부 텍스트
        major = major[:-2]  # '학과' 또는 '학부' 삭제

        major2 = driver.find_element_by_xpath(
            '//*[@id="container_skip"]/div/section[1]/div/table/tbody/tr[1]/td[2]').text.strip()  # 마이페이지의 부전공/복수전공 텍스트
        major2 = major2[6:]
        major2 = major2.split("복수전공 : ")
        major_sub = major2[0].rstrip()  # 복수전공이나 부전공을 안 해서 씨앗에서 어떻게 표시되는지 잘 모르겠음...
        major_multiple = major2[1].rstrip()
        
        user_major = [major, major_sub, major_multiple]

        # 입력한 키워드 있으면 추가
        if request.POST.get('keyword'):
            user_major.append(request.POST.get('keyword'))

# ------------------------- CIEAT에서 비교과 활동 읽어오기 ---------------------------

        driver.get('https://cieat.chungbuk.ac.kr/ncrProgramAppl/a/m/goProgramApplList.do')  # 비교과 신청 주소
        page_num = 1  # 현재 페이지

        time.sleep(2)
        afford = driver.find_element_by_xpath('//*[@id="program_chk1"]')  # 신청 가능 체크 박스
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
                    # 운영부서 검색
                    department = activity.find_elements_by_tag_name('dd')[2].find_elements_by_tag_name('span')[
                        1].text.strip()  # 운영부서, (부서이름)
                    for user_department in user_major:
                        if user_department != '-':
                            if user_department in department:
                                name = activity.find_element_by_tag_name('dt').find_element_by_tag_name('a').text.strip()  # 활동명
                                activity_detail = activity.find_elements_by_tag_name('dd')
                                registration_date = activity_detail[0].find_elements_by_tag_name('span')[1].text.strip()  # 모집 기간
                                activity_date = activity_detail[1].find_elements_by_tag_name('span')[1].text.strip()  # 활동 기간

                                if Activity.objects.filter(name=name, registration_date=registration_date,
                                                           activity_date=activity_date, department=department, user=request.user).count() == 0:
                                    Activity(name=name, registration_date=registration_date,
                                             activity_date=activity_date, department=department, user=request.user).save()

                    # 활동명 검색
                    name = activity.find_element_by_tag_name('dt').text.strip()  # 활동명
                    for user_department in user_major:
                        if user_department != '-':
                            if user_department in name:
                                name = activity.find_element_by_tag_name('dt').find_element_by_tag_name(
                                    'a').text.strip()  # 활동명
                                activity_detail = activity.find_elements_by_tag_name('dd')
                                registration_date = activity_detail[0].find_elements_by_tag_name('span')[
                                    1].text.strip()  # 모집 기간
                                activity_date = activity_detail[1].find_elements_by_tag_name('span')[
                                    1].text.strip()  # 활동 기간

                                if Activity.objects.filter(name=name, registration_date=registration_date,
                                                           activity_date=activity_date, department=department, user=request.user).count() == 0:
                                    Activity(name=name, registration_date=registration_date,
                                             activity_date=activity_date, department=department, user=request.user).save()

                except NoSuchElementException or TimeoutException:
                    print("현재 신청할 수 있는 비교과 활동이 존재하지 않습니다.\n")
                    pass

            page_num += 1
            try:  # 신청 가능한 모든 페이지에 대해 조사
                driver.find_element_by_xpath(
                    '//*[@id="ncrProgramAjaxDiv"]/article/div[2]/div/a[' + str(page_num) + ']').send_keys(Keys.ENTER)
                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
            except NoSuchElementException:
                break

    return redirect('time_table:cieat_interest')


def choose_timetable(request):
    if request.user.id is None:
        return redirect('login')
    if request.method == "GET":
        return redirect('time_table:choose_timetable')
    elif request.method == "POST":
        for data in request.POST.getlist('delete_data'):
            Data.objects.filter(id=data).delete()
    return redirect('time_table:schedule')


def load_timetable(request):
    if request.user.id is None:
        return redirect('login')
    pd.options.display.max_rows = 22  # 데이터 프레임 표시 최대 열수를 22로 지정
    pd.set_option('display.max_columns', 3668)  # 데이터 프레임 표시 최대 행수를 3668로 지정

    __course_list = {}  # 현재 수강 중인 과목의 이름과 교수님 목록 (과목명:교수님 형태) >> 엑셀 파일에서 과목 선별하기 위한 변수
    __time = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
              '20:00', '21:00', '22:00', '23:00', '24:00']  # 오전 09시 ~ 오전 00시
    __days = ['월', '화', '수', '목', '금', '토', '일']

    if request.method == "GET":
        return redirect('time_table:setting')
    elif request.method == "POST":
        driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')  # 씨앗 주소
        try:
            driver.find_element_by_class_name('btn_login').click()  # CIEAT 로그인 버튼
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'loginForm')))
            driver.find_element_by_name('userId').send_keys(Profile.objects.get(user=request.user).student_ID)  # 입력받은 학번으로 로그인
            driver.find_element_by_name('userPw').send_keys(Profile.objects.get(user=request.user).CBNU_PW)  # 입력받은 비밀번호로 로그인
            driver.find_element_by_class_name('btn_login_submit').click()
        except UnexpectedAlertPresentException:  # 유저 정보 오기입
            print("학번과 비밀번호를 확인해주십시오.")
            return redirect('time_table:setting')
        except TimeoutException:
            pass
        except NoSuchElementException:
            pass  # 이미 로그인 되어있는 상태
        finally:
            driver.get('https://cieat.chungbuk.ac.kr/mileageHis/a/m/goMileageHisList.do')  # 마이페이지 주소

        # 내가 원하는 element가 load 될때까지 기다리기
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="mileageRcrHistList"]/div')))  # 마이페이지 내 교과 이수 현황
        except UnexpectedAlertPresentException: # 아주가끔 서버 다운 있음
            print("현재 서비스가 원활하지 않습니다.")
            print("잠시 후 다시 이용해 주십시오.")
            return redirect('time_table:setting')

        # 기존에 존재하는 시간표 초기화
        Data.objects.filter(sort='시간표', user=request.user).delete()

# ------------------------- CIEAT의 마이페이지에서 과목명 가져오기 ---------------------------

        tbody = driver.find_element_by_xpath('//*[@id="mileageRcrHistList"]/div').find_element_by_tag_name(
            'tbody')  # 교과 이수 현황 테이블
        rows = tbody.find_elements_by_tag_name('tr')  # 행 별로 저장
        try:
            for index, value in enumerate(rows):
                lecture = value.find_elements_by_tag_name('td')[3]  # 과목명 (rows의 3번째 열에 해당)
                professor = value.find_elements_by_tag_name('td')[5]  # 교수님 (rows의 5번째 열에 해당)
                __course_list[lecture.text.strip()] = professor.text.strip()  # course_list에 '과목명: 교수님' 추가
        except IndexError:
            return redirect('time_table:setting')  # 5.28 3:44시경 CIEAT에서 교과 이수 현황이 출력되지 않는 문제(CIEAT의 문제라 달리 해결할 방도가 없음)

# --------------- 개설강좌계획서.xlsx(from 개신누리)에서 내가 수강하는 과목 정보 읽어오기 ---------------------------

        lectures_info_list = pd.read_excel('./개설강좌(계획서)조회.xlsx',  # 상대참조(같은 디렉터리 내에 엑셀 파일 있다고 가정)
                                           header=0,  # 칼럼이 시작하는 곳
                                           dtype={'순번': str,
                                                  '과목명': str,  # 각 칼럼의 자료형
                                                  '담당교수': str,
                                                  '수업시간': str},
                                           index_col='순번',  # '순번'을 index로 사용
                                           nrows=3668)  # 총 읽어올 열의 개수

        lectures_time_list = lectures_info_list.loc[:, ['과목명', '담당교수',
                                                        '수업시간']]  # loc으로 엑셀에서 '과목명', '담당교수', '수업시간'의 열만 추출, 앞의 :는 행 부분 / .iloc[index] 방법도 존재

        for lecture_name, professor in __course_list.items():  # CIEAT에서 가져온 과목명, 교수님 성함 (계절학기를 신청하였을 경우 계절학기가 추가될 수도 있음)
            searching_lecture = lectures_time_list[
                lectures_time_list[
                    '과목명'] == lecture_name]  # CIEAT의 마이페이지에서 가져온 과목명과 일치하는 행 선별, lectures_time_list[]으로 유효한 값을 가지는 행만 추출
            searching_lecture = searching_lecture[
                searching_lecture['담당교수'] == professor]  # 일치하는 과목명 선별 후 일치하는 담당교수 행 추출
            result = searching_lecture.loc[:,
                     ['과목명', '담당교수', '수업시간']]  # 선별되어진 searching_lecture의 '과목명', '담당교수'와 '수업시간' 열을 result에 저장

            list_from_result = result.values.tolist()  # 데이터프레임을 numpy의 ndarray로 변환: 데이터프레임 객체의 values 속성 사용 (pandas에 정의됨)
            # ndarray는 numpy의 다차원 행렬 자료구조 클래스, 파이썬이 제공하는 list 자료형과 동일한 출력 형태
            # list_from_result[index][0]=과목명
            # list_from_result[index][1]=담당교수
            # list_from_result[index][2]=시간 리스트

            if len(list_from_result) == 0:  # 해당 교과목이 존재하지 않는 경우
                pass  # 개신누리에서 개설강좌(계획서)조회.xlsx를 새로 다운 받야아 함!

            else:
                for data in list_from_result:  # list_from_result: 같은 이름 다른 수업명 리스트
                    split_time_with_room_info = data[2].split('  ')
                    time_1 = split_time_with_room_info[0].split('[')
                    # case 1: 일주일에 두 번 수업하는데 시간표가 {시간[강의실] 시간[강의실]}의 형태인 경우 split_time_with_room_info=['시간[강의실]', '시간[강의실]']
                    # case 2: 일주일에 두 번 수업하는데 시간표가 {시간 시간[강의실]}의 형태인 경우 ['시간', '시간[강의실]']
                    # case 2 예시: 월08 ,09  수03[강의실]
                    # case 3: 일주일에 한 번 수업하고 시간표가 {시간[강의실]}의 형태인 경우 ['시간[강의실]']

                    time_1[0] = time_1[0].strip()  # time_1[0]: 첫 번째 시간

                    day_of_first_lecture = time_1[0][0]  # 첫 번째 강의의 요일 가져오기
                    time_of_first_lecture = time_1[0][
                                            1:]  # 첫 번째 강의의 시간 리스트 가져오기 (ex: [01 ,02 ,03 ,04 ,05])
                    each_time_of_first_lecture = time_of_first_lecture.split(' ,')  # 첫 번째 강의의 시간 개별로 가져오기

                    # 시작시간 = each_time_of_first_lecture[0] + 8
                    # 끝나는 시간 = each_time_of_first_lecture[-1] + 9

                    # 첫 번째 시간
                    time_1_organized = [day_of_first_lecture,
                                        int(each_time_of_first_lecture[0]) + 8,
                                        int(each_time_of_first_lecture[-1]) + 9]

                    # 일주일에 수업을 2번하는 경우
                    try:
                        time_2 = split_time_with_room_info[1].split('[')
                        time_2[0] = time_2[0].strip()  # time_2[0]: 두 번째 시간
                        day_of_second_lecture = time_2[0][0]  # 두 번째 강의의 요일 가져오기
                        time_of_second_lecture = time_2[0][1:]  # 두 번째 강의의 시간 리스트 가져오기
                        each_time_of_second_lecture = time_of_second_lecture.split(' ,')  # 두 번째 강의의 시간 개별로 가져오기
                        time_2_organized = [day_of_second_lecture,
                                            int(each_time_of_second_lecture[0]) + 8,
                                            int(each_time_of_second_lecture[-1]) + 9]

                        Data(sort='시간표', name=data[1], context=data[0], content=time_1_organized[0],
                             start_h=time_1_organized[1], end_h=time_1_organized[2], user=request.user).save()
                        Data(sort='시간표', name=data[1], context=data[0], content=time_2_organized[0],
                             start_h=time_2_organized[1], end_h=time_2_organized[2], user=request.user).save()
                        # 교수님, 과목명, 요일, 시작시간, 끝시간 DB에 저장
                    except IndexError:  # 두 번째 시간 없을 때 time_1_organized만 넣기
                        Data(sort='시간표', name=data[1], context=data[0], content=time_1_organized[0],
                             start_h=time_1_organized[1], end_h=time_1_organized[2], user=request.user).save()
                        # time_2_organized는 try문 안에 선언

    # DB에서 시간표 읽어와서 출력
    context = {'class': Data.objects.filter(sort='시간표', user=request.user).order_by('context')}
    return render(request, 'time_table/choose_timetable.html', context)


def setting(request):
    if request.user.id is None:
        return redirect('login')
    return render(request, 'setting.html')
    # return redirect('time_table:setting')


def add_schedule(request):
    if request.user.id is None:
        return redirect('login')
    return render(request, 'time_table/add_schedule.html')


# 지금은 특정 날짜, 시간만 입력받을 수 있는데 추후에 요일별 반복 기능도 추가하기.
def add_function(request):
    if request.user.id is None:
        return redirect('login')
    name = request.POST.get('name')
    content = request.POST.get('content')
    date = request.POST.get('date')
    start_h = request.POST.get('start_h')
    end_h = request.POST.get('end_h')
    time_input = "".join([date, "-", start_h])
    time = datetime.strptime(time_input, '%Y-%m-%d-%H:%M').replace(tzinfo=kst)
    if Data.objects.filter(sort='개인일정', name=name, context=content, content=date_list[time.weekday()],
                           time=time, start_h=int(start_h.split(":")[0]), end_h=int(end_h.split(":")[0]), user=request.user).count() == 0:
        Data(sort='개인일정', name=name, context=content, content=date_list[time.weekday()],
             time=time, start_h=int(start_h.split(":")[0]), end_h=int(end_h.split(":")[0]), user=request.user).save()
    return redirect('time_table:schedule')


def edit_schedule(request, data_id):
    if request.user.id is None:
        return redirect('login')
    data = Data.objects.get(id=data_id)
    context = {'data': data}
    return render(request, 'time_table/edit_schedule.html', context)


def delete_function(request, data_id):
    if request.user.id is None:
        return redirect('login')
    Data.objects.get(id=data_id).delete()
    return redirect('time_table:schedule')


def edit_function(request, data_id):
    if request.user.id is None:
        return redirect('login')
    Data.objects.get(id=data_id).delete()
    name = request.POST.get('name')
    content = request.POST.get('content')
    date = request.POST.get('date')
    start_h = request.POST.get('start_h')
    end_h = request.POST.get('end_h')
    time_input = "".join([date, "-", start_h])
    time = datetime.strptime(time_input, '%Y-%m-%d-%H:%M').replace(tzinfo=kst)
    Data(sort='개인일정', name=name, context=content, content=date_list[time.weekday()],
         time=time, start_h=int(start_h.split(":")[0]), end_h=int(end_h.split(":")[0]), user=request.user).save()
    return redirect('time_table:schedule')


def delete_assignment(request, data_id):
    if request.user.id is None:
        return redirect('login')
    t = Data.objects.get(id=data_id)
    t.valid = 0
    t.save()
    return redirect('time_table:schedule')


def assignment_schedule(request, assignment_id):
    if request.user.id is None:
        return redirect('login')
    assignment = Data.objects.get(id=assignment_id)
    context = {'assignment': assignment}
    return render(request, 'time_table/assignment_schedule.html', context)


def available_time(request, assignment_id):
    if request.user.id is None:
        return redirect('login')
    # schedule 함수랑 비슷하게 오늘부터 과제 마감일까지 시간표, 개인일정 쭉 읽어오는데
    # 요일, 시간에 항목이 있으면 count = 0, 없으면 count++해서 count == need_time이면 일정 생성.
    # count = 0일때 start_h 업데이트
    assignment = Data.objects.get(id=assignment_id)
    name = "".join([assignment.context, " 과제하기"])
    content = assignment.name

    need_time = int(request.POST.get('need_time'))
    # 일정 생성할때 고려할 시간범위. 추후에 사용자한테서 입력받아오도록 수정.
    time_list = range(8, 18)
    now = datetime.now().replace(tzinfo=kst)
    count = 0
    while True:
        now = now + timedelta(days=1)
        # 과제 기한을 넘어가면 종료
        if now > assignment.time:
            print('과제할 시간이 없습니다.')
            return redirect('time_table:schedule')
        now_date = date_list[now.weekday()]
        for _time in time_list:
            temp = Data.objects.filter(Q(sort='시간표', content=now_date, start_h__lte=_time, end_h__gt=_time, user=request.user)
                                       | Q(sort='개인일정', content=now_date, start_h__lte=_time, end_h__gt=_time, user=request.user))
            if temp:
                count = 0
            else:
                if count == 0:
                    start_h = _time
                count = count+1
            print(temp)
            print(count)
            print(start_h)
            if count == need_time:
                time_input = "".join([str(now.year), "-", str(now.month), "-", str(now.day), "-", str(start_h), ":00"])
                # 이미 이 과제에 대한 일정이 있을 경우 삭제하고 추가
                if Data.objects.filter(sort='개인일정', name=name, context=content, user=request.user).count() != 0:
                    Data.objects.filter(sort='개인일정', name=name, context=content, user=request.user).delete()
                Data(sort='개인일정', name=name, context=content, content=now_date,
                     time=datetime.strptime(time_input, '%Y-%m-%d-%H:%M'),
                     start_h=start_h, end_h=start_h+need_time, user=request.user).save()
                return redirect('time_table:schedule')


def schedule(request):  # 일정들 DB에서 불러와서 출력
    if request.user.id is None:
        return redirect('login')
    now = datetime.now()
    now_date = date_list[datetime.today().weekday()]

    # 날짜 지난 과제 삭제
    Data.objects.filter(sort='과제', time__lt=now, user=request.user).delete()
    # 날짜 지난 일정 삭제
    Data.objects.filter(sort='개인일정', time__lt=now, end_h__lt=now.hour, user=request.user).delete()

    # list_schedule. 시간 순서대로 정렬.
    today_s = datetime(now.year, now.month, now.day)
    today_e = datetime(now.year, now.month, now.day, 23, 59)
    # 오늘 시간표, 일정 합쳐서 불러오기
    today_list = Data.objects.filter(Q(sort='시간표', content=now_date, end_h__gt=now.hour, user=request.user)
                                     | Q(sort='개인일정', time__lte=today_e), user=request.user).order_by('start_h')

    # time_table
    time_list = ["09", "10", "11", "12", "13", "14", "15", "16", "17"]
    weekday = ['월', '화', '수', '목', '금', '토']
    # 시간별로 묶어서 저장
    time_table = []
    for _time in time_list:
        # 요일별로 묶어서 저장
        sametime = []
        for date in weekday:
            temp = Data.objects.filter(sort='시간표', content=date, start_h__lte=int(_time), end_h__gt=int(_time), user=request.user)
            if temp:
                sametime.append(temp)
            else:
                sametime.append('empty')
        time_table.append({_time: sametime})  # 시간이랑 요일별로 묶어서 저장한거 딕셔너리로 함께 저장

    # 앞으로 남은 과제 읽어오기, 개인일정도 같이 읽어올 수 있도록 수정하기.
    data_list = Data.objects.filter(Q(sort='과제', time__gte=today_s, user=request.user)
                                    | Q(sort='개인일정', time__gt=today_e), user=request.user).order_by('time')
    context = {'now': now, 'date': now_date, 'today_list': today_list,
               'time_table': time_table, 'data_list': data_list, 'today_e': today_e}

# ---------------- link to zoom ------------------------
#   과목 시작 시간과 현재 시간을 비교해서 실행
    today_schedule = Data.objects.filter(sort='시간표', content=now_date, end_h__gt=now.hour, user=request.user)
    if today_schedule:
        lecture_info = today_schedule[0]  # 첫번째 강의
        # 시작 시간 2분 전일 때 줌 링크 연결
        if lecture_info.start_h - 1 == now.hour and now.minute == 58:
            zoom_link(request.user, lecture_info.context)

    return render(request, 'template.html', context)


def zoom_link(user, current_lecture):  # 해당 과목 내 공지 사항으로 들어가서 링크 받음

    driver.get('https://cbnu.blackboard.com/')
    # 가끔씩 학번이랑 비밀번호를 홈페이지에 입력하지 못하고 오류가 발생하는 경우가 있어서 추가.
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "uid")))
        # 로그인 되어있지 않는 경우 로그인
        driver.find_element_by_name('uid').send_keys(Profile.objects.get(user=user).student_ID)  # 학번
        driver.find_element_by_name('pswd').send_keys(Profile.objects.get(user=user).CBNU_PW)  # Blackboard 비밀번호
        driver.find_element_by_xpath('//*[@id="entry-login"]').click()
    except TimeoutException:
        print('로그인상태')
        pass
    except UnexpectedAlertPresentException:  # 유저 정보 오기입
        print("학번과 비밀번호를 확인해주십시오.")
        return redirect('time_table:schedule')
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
        except TimeoutException:
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
            course = driver.find_element_by_partial_link_text('zoom.us')  # 줌 링크가 있는 요소 발견
            print("줌링크발견")
            go_to_zoom(course.text.strip())  # 줌 실행 화면을 창을 띄워서 보여주기 위함
            return  # driver 설정이 다른 파일이 해당 링크를 입력받기
            # coure.click()를 쓰지 않고 새 탭에서 여는 방식을 채택한 이유: 줌 링크를 열면 어떤 사람은 'zoom meetings를 여시겠습니까'가 뜸.
            # '항상 zoom.us에서 연결된 앱에 있는 이 유형의 링크를 열도록 허용' 체크박스를 표시 안 하면 생기는데, 이거는 웹의 요소가 아니라서 웹크롤링으로 해결할 수 없음.

        except NoSuchElementException:
            pass

        scroll.click()
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

        if num == 19:
            print("줌 링크가 존재하지 않습니다.")


def go_to_zoom(link_text):
    try:
        _driver = webdriver.Chrome('/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')  # 창 띄워야 함
        _driver.get(link_text)  # 약 1분 정도 소요됨!! >> 따라서 수업 시작 1분 전에 줌 화면을 크롬에 띄움
        time.sleep(60)  # 1분 후에 종료
    except InvalidArgumentException:  # 잘못된 형식의 링크
        print("해당 줌 페이지가 존재하지 않습니다.\n")


def crawling(request):
    if request.user.id is None:
        return redirect('login')
    if request.method == "GET":
        return render(request, 'template.html')
    elif request.method == "POST":
        # 로그인
        driver.get('https://cbnu.blackboard.com/')
        # 가끔씩 학번이랑 비밀번호를 홈페이지에 입력하지 못하고 오류가 발생하는 경우가 있어서 추가.
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "uid")))
            # 로그인 되어있지 않는 경우 로그인
            driver.find_element_by_name('uid').send_keys(Profile.objects.get(user=request.user).student_ID)  # 학번
            driver.find_element_by_name('pswd').send_keys(Profile.objects.get(user=request.user).CBNU_PW)  # Blackboard 비밀번호
            driver.find_element_by_xpath('//*[@id="entry-login"]').click()
        except TimeoutException:
            print('로그인상태')
            pass
        except UnexpectedAlertPresentException:  # 유저 정보 오기입
            print("학번과 비밀번호를 확인해주십시오.")
            return redirect('time_table:schedule')
        finally:
            driver.get('https://cbnu.blackboard.com/ultra/stream')

        # 내가 원하는 element가 load 될때까지 기다리기
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "activity-feed")))
        finally:
            pass

        # BeautifulSoup으로 html소스를 python객체로 변환하기
        # 첫 인자는 html 소스코드, 두 번째 인자는 어떤 parser를 이용할지 명시.
        # Python 내장 html.parser
        soup = bs(driver.page_source, 'html.parser')

        # select - CSS Selector를 이용해 조건과 일치하는 모든 객체들을 List로 반환

        soup = soup.find('div', class_="activity-stream row collapse")

        upcoming = soup.find('div', class_="js-upcomingStreamEntries activity-group columns main-column")
        # 왜 읽어오지 못하나 했더니 today는 비어있을 때도 있다.
        today = soup.find('div', class_="js-todayStreamEntries activity-group columns main-column")
        # previous = soup.find('div', class_="js-previousStreamEntries activity-group columns main-column")

        # Data 클래스 하나에 upcoming, today, previous 구분 없이 저장. 추후에 필요시 구분해서 저장하도록 수정할 것.

        # 제공 예정
        if upcoming is not None:
            element_cards = upcoming.find('ul', class_="activity-feed").find_all(class_='element-card')
            if element_cards is not None:
                for element_card in element_cards:

                    # sort - 종류(과제, 공지, 성적..)
                    sort = "찾을 수 없음"
                    find_result = element_card.find('svg')
                    if find_result is not None:
                        sort = find_result.attrs.get('aria-label')

                    details = element_card.find('div', class_="element-details")
                    context_ellipsis = details.find('div', class_="context ellipsis").text.strip()
                    name = details.find('div', class_="name").text.strip()

                    # content - 성적 입력 최적화
                    IsItGrade = element_card.find("bb-ui-icon-grades")
                    if IsItGrade is not None:
                        contents = details.find('div', class_="content").text.strip().split()
                        if contents:
                            content = "".join(["내 성적 - ", contents[3], contents[4]])
                    # 과제일 경우 마감 기한 입력 최적화
                    elif sort == '과제':
                        content = details.find('div', class_="content").text.strip()
                        contents = re.split(': |. ', content)
                        if contents:
                            # year = "".join(["20", contents[1]])
                            # month = contents[2]
                            # day = contents[3]
                            # date = date_list[calendar.weekday(int("".join(["20", contents[1]])),
                            #                                   int(contents[2]), int(contents[3]))]
                            # time = contents[4].split(':')
                            # hour = time[0]
                            # minute = time[1]
                            time_input = "".join(["20", contents[1], "-", contents[2], "-", contents[3], "-", contents[4]])
                    else:
                        content = details.find('div', class_="content").text.strip()

                    #       due_date = details.find('div', class_="due-date").text.strip()
                    #       summary = details.find('div', class_="content").text.strip()

                    # 중복된 데이터는 DB에 저장하지 않는다.
                    if sort == '과제':
                        if Data.objects.filter(sort='과제', context=context_ellipsis, name=name,
                                               content=content, user=request.user).count() == 0:
                            Data(sort='과제', context=context_ellipsis, name=name,
                                 content=content, time=datetime.strptime(time_input, '%Y-%m-%d-%H:%M').replace(tzinfo=kst), user=request.user).save()
                    # 과제 외의 일정 일단 주석처리
                    # else:
                    #     if Data.objects.filter(sort=sort, context_ellipsis=context_ellipsis, name=name,
                    #                            content=content).count() == 0:
                    #         Data(sort=sort, context_ellipsis=context_ellipsis, name=name,
                    #              content=content).save()

        # 오늘
        if today is not None:
            element_cards = today.find('ul', class_="activity-feed").find_all(class_='element-card')
            if element_cards is not None:
                for element_card in element_cards:

                    # sort - 종류(과제, 공지, 성적..)
                    sort = "찾을 수 없음"
                    find_result = element_card.find('svg')
                    if find_result is not None:
                        sort = find_result.attrs.get('aria-label')

                    details = element_card.find('div', class_="element-details")
                    context_ellipsis = details.find('div', class_="context ellipsis").text.strip()
                    name = details.find('div', class_="name").text.strip()

                    # content - 성적 입력 최적화
                    IsItGrade = element_card.find("bb-ui-icon-grades")
                    if IsItGrade is not None:
                        contents = details.find('div', class_="content").text.strip().split()
                        if contents:
                            content = "".join(["내 성적 - ", contents[3], contents[4]])
                    # 과제일 경우 마감 기한 입력 최적화
                    elif sort == '과제':
                        content = details.find('div', class_="content").text.strip()
                        contents = re.split(': |. ', content)
                        if contents:
                            # year = "".join(["20", contents[1]])
                            # month = contents[2]
                            # day = contents[3]
                            # date = date_list[calendar.weekday(int("".join(["20", contents[1]])),
                            #                                   int(contents[2]), int(contents[3]))]
                            # time = contents[4].split(':')
                            # hour = time[0]
                            # minute = time[1]
                            time_input = "".join(
                                ["20", contents[1], "-", contents[2], "-", contents[3], "-", contents[4]])
                    else:
                        content = details.find('div', class_="content").text.strip()

                    #       due_date = details.find('div', class_="due-date").text.strip()
                    #       summary = details.find('div', class_="content").text.strip()

                    # 중복된 데이터는 DB에 저장하지 않는다.
                    if sort == '과제':
                        if Data.objects.filter(sort='과제', context=context_ellipsis, name=name,
                                               content=content).count() == 0:
                            Data(sort='과제', context=context_ellipsis, name=name,
                                 content=content, time=datetime.strptime(time_input, '%Y-%m-%d-%H:%M').replace(tzinfo=kst), user=request.user).save()
                    # 과제 외의 일정 일단 주석처리
                    # else:
                    #     if Data.objects.filter(sort=sort, context_ellipsis=context_ellipsis, name=name,
                    #                            content=content).count() == 0:
                    #         Data(sort=sort, context_ellipsis=context_ellipsis, name=name,
                    #              content=content).save()
    return redirect('time_table:schedule')
