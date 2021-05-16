from selenium import webdriver
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException

import pandas as pd #엑셀을 다루는 라이브러리 pandas
import numpy as np #수치 해석용 라이브러리

pd.options.display.max_rows=22 # 데이터 프레임 표시 최대 열수를 22로 지정
pd.set_option('display.max_columns',3668) # 데이터 프레임 표시 최대 행수를 3668로 지정


# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome('/Users/이승현/chromedriver/chromedriver') #본인 컴퓨터에서 chromedrive가 있는 경로 입력
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')

class Student:
    __course_list={} #현재 수강 중인 과목의 이름과 교수님 목록 (과목명:교수님 형태)
    __schedule_list={} #현재 수강 중인 과목의 이름과 시간 목록 (과목명:(요일과 시간 구분x)시간 형태)
    __schedule_list_ver2={} #현재 수강 중인 과목의 이름과 시간 목록 (과목명:(요일과 시간이 리스트 형태로 구분)시간 형태) // 만일을 위하여 구현함
    __week=[] #일주일 강의 시간 목록
    # [['월', ['08,09']], ['수', ['03']]]
    # [['금', ['01,02,03']], ['', []]]과 같은 형태로 출력됨. (*숫자는 int형이 아닌 str형!)
    __course_name_for_DB=[]#DB를 위한 교과목명              Q!: class로 배열을 만들어서 값을 대입하나?
    __professor_for_DB=[]#DB를 위한 교수명 리스트
#week는 어떻게 처리해야하지?

    def get_subject_name(self):  # CIEAT의 마이페이지에서 과목명 가져오기
        driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')  # 씨앗 주소
        driver.find_element_by_class_name('btn_login').click()  # CIEAT 로그인 버튼
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'loginForm')))
        finally:
            pass

        # 개인정보 삭제하고 커밋할 것!!!
        try:
            driver.find_element_by_name('userId').send_keys('')  # 학번 작성
            driver.find_element_by_name('userPw').send_keys('')  # 비밀번호 작성
            driver.find_element_by_class_name('btn_login_submit').click()
            try:
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_skip"]/ul/li[9]/ul'))) #마이페이지 xpath
            finally:
                pass
        except UnexpectedAlertPresentException: #유저 정보 오기입
            print("학번과 비밀번호를 확인해주십시오.")
            return

        driver.get('https://cieat.chungbuk.ac.kr/mileageHis/a/m/goMileageHisList.do')  # 마이페이지 주소
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="mileageRcrHistList"]/div')))  # 마이페이지 내 교과 이수 현황
        finally:
            pass

        tbody = driver.find_element_by_xpath('//*[@id="mileageRcrHistList"]/div').find_element_by_tag_name(
            'tbody')  # 교과 이수 현황 테이블
        rows = tbody.find_elements_by_tag_name('tr')  # 행 별로 저장
        for index, value in enumerate(rows):
            lecture = value.find_elements_by_tag_name('td')[3]  # 과목명 (rows의 3번째 열에 해당)
            professor = value.find_elements_by_tag_name('td')[5]  # 교수님 (rows의 5번째 열에 해당)
            self.__course_list[lecture.text.strip()] = professor.text.strip()  # course_list에 '과목명: 교수님' 추가

            self.__course_name_for_DB.append(lecture.text.strip()) #DB용 교과목명 목록 구축
            self.__professor_for_DB.append(professor.text.strip()) #DB용 교수님 성함 목록 구축

    def get_schedule(self): #개신누리에서 엑셀 파일 다운 받아서 전체 강좌의 시간표 확인
        lectures_info_list=pd.read_excel('./개설강좌(계획서)조회.xlsx', #상대참조(같은 디렉터리 내에 엑셀 파일 있다고 가정)
                                         header=0, #칼럼이 시작하는 곳
                                         dtype={'순번':str,
                                                '과목명':str, #각 칼럼의 자료형
                                                '담당교수':str,
                                                '수업시간':str},
                                        index_col='순번', #'순번'을 index로 사용
                                        nrows=3668) #총 읽어올 열의 개수

        lectures_time_list=lectures_info_list.loc[:,['과목명','담당교수','수업시간']] #loc으로 엑셀에서 '과목명', '담당교수', '수업시간'의 열만 추출, 앞의 :는 행 부분 / .iloc[index] 방법도 존재

        for lecture_name, professor in self.__course_list.items():
            searching_lecture = lectures_time_list[
                lectures_time_list['과목명'] == lecture_name]  #CIEAT의 마이페이지에서 가져온 과목명과 일치하는 행 선별, lectures_time_list[]으로 유효한 값을 가지는 행만 추출
            searching_lecture=searching_lecture[searching_lecture['담당교수']==professor] #일치하는 과목명 선별 후 일치하는 담당교수 행 추출
            result=searching_lecture.loc[:,['과목명','담당교수','수업시간']] #선별되어진 searching_lecture의 '과목명', '담당교수'와 '수업시간' 열을 result에 저장 (순번은 왜 자꾸 출력되는 거지?)
            list_from_result=result.values.tolist() #데이터프레임을 numpy의 ndarray로 변환: 데이터프레임 객체의 values 속성 사용 (pandas에 정의됨)
                                                    #ndarray는 numpy의 다차원 행렬 자료구조 클래스, 파이썬이 제공하는 list 자료형과 동일한 출력 형태

            # list_from_result[index][0]=과목명
            # list_from_result[index][1]=담당교수
            # list_from_result[index][2]=시간 리스트
            if len(list_from_result)==0:
                print("해당 과목명과 일치하는 수업이 존재하지 않습니다.")
            else:
                print("[",lecture_name,"] 검색 결과:", sep='')
                for index in range(len(list_from_result)):
                    time_1=list_from_result[index][2].split('[') #time_1[0]: 첫 번째 시간
                    #시간표가 시간[강의실] 시간[강의실]의 형태인 경우 parsing_1=[시간, 강의실] 시간, 강의실]] 꼴
                    try:
                        time_2=time_1[1].split(']') #time_2[-1]: 두 번째 시간
                    except ValueError: #두 번째 시간 없을 때 time_2는 공백란
                        time_2=''

                    time_1[0].strip()
                    time_2[-1].strip()
                    time=time_1[0]+time_2[-1]
                    del list_from_result[index][2] #시간+[강의실]에서 시간만 보이도록 변경
                    list_from_result[index].append(time) #시간 리스트에 추가
                    print(index+1,":",list_from_result[index][1],"교수님 -",list_from_result[index][2]) #'순번 : 000 교수님 - 시간' 형태로 출력
                print()

            while(True):
                print("*과목을 잘못 선택하였을 경우 0을 입력해주세요.")
                choose_lecture_num=int(input("해당하는 과목의 순번 입력 >> ")) #수업명이 겹치는 경우가 꽤 있으므로 시간대를 고름
                print()

                if choose_lecture_num==0:
                    break
                elif 1 <= choose_lecture_num and choose_lecture_num <= len(list_from_result):
                    lecture_time=list_from_result[choose_lecture_num-1][2] #lecture_time: 찾은 과목의 시간을 저장
                    self.__schedule_list[lecture_name]=lecture_time #스케줄 딕셔너리에 과목명:(요일과 시간 구분x)시간 형태로 입력
                    break
                else:
                    print("순번에 맞게 입력해주세요.")


    def get_divided_schedule(self): #수강하는 과목을 요일과 n교시로 나누어 리스트에 저장
        for lecture_name, lecture_time in self.__schedule_list.items():
            number_of_lecture=lecture_time.split('  ') #공백이 최소 2번 이상 나온 후 다른 요일의 수업 표시하므로 split

            number_of_lecture[0]=number_of_lecture[0].replace(' ','')
            day_of_first_lecture=number_of_lecture[0][0] #첫 번째 강의의 요일 가져오기
            time_of_first_lecture=number_of_lecture[0][1:] #첫 번째 강의의 시간 리스트 가져오기
            each_time_of_first_lecture=time_of_first_lecture.split(' ,') #첫 번째 강의의 시간 개별로 가져오기

            try: #수업을 1주일에 한 번만 하는 경우 대비
                number_of_lecture[1]=number_of_lecture[1].replace(' ','')
                day_of_second_lecture = number_of_lecture[1][0]  # 두 번째 강의의 요일 가져오기
                time_of_second_lecture = number_of_lecture[1][1:]  # 두 번째 강의의 시간 리스트 가져오기
                each_time_of_second_lecture = time_of_second_lecture.split(' ,')  # 두 번째 강의의 시간 개별로 가져오기
            except IndexError:
                day_of_second_lecture=''
                each_time_of_second_lecture=[]

            modified_lecture_time=[[day_of_first_lecture,each_time_of_first_lecture],[day_of_second_lecture,each_time_of_second_lecture]] #[[첫 번째 요일,[시간1,시간2,...]],[두 번째 요일,[시간1,시간2,...]]]
            self.__week.append(modified_lecture_time) #week에 상단 리스트 형태로 삽입

            self.__schedule_list_ver2[lecture_name]=modified_lecture_time #schedule_list_ver2는 schedule_list와 달리 요일과 시간이 구분되어있음

student1=Student()
student1.get_subject_name()
student1.get_schedule()
student1.get_divided_schedule()