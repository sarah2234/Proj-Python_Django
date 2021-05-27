from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
import pandas as pd #엑셀을 다루는 라이브러리 pandas

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
    __course_list={} #현재 수강 중인 과목의 이름과 교수님 목록 (과목명:교수님 형태) >> 엑셀 파일에서 과목 선별하기 위한 변수

    __time=['09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00','24:00'] #오전 09시 ~ 오전 00시
    __days = ['월', '화', '수', '목', '금', '토', '일']

    list_for_DB=[]  # DB용 리스트 ([교수님, 과목명, [월, 09:00, 10:00], [화, 09:00, 10:00]]와 같이 한 리스트로 묶어서 저장됨)

    def __init__(self):
########################################################################################################################
        self.login_error=1  # 학번이나 비밀번호 제대로 기입하면 0

        while self.login_error==1:
            self.id = input('학번을 입력하세요: ')
            self.password = input('비밀번호를 입력하세요: ')
########################################################################################################################
            driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')  # 씨앗 주소
            driver.find_element_by_class_name('btn_login').click()  # CIEAT 로그인 버튼
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'loginForm')))

########################################################################################################################
            try:
########################################################################################################################
                driver.find_element_by_name('userId').send_keys(self.id)  # 입력받은 학번으로 로그인
                driver.find_element_by_name('userPw').send_keys(self.password)  # 입력받은 비밀번호로 로그인
                driver.find_element_by_class_name('btn_login_submit').click()
                self.login_error=0  # 로그인 성공
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_skip"]/ul/li[9]/ul')))  # 마이페이지 xpath
                try:
                    element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="mileageRcrHistList"]/div')))  # 마이페이지 내 교과 이수 현황
                except UnexpectedAlertPresentException:
                    return  # 아이디와 비밀번호를 웹 크롤러로 잘못 입력받았을 때 뜨는 페이지 (혹은 아주 가끔 서버 다운 있음)

                major = driver.find_element_by_xpath(
                    '//*[@id="container_skip"]/div/section[1]/div/table/tbody/tr[1]/td[1]').text.strip()  # 마이페이지의 학과/학부 텍스트
                self.major = major[:-2]  # '학과' 또는 '학부' 삭제

                major_sub = driver.find_element_by_xpath(
                    '//*[@id="container_skip"]/div/section[1]/div/table/tbody/tr[1]/td[2]').text.strip()  # 마이페이지의 부전공/복수전공 텍스트
                major_sub = major_sub[6:]
                major_sub = major_sub.split("복수전공 : ")
                self.major_sub = major_sub[0].rstrip()  # 복수전공이나 부전공을 안 해서 씨앗에서 어떻게 표시되는지 잘 모르겠음...
                self.major_multiple = major_sub[1].rstrip()
########################################################################################################################
            except UnexpectedAlertPresentException:  # 유저 정보 오기입
                print("학번과 비밀번호를 확인해주십시오.")
                print()
########################################################################################################################
        self._get_subject_name()

    def _get_subject_name(self):  # CIEAT의 마이페이지에서 과목명 가져오기
        driver.get('https://cieat.chungbuk.ac.kr/mileageHis/a/m/goMileageHisList.do')  # 마이페이지 주소
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="mileageRcrHistList"]/div')))  # 마이페이지 내 교과 이수 현황

        tbody = driver.find_element_by_xpath('//*[@id="mileageRcrHistList"]/div').find_element_by_tag_name(
            'tbody')  # 교과 이수 현황 테이블
        rows = tbody.find_elements_by_tag_name('tr')  # 행 별로 저장
        try:
            for index, value in enumerate(rows):
                lecture = value.find_elements_by_tag_name('td')[3]  # 과목명 (rows의 3번째 열에 해당)
                professor = value.find_elements_by_tag_name('td')[5]  # 교수님 (rows의 5번째 열에 해당)
                self.__course_list[lecture.text.strip()] = professor.text.strip()  # course_list에 '과목명: 교수님' 추가
        except IndexError:
            return #5.28 3:44시경 CIEAT에서 교과 이수 현황이 출력되지 않는 문제(CIEAT의 문제라 달리 해결할 방도가 없음)

    def get_schedule(self): #개신누리에서 엑셀 파일 다운 받아서 전체 강좌의 시간표 확인, CIEAT 내 교과목 이수 현황의 교과목+교수님과 일치하는 과목 전부 가져옴(중복 가능성 존재)

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

            if len(list_from_result)==0:  # 해당 교과목이 존재하지 않는 경우
                pass  # 개신누리에서 개설강좌(계획서)조회.xlsx를 새로 다운 받야아 함!

            else:
                for index in range(len(list_from_result)): #list_from_result: 같은 이름 다른 수업명 리스트
                    split_time_with_room_info=list_from_result[index][2].split('  ')
                    time_1=split_time_with_room_info[0].split('[')
                    #case 1: 일주일에 두 번 수업하는데 시간표가 {시간[강의실] 시간[강의실]}의 형태인 경우 split_time_with_room_info=['시간[강의실]', '시간[강의실]']
                    #case 2: 일주일에 두 번 수업하는데 시간표가 {시간 시간[강의실]}의 형태인 경우 ['시간', '시간[강의실]']
                    #case 2 예시: 월08 ,09  수03[강의실]
                    #case 3: 일주일에 한 번 수업하고 시간표가 {시간[강의실]}의 형태인 경우 ['시간[강의실]']

                    time_1[0] = time_1[0].strip() #time_1[0]: 첫 번째 시간

                    day_of_first_lecture = time_1[0][0]  # 첫 번째 강의의 요일 가져오기
                    time_of_first_lecture = time_1[0][
                                            1:]  # 첫 번째 강의의 시간 리스트 가져오기 (ex: [01 ,02 ,03 ,04 ,05])
                    each_time_of_first_lecture = time_of_first_lecture.split(' ,')  # 첫 번째 강의의 시간 개별로 가져오기

                    #each_time_of_first_lecture[0]=시작하는 시간
                    #each_time_of_first_lecture[-1]=끝나는 시간

# 첫 번째 시간
                    if each_time_of_first_lecture[0][0] == '0':  # 강의 시작하는 시간의 형태가 01와 같으면 1로 수정
                        each_time_of_first_lecture[0] = each_time_of_first_lecture[0][1:]

                    lecture_start_time = self.__time[
                        int(each_time_of_first_lecture[0])]  # 강의 시작하는 시간의 형태를 정수에서 09:00와 같이 저장

                    if len(each_time_of_first_lecture) == 1:  # 한 시간짜리 강의일 때 시작하는 시간만 기록
                        time_1_organized = [day_of_first_lecture, lecture_start_time]  # [월, 09:00] 형태의 리스트

                    else:  # 두 시간 이상 강의
                        if each_time_of_first_lecture[-1][0] == '0':  # 강의 끝나는 시간의 형태가 09와 같으면 9로 수정
                            each_time_of_first_lecture[-1] = each_time_of_first_lecture[-1][1:]

                        lecture_end_time = self.__time[
                            int(each_time_of_first_lecture[-1])]  # 강의 끝나는 시간의 형태를 정수에서 09:00와 같이 저장

                        time_1_organized = [day_of_first_lecture,
                                            lecture_start_time, lecture_end_time]  # [월, 09:00, 10:00] 형태의 리스트

# 일주일에 수업을 2번하는 경우
                    try:
                        time_2=split_time_with_room_info[1].split('[')
                        time_2[0]=time_2[0].strip() #time_2[0]: 두 번째 시간
                        day_of_second_lecture = time_2[0][0]  # 두 번째 강의의 요일 가져오기
                        time_of_second_lecture = time_2[0][1:]  # 두 번째 강의의 시간 리스트 가져오기
                        each_time_of_second_lecture = time_of_second_lecture.split(' ,')  # 두 번째 강의의 시간 개별로 가져오기

                        if each_time_of_second_lecture[0][0] == '0':  # 강의 시작하는 시간의 형태가 01와 같으면 1로 수정
                            each_time_of_second_lecture[0] = each_time_of_second_lecture[0][1:]

                        lecture_start_time = self.__time[
                            int(each_time_of_second_lecture[0])]  # 강의 시작하는 시간의 형태를 정수에서 09:00와 같이 저장


                        if len(each_time_of_second_lecture) == 1: # 한 시간짜리 강의일 때
                            time_2_organized = [day_of_second_lecture, lecture_start_time]  # [월, 09:00] 형태의 리스트

                        else:  # 두 시간 이상 강의
                            if each_time_of_second_lecture[-1][0] == '0':  # 강의 끝나는 시간의 형태가 09와 같으면 9로 수정
                                each_time_of_second_lecture[-1] = each_time_of_second_lecture[-1][1:]

                            lecture_end_time = self.__time[
                                int(each_time_of_second_lecture[-1])]  # 강의 끝나는 시간의 형태를 정수에서 09:00와 같이 저장

                            time_2_organized = [day_of_second_lecture,
                                                lecture_start_time, lecture_end_time]  # [월, 09:00, 10:00] 형태의 리스트

                        self.list_for_DB.append(
                            [list_from_result[index][0], list_from_result[index][1], time_1_organized, time_2_organized])
                        # [과목명, 교수님, [월, 09:00, 10:00], [화, 09:00, 10:00]] 형태의 리스트로 DB용 리스트에 넣기
                    except IndexError:#두 번째 시간 없을 때 time_1_organized만 넣기
                        self.list_for_DB.append([list_from_result[index][0], list_from_result[index][1], time_1_organized])
                        # [과목명, 교수님, [월, 09:00, 10:00]] 형태의 리스트로 DB용 리스트에 넣기 (time_1_organized는 try문 안에 선언)