# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 02:36:03 2021

@author: chisanahn
"""

# requests(속도가 빠르다), selenium(동적 웹페이지 수집가능, 쉬운 login)
# import requests
from selenium import webdriver

# html 코드를 Python이 이해하는 객체 구조로 변환하는 Parsing 수행
from bs4 import BeautifulSoup

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

# 로그인
driver.get('https://cbnu.blackboard.com/')
driver.find_element_by_name('uid').send_keys('블랙보드 아이디')
driver.find_element_by_name('pswd').send_keys('블랙보드 패스워드')
driver.find_element_by_xpath('//*[@id="entry-login"]').click()

# 활동 스트림에서 원하는 정보 받아오기 - div id site-wrap 다음 부분부터는 안 읽히는데 나머지 부분은 동적이라서 값을 못 읽어오는 것 같다.
# 활동 스트림은 수시로 값이 바뀌는 곳이라 동적으로 설정되어 있는 것 같다. 과목별 항목으로 이동해서 각각의 값을 읽어오는 게 더 좋으려나...
# 동적이더라도 selenium으로 동적으로 읽어와서 bs에 넘겨주면 제대로 읽어와야 하는데 왜 동작하지 않지..
# 로딩 될때까지 기다렸더니 로딩이 된다!!!!!

driver.get('https://cbnu.blackboard.com/ultra/stream')

# 내가 원하는 element가 load 될때까지 기다리기
try:
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "activity-group-title"))) # 이걸 원하는 내용으로 바꿨더니 로딩이 된다!!!!
finally:
    pass

# BeautifulSoup으로 html소스를 python객체로 변환하기
# 첫 인자는 html 소스코드, 두 번째 인자는 어떤 parser를 이용할지 명시.
# Python 내장 html.parser
soup = bs(driver.page_source, 'html.parser')
soup = soup.find('body')
soup = soup.find('div', class_="activity-stream row collapse")
print(soup.find('h2', class_="activity-group-title").text)

# select - CSS Selector를 이용해 조건과 일치하는 모든 객체들을 List로 반환