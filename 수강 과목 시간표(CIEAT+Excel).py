from selenium import webdriver
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

import pandas as pd #엑셀을 다루는 라이브러리 pandas

pd.options.display.max_rows=22 # 데이터 프레임 표시 최대 열수를 22로 지정
pd.set_option('display.max_columns',3668) # 데이터 프레임 표시 최대 행수를 3668로 지정


# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

def get_schedule(): #개신누리에서 엑셀 파일 다운 받아서 전체 강좌의 시간표 확인
    lectures_info=pd.read_excel('./개설강좌(계획서)조회.xlsx', #상대참조(같은 디렉터리 내에 엑셀 파일 있다고 가정)
                                header=0, #칼럼이 시작하는 곳
                                dtype={'순번':str,
                                       '과목명':str, #각 칼럼의 자료형
                                       '담당교수':str,
                                       '수업시간':str},
                                index_col='순번', #'순번'을 index로 사용
                                nrows=3668) #총 읽어올 열의 개수

    lectures_time=lectures_info.loc[:,['과목명','담당교수','수업시간']] #loc으로 엑셀에서 '과목명', '담당교수', '수업시간'의 열만 추출, 앞의 :는 행 부분
    # print(lectures_time) #전체 강의 목록 (테스트용으로 전체 강의 목록을 출력할 때는 nrows의 수를 줄여서 할 것)

    input_subject=input("과목이름 입력 >> ") #추후 씨앗의 마이페이지로 과목명 입력 없이 할 것
    searching_lecture=lectures_time[lectures_time['과목명']==input_subject] #입력받은 과목명과 일치하는 행 선별, lectures_time[]으로 유효한 값을 가지는 행만 추출
    result=searching_lecture['수업시간'] #searching_lecture의 '수업시간' 열을 result에 저장 (순번은 왜 자꾸 출력되는 거지?)
    print(result)

    input_index=int(input("해당하는 번째 입력(0부터 시작) >> ")) #수업명이 겹치는 경우가 꽤 있으므로 시간대를 고름 (순번 무시)
    result_2=result.iloc[input_index] #iloc: [] 안의 인덱스를 가지는 행 추출
    print(result_2) #사용자가 찾고자하는 과목의 시간대 발견



# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome('/Users/이승현/chromedriver/chromedriver') #본인 컴퓨터에서 chromedrive가 있는 경로 입력
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')

def get_subject_name(): #CIEAT의 마이페이지에서 과목명 가져오기
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, '교과 이수 현황'))) #마이페이지 내 교과 이수 현황
    finally:
        pass
    course_list=[]
    driver.find_element_by_class_name('section_sarea tbl tbl_col scrollx_tbl_md').find_element_by_tag_name('tbody')

# 로그인
driver.get('https://cieat.chungbuk.ac.kr/clientMain/a/t/main.do')
driver.find_element_by_class_name('btn_login').click() #CIEAT 로그인 버튼
try:
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'loginForm')))
finally:
    pass
driver.find_element_by_name('userId').send_keys('') #학번 작성
driver.find_element_by_name('userPw').send_keys('') #비밀번호 작성
driver.find_element_by_class_name('btn_login_submit').click()

try:
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, '마이페이지'))) #CIEAT의 마이페이지
finally:
    pass


