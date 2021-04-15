# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 02:36:03 2021

@author: chisanahn
"""

# Stream에서 읽어온 값들을 정리할 클래스
class Data:
    def __init__(self, sort, context_ellipsis, name, content):    # due-date, summary는 content 안에 속해 있음. 나중에 시간이 되면 분류해서 넣기.
        self.sort = sort
        self.context_ellipsis = context_ellipsis
        self.name = name
        self.content = content

    def show(self):RRrrruuuuuuuuuuuuuUUUUUUUiiddd::wq::::::
        print("-----------------\n" +
              "종류| " + self.sort +
              "\n과목| " + self.context_ellipsis +
              "\n제목| " + self.name +
              "\n내용| " + self.content)


# requests(속도가 빠르다), selenium(동적 웹페이지 수집가능, 쉬운 login)
# import requests
from selenium import webdriver

# html 코드를 Python이 이해하는 객체 구조로 변환하는 Parsing 수행
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
driver = webdriver.Chrome(
    '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe',
    chrome_options=options)
# driver = webdriver.Chrome(
#     '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe')

# 로그인
driver.get('https://cbnu.blackboard.com/')
driver.find_element_by_name('uid').send_keys('학번')
driver.find_element_by_name('pswd').send_keys('블랙보드 비밀번호')
driver.find_element_by_xpath('//*[@id="entry-login"]').click()

# 활동 스트림에서 원하는 정보 받아오기 - div id site-wrap 다음 부분부터는 안 읽히는데 나머지 부분은 동적이라서 값을 못 읽어오는 것 같다.
# 활동 스트림은 수시로 값이 바뀌는 곳이라 동적으로 설정되어 있는 것 같다. 과목별 항목으로 이동해서 각각의 값을 읽어오는 게 더 좋으려나...
# 동적이더라도 selenium으로 동적으로 읽어와서 bs에 넘겨주면 제대로 읽어와야 하는데 왜 동작하지 않지..
# 로딩 될때까지 기다렸더니 로딩이 된다!!!!!
# 와 근데 읽어오는데 시간이 좀 너무 오래걸리는것 같다.

driver.get('https://cbnu.blackboard.com/ultra/stream')

# 내가 원하는 element가 load 될때까지 기다리기
try:
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "activity-feed"))) # 이걸 원하는 내용으로 바꿨더니 로딩이 된다!!!!
finally:
    pass

# BeautifulSoup으로 html소스를 python객체로 변환하기
# 첫 인자는 html 소스코드, 두 번째 인자는 어떤 parser를 이용할지 명시.
# Python 내장 html.parser
soup = bs(driver.page_source, 'html.parser')

# select - CSS Selector를 이용해 조건과 일치하는 모든 객체들을 List로 반환

soup = soup.find('div', class_="activity-stream row collapse")

upcoming = soup.find('div', class_="js-upcomingStreamEntries activity-group columns main-column").find('ul', class_="activity-feed")
# 왜 읽어오지 못하나 했더니 today는 비어있을 때도 있다.
today = soup.find('div', class_="js-todayStreamEntries activity-group columns main-column").find('ul', class_="activity-feed")
# previous = soup.find('div', class_="js-previousStreamEntries activity-group columns main-column")

# icon의 종류가 달라서 종류에 맞게 정보를 읽어올수있도록
icon_list = ["bb-ui-icon-grades", "bb-ui-icon-test", "bb-ui-icon-assignment",
             "bb-ui-icon-announcement", "bb-ui-icon-pdf", "bb-ui-icon-document",
             "bb-ui-icon-video"]

# 제공 예정
upcoming_feed = []
element_cards = upcoming.find_all(class_='element-card')
if element_cards is not None:
    for element_card in element_cards:

        # sort - 종류(과제, 공지, 성적..)
        sort = "찾을 수 없음"
        for icon in icon_list:
            find_result = element_card.find(icon)
            if find_result is not None:
                sort = find_result.attrs.get('title-access')

        details = element_card.find('div', class_="element-details")
        context_ellipsis = details.find('div', class_="context ellipsis").text.strip()
        name = details.find('div', class_="name").text.strip()

        # content - 성적 출력 최적화
        IsItGrade = element_card.find("bb-ui-icon-grades")
        if IsItGrade is not None:
            contents = details.find('div', class_="content").text.strip().split()
            if contents != []:
                content = "".join(["내 성적 - ", contents[3], contents[4]])
        else:
            content = details.find('div', class_="content").text.strip()

#       due_date = details.find('div', class_="due-date").text.strip()
#       summary = details.find('div', class_="content").text.strip()
        upcoming_feed.append(Data(sort, context_ellipsis, name, content))

    print("Upcoming Stream\n")
    for item in upcoming_feed:
        item.show()


# 오늘
today_feed = []
element_cards = today.find_all(class_='element-card')
if element_cards is not None:
    for element_card in element_cards:

        # sort - 종류(과제, 공지, 성적..)
        sort = "찾을 수 없음"
        for icon in icon_list:
            find_result = element_card.find(icon)
            if find_result is not None:
                sort = find_result.attrs.get('title-access')

        details = element_card.find('div', class_="element-details")
        context_ellipsis = details.find('div', class_="context ellipsis").text.strip()
        name = details.find('div', class_="name").text.strip()

        # content - 성적 출력 최적화
        IsItGrade = element_card.find("bb-ui-icon-grades")
        if IsItGrade is not None:
            contents = details.find('div', class_="content").text.strip().split()
            if contents != []:
                content = "".join(["내 성적 - ", contents[3], contents[4]])
        else:
            content = details.find('div', class_="content").text.strip()

#       due_date = details.find('div', class_="due-date").text.strip()
#       summary = details.find('div', class_="content").text.strip()
        today_feed.append(Data(sort, context_ellipsis, name, content))

    print("\nToday Stream\n")
    for item in today_feed:
        item.show()

