from selenium import webdriver
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException

import pandas as pd #엑셀을 다루는 라이브러리 pandas
import datetime
import time

pd.options.display.max_rows=22 # 데이터 프레임 표시 최대 열수를 22로 지정
pd.set_option('display.max_columns',3668) # 데이터 프레임 표시 최대 행수를 3668로 지정


# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome('/Users/이승현/chromedriver/chromedriver', options=options) #본인 컴퓨터에서 chromedrive가 있는 경로 입력
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')

class Student:
    __course_list={} #현재 수강 중인 과목의 이름과 교수님 목록 (과목명:교수님 형태)
    __schedule_list={} #현재 수강 중인 과목의 이름과 시간 목록 ('컴퓨터구조': '월08 ,09  수03 '와 같은 형태) // 추후 lectures_sorted_by_week에서 요일별로 강의 정리하기 위함
    major='-' #enrollment_in_CIEAT.py에서 자신의 전공과 관련된 비교과 활동 웹크롤링
    major_sub='-' #enrollment_in_CIEAT.py에서 자신의 부전공과 관련된 비교과 활동 웹크롤링
    major_multiple='-' #enrollment_in_CIEAT.py에서 자신의 복수전공과 관련된 비교과 활동 웹크롤링

    __time=['09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00','24:00'] #오전 09시 ~ 오전 00시
    __days = ['월', '화', '수', '목', '금', '토', '일']

    lectures_sorted_by_week=[[],[],[],[],[],[],[]] #요일별로 강의 정리 (인덱스 0: 월요일)
    #ex)lectures_sorted_by_week[0]=[['선형대수학', '09:00', '10:00'], ['소프트웨어실전영어', '10:00', '12:00'], ['자료구조', '13:00', '15:00'], ['컴퓨터구조', '16:00', '18:00']]

    course_name_for_DB=[]  # DB를 위한 교과목명
    professor_for_DB=[]  # DB를 위한 교수명 리스트

    def __init__(self):
        self.login_error=1  # 학번이나 비밀번호 제대로 기입하면 0

        while self.login_error==1:
            self.id = input('학번을 입력하세요: ')
            self.password = input('비밀번호를 입력하세요: ')

            driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')  # 씨앗 주소
            driver.find_element_by_class_name('btn_login').click()  # CIEAT 로그인 버튼
            try:
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, 'loginForm')))
                driver.find_element_by_name('userId').send_keys(self.id)  # 입력받은 학번으로 로그인
                driver.find_element_by_name('userPw').send_keys(self.password)  # 입력받은 비밀번호로 로그인
                driver.find_element_by_class_name('btn_login_submit').click()
                self.login_error = 0  # 로그인 성공
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_skip"]/ul/li[9]/ul')))  # 마이페이지 xpath
            except UnexpectedAlertPresentException:  # 유저 정보 오기입
                print("학번과 비밀번호를 확인해주십시오.")
                print()
                self.login_error = 1
            except TimeoutException:
                pass  # 이미 로그인 되어있는 상태

        self._get_subject_name()

    def _get_subject_name(self):  # CIEAT의 마이페이지에서 과목명 가져오기 & 전공
        driver.get('https://cieat.chungbuk.ac.kr/mileageHis/a/m/goMileageHisList.do')  # 마이페이지 주소
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="mileageRcrHistList"]/div')))  # 마이페이지 내 교과 이수 현황
        except UnexpectedAlertPresentException:
            print("현재 서비스가 원활하지 않습니다.")
            print("잠시 후 다시 이용해 주십시오.")
            return  # 객체를 다시 생성해야 하나? 그런데 이건 아이디와 비밀번호를 웹 크롤러로 잘못 입력받았을 때 뜨는 페이지라서 괜찮을 거 같기도 (아주 가끔 서버 다운 있음)

        major=driver.find_element_by_xpath('//*[@id="container_skip"]/div/section[1]/div/table/tbody/tr[1]/td[1]').text.strip()  # 마이페이지의 학과/학부 텍스트
        self.major=major[:-2]  # '학과' 또는 '학부' 삭제

        major_sub=driver.find_element_by_xpath('//*[@id="container_skip"]/div/section[1]/div/table/tbody/tr[1]/td[2]').text.strip()   # 마이페이지의 부전공/복수전공 텍스트
        major_sub=major_sub[6:]
        major_sub=major_sub.split("복수전공 : ")
        self.major_sub=major_sub[0].rstrip()  # 복수전공이나 부전공을 안 해서 씨앗에서 어떻게 표시되는지 잘 모르겠음...
        self.major_multiple=major_sub[1].rstrip()

        tbody = driver.find_element_by_xpath('//*[@id="mileageRcrHistList"]/div').find_element_by_tag_name(
            'tbody')  # 교과 이수 현황 테이블
        rows = tbody.find_elements_by_tag_name('tr')  # 행 별로 저장
        for index, value in enumerate(rows):
            try:
                lecture = value.find_elements_by_tag_name('td')[3]  # 과목명 (rows의 3번째 열에 해당)
                professor = value.find_elements_by_tag_name('td')[5]  # 교수님 (rows의 5번째 열에 해당)
            except IndexError:  # 5.26 오전 3:45에 CIEAT 서버의 문제인지 이수 현황이 뜨지 않는 오류가 발생했다.
                print('다시 시도해주십시오.\n')
                return

            self.__course_list[lecture.text.strip()] = professor.text.strip()  # course_list에 '과목명: 교수님' 추가

            self.course_name_for_DB.append(lecture.text.strip()) #DB용 교과목명 목록 구축
            self.professor_for_DB.append(professor.text.strip()) #DB용 교수님 성함 목록 구축

    def get_schedule(self): #개신누리에서 엑셀 파일 다운 받아서 전체 강좌의 시간표 확인, CIEAT 내 교과목 이수 현황과 비교하여 사용자에게 입력받음
        #계절학기의 경우 학기 도중에 추가될 수 있으므로 사용자에게 0을 입력받아서 맨 마지막에 제외시킬 것

        deleting_course_list=[] #사용자가 제거하고 싶은 수강 과목을 해당 리스트에 저장 후 함수의 끝 부분에서 삭제 (반복문에서 삭제할 경우 딕셔너리의 길이가 달라짐)
        deleting_professor_list=[] ##사용자가 제거하고 싶은 수강 과목의 교수님 성함을 해당 리스트에 저장 후 함수의 끝 부분에서 삭제

        lectures_info_list=pd.read_excel('./개설강좌(계획서)조회.xlsx', #상대참조(같은 디렉터리 내에 엑셀 파일 있다고 가정)
                                         header=0, #칼럼이 시작하는 곳
                                         dtype={'순번':str,
                                                '과목명':str, #각 칼럼의 자료형
                                                '담당교수':str,
                                                '수업시간':str},
                                        index_col='순번', #'순번'을 index로 사용
                                        nrows=3668) #총 읽어올 열의 개수

        lectures_time_list=lectures_info_list.loc[:,['과목명','담당교수','수업시간']] #loc으로 엑셀에서 '과목명', '담당교수', '수업시간'의 열만 추출, 앞의 :는 행 부분 / .iloc[index] 방법도 존재

        for lecture_name, professor in self.__course_list.items(): #CIEAT에서 가져온 과목명, 교수님 성함 (계절학기를 신청하였을 경우 계절학기가 추가될 수도 있음)
            searching_lecture = lectures_time_list[
                lectures_time_list['과목명'] == lecture_name]  #CIEAT의 마이페이지에서 가져온 과목명과 일치하는 행 선별, lectures_time_list[]으로 유효한 값을 가지는 행만 추출
            searching_lecture=searching_lecture[searching_lecture['담당교수']==professor] #일치하는 과목명 선별 후 일치하는 담당교수 행 추출
            result=searching_lecture.loc[:,['과목명','담당교수','수업시간']] #선별되어진 searching_lecture의 '과목명', '담당교수'와 '수업시간' 열을 result에 저장

            list_from_result=result.values.tolist() #데이터프레임을 numpy의 ndarray로 변환: 데이터프레임 객체의 values 속성 사용 (pandas에 정의됨)
                                                    #ndarray는 numpy의 다차원 행렬 자료구조 클래스, 파이썬이 제공하는 list 자료형과 동일한 출력 형태

            # list_from_result[index][0]=과목명
            # list_from_result[index][1]=담당교수
            # list_from_result[index][2]=시간 리스트
            if len(list_from_result)==0:
                print("해당 과목명과 일치하는 수업이 존재하지 않습니다.")
            else:
                print("[",lecture_name,"] 검색 결과:", sep='')
                for index in range(len(list_from_result)): #list_from_result: 같은 이름 다른 수업명 리스트
                    time_1=list_from_result[index][2].split('[') #time_1[0]: 첫 번째 시간
                    #시간표가 시간[강의실] 시간[강의실]의 형태인 경우 parsing_1=['시간', '강의실] 시간', '강의실]'] 꼴

                    try:
                        time_2=time_1[1].split(']') #time_2[-1]: 두 번째 시간
                    except ValueError: #두 번째 시간 없을 때 time_2는 공백란
                        time_2=''

                    time=time_1[0]+time_2[-1] #첫 번째 시간 + 두 번째 시간
                    del list_from_result[index][2] #'시간+[강의실]'에서 '첫 번째 시간 + 두 번째 시간'으로 보이도록 변경
                    list_from_result[index].append(time) #'첫 번째 시간 + 두 번째 시간' 리스트에 추가

                    print(index+1,":",list_from_result[index][1],"교수님 -",list_from_result[index][2]) #'순번 : 000 교수님 - 시간' 형태로 출력
                print()

            while(True):
                print("*과목을 잘못 선택하였을 경우 0을 입력해주세요.")
                choose_lecture_num=input("해당하는 과목의 순번 입력 >> ")  # 수업명이 겹치는 경우가 꽤 있으므로 시간대를 고름
                print()
                try:  # 중첩이 어지간히 된 함수로구먼.
                    choose_lecture_num=int(choose_lecture_num) # 정수형으로 바꿀 수 있으면 바꾸기
                except ValueError:
                    print("숫자를 기입해주세요.")
                    print()
                    continue

                if choose_lecture_num == 0:
                    deleting_course_list.append(lecture_name) #나중에 삭제할 수 있도록 리스트에 저장
                    deleting_professor_list.append(professor)
                    break
                elif 1 <= choose_lecture_num and choose_lecture_num <= len(list_from_result):
                    lecture_time=list_from_result[choose_lecture_num-1][2] #lecture_time: 찾은 과목의 시간을 저장
                    self.__schedule_list[lecture_name]=lecture_time #스케줄 딕셔너리에 과목명:(요일과 시간 구분x)시간 형태로 입력
                    break
                else:
                    print("순번에 맞게 입력해주세요.")
                    print()

        for course in deleting_course_list:
            del self.__course_list[course] #deleting_course_list에 저장하였던 교과목 딕셔너리에서 삭제
            self.course_name_for_DB.remove(course) #DB용 리스트에서도 삭제
        for professor in deleting_professor_list:
            self.professor_for_DB.remove(professor) #DB용 리스트에서 교수님 성함 삭제

        self._convert_to_timeline()

#아래 함수 for문, if문, try문이 너무 중첩되어 있으므로 정리할 것
    def _convert_to_timeline(self): #수강하는 과목을 요일과 n교시로 나누어 01교시=09:00와 같이 저장
        for lecture_name, lecture_time in self.__schedule_list.items():
            number_of_lecture=lecture_time.split('  ') #공백이 최소 2번 이상 나온 후 다른 요일의 수업 표시하므로 split

            try: #수업을 1주일에 두 번 하는 경우 대비
                # 첫 번째 수업=number_of_lecture[0]
                number_of_lecture[0]=number_of_lecture[0].strip()
                day_of_first_lecture = number_of_lecture[0][0]  # 첫 번째 강의의 요일 가져오기
                time_of_first_lecture = number_of_lecture[0][1:]  # 첫 번째 강의의 시간 리스트 가져오기 (ex: 01 ,02 ,03 ,04 ,05)
                each_time_of_first_lecture = time_of_first_lecture.split(' ,')  # 첫 번째 강의의 시간 개별로 가져오기

                for index, time_num in enumerate(each_time_of_first_lecture):  # time_num 예시: 01, 02, 10 등의 문자열
                    if time_num[0] == '0':
                        time_num = time_num[1:]  # 02 >> 2와 같이 변경
                    time_num = int(time_num)
                    each_time_of_first_lecture[index] = time_num  # 정수형으로 저장(__time의 인덱스로 사용하기 위함)

                # 두 번째 수업=number_of_lecture[1]
                number_of_lecture[1] = number_of_lecture[1].strip()
                day_of_second_lecture = number_of_lecture[1][0]  # 두 번째 강의의 요일 가져오기
                time_of_second_lecture=number_of_lecture[1][1:]  # 두 번째 강의의 시간 리스트 가져오기
                each_time_of_second_lecture = time_of_second_lecture.split(' ,')  # 두 번째 강의의 시간 개별로 가져오기

                for index, time_num in enumerate(each_time_of_second_lecture):  # time_num 예시: 01, 02, 10 등의 문자열
                    if time_num[0] == '0':
                        time_num = time_num[1:] #02 >> 2와 같이 변경
                    time_num = int(time_num)
                    each_time_of_second_lecture[index] = time_num #정수형으로 저장(__time의 인덱스로 사용하기 위함)

            except IndexError: #1주일에 1번 하는 수업에 대해서는 공백 처리
                day_of_second_lecture=''
                each_time_of_second_lecture=[]

# 시간 순으로 요일별 리스트에 강의 넣기
            #day_of_first_lecture와 day_of_second_lecture은 각각 164, 176 줄에 선언되었음 (try문 안에 선언되어서 'local variable might be referenced before assignment' 뜸)
            if day_of_second_lecture=='': #1주일에 1번 하는 수업
                self._place_in_order(lecture_name,day_of_first_lecture,self.__time[each_time_of_first_lecture[0]-1],self.__time[each_time_of_first_lecture[-1]])

            else: #1주일에 2번 하는 수업
                self._place_in_order(lecture_name, day_of_first_lecture, self.__time[each_time_of_first_lecture[0] - 1],self.__time[each_time_of_first_lecture[-1]])
                self._place_in_order(lecture_name,day_of_second_lecture,self.__time[each_time_of_second_lecture[0]-1],self.__time[each_time_of_second_lecture[-1]])

# 시작 시간 비교해서 빠른 순으로 리스트에 삽입
    def _place_in_order(self, lecture_name, lecture_day, lecture_start_time, lecture_finish_time):
        clock_lecture_start_time = datetime.datetime.strptime(lecture_start_time,"%H:%M")  # 시계 형태로 시작 시간 표시
        new_lecture_info = [lecture_name, lecture_start_time, lecture_finish_time]  # ex) [선형대수학, 09:00, 10:00] (시간은 문자열)

        day_number=self.__days.index(lecture_day)  # 해당 강의의 요일을 숫자로 환산

        if not self.lectures_sorted_by_week[day_number]:  # 리스트가 비어있을 때 (처음으로 과목 정보를 리스트에 넣을 때)
            self.lectures_sorted_by_week[day_number].append(list(new_lecture_info))
            return  # 삽입 완료

        for index, lecture in enumerate(self.lectures_sorted_by_week[day_number]):  # https://pythonq.com/so/python/1591378
            time=lecture[1]  # __lectures_sorted_by_week의 기존에 있던 강의의 시작 시간
            compare_start_time = datetime.datetime.strptime(time, "%H:%M")  # lectures_sorted_by_week 리스트에 있는 강의들의 시작 시간을 시:분 형태로 가져옴

            if (clock_lecture_start_time-compare_start_time).days == -1:   # insert_starting_lecture_time(리스트에 새로 넣으려는 과목의 시간)이 리스트에 있던 A 과목의 시간보다 먼저일 때
                self.lectures_sorted_by_week[day_number].insert(index,list(new_lecture_info))  # A 과목의 인덱스에 새로운 과목 정보 new_info를 넣을 것
                return  # 삽입 완료

        self.lectures_sorted_by_week[day_number].append(new_lecture_info)  # 새로 넣으려는 과목의 시간이 맨 마지막일 때 리스트의 끝에 삽입



