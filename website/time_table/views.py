from django.shortcuts import render

# Create your views here.
# requests(속도가 빠르다), selenium(동적 웹페이지 수집가능, 쉬운 login)
# import requests
from selenium import webdriver
# html 코드를 Python이 이해하는 객체 구조로 변환하는 Parsing 수행
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websaver.settings")
import django
django.setup()

from django.shortcuts import render, redirect

from . models import Data




# 창 띄우지 않는 설정. background에서 동작.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

# chrome driver를 불러오고 위의 option을 적용시킴
# driver = webdriver.Chrome()  # 본인 컴퓨터에서 chromedrive가 있는 경로 입력
# 입력예시
driver = webdriver.Chrome(
   '/Users/chisanahn/Desktop/Python_Project/chromedriver.exe',
   chrome_options=options)


def table(request):
    """
    Data 목록 출력
    """
    data_list = Data.objects.order_by('context_ellipsis')
    context = {'data_list': data_list}
    return render(request, 'time_table/data_list.html', context)


def crawling(request):
    if request.method == "GET":
        return render(request, 'data_list.html')
    elif request.method == "POST":
        # 로그인
        driver.get('https://cbnu.blackboard.com/')
        driver.find_element_by_name('uid').send_keys(request.POST['uid'])  # 학번 작성
        driver.find_element_by_name('pswd').send_keys(request.POST['pswd'])  # Blackboard 비밀번호 작성
        driver.find_element_by_xpath('//*[@id="entry-login"]').click()

        driver.get('https://cbnu.blackboard.com/ultra/stream')

        # 내가 원하는 element가 load 될때까지 기다리기
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "activity-feed")))  # 이걸 원하는 내용으로 바꿨더니 로딩이 된다!!!!
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
        if upcoming != None:
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

                    # 중복된 데이터는 DB에 저장하지 않는다.
                    if Data.objects.filter(sort=sort, context_ellipsis=context_ellipsis, name=name,
                                           content=content).count() == 0:
                        Data(sort=sort, context_ellipsis=context_ellipsis, name=name,
                             content=content).save()

        # 오늘
        if today != None:
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

                    # 중복된 데이터는 DB에 저장하지 않는다.
                    if Data.objects.filter(sort=sort, context_ellipsis=context_ellipsis, name=name,
                                           content=content).count() == 0:
                        Data(sort=sort, context_ellipsis=context_ellipsis, name=name,
                             content=content).save()

    return redirect('time_table:table')
