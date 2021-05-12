from selenium import webdriver
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome('') #본인 컴퓨터에서 chromedrive가 있는 경로 입력
#driver = webdriver.Chrome('/Users/이승현/chromedriver/chromedriver') #본인 컴퓨터에서 chromedrive가 있는 경로 입력
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')

# 로그인
driver.get('https://cbnu.blackboard.com/')
driver.find_element_by_name('uid').send_keys('') #학번 작성
driver.find_element_by_name('pswd').send_keys('') #Blackboard 비밀번호 작성
driver.find_element_by_xpath('//*[@id="entry-login"]').click()

driver.get('https://cbnu.blackboard.com/ultra/course')

# 내가 원하는 element가 load 될때까지 기다리기
try:
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'course-title')))
finally:
    pass

soup = bs(driver.page_source, 'html.parser')

driver.implicitly_wait(3)

print("종료하려면 Q 입력")
print("개신누리 기준으로 띄어쓰기 포함하여 정확히 입력할 것")
print("추후 개신누리에서 과목 리스트 웹크롤링하기")
#subject_list=["객체지향 프로그래밍", "기초통계학", "나무문화그리고환경", "미래설계구현", "선형대수학", "소프트웨어실전영어", "오픈소스기초프로젝트", "자료구조", "컴퓨터구조"]
subject_list=["기초통계학"]
#while True:
#    subject_name=input("과목명 입력 >> ")
#    if subject_name == 'Q':
#        break
#    subject_list.append(subject_name)


course_list=[]
for subject in subject_list:
    course=driver.find_element_by_partial_link_text(subject)
    if course is not None:
        course_list.append(course)

#course_list = soup.find_all('a', {'class':'course-title'})

for course in course_list:
    course.click()
    driver.switch_to.frame('classic-learn-iframe')

    # 내가 원하는 element가 load 될때까지 기다리기
    try:
        course = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'button-6')))
    finally:
        pass
    notice = driver.find_element_by_class_name('button-6') #'나의 공지 사항' 란의 '더보기' 버튼
    notice.click()

    try:
        course = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'pageTitleText'))) #공지 사항 페이지에서 페이지의 제목 '공지 사항'의 id인 pageTitleText
    finally:
        pass
    try:
        zoom = driver.find_element_by_partial_link_text('https://zoom.us') #zoom 링크가 있을 때 'https://zoom.us' 텍스트를 가진 최상단의 링크 클릭하기
    except NoSuchElementException:
        pass
    finally:
        print("실시간 수업 링크로 연결") #실행 확인 문구 (나중에 수정)
