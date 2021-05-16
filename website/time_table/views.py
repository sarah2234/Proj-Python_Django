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
from datetime import datetime
import calendar

from .models import Data, TimeTable
import re

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


date_list = ['월', '화', '수', '목', '금', '토', '일']


def table(request):
    """
    Data 목록 출력
    """
    data_list = Data.objects.order_by('context_ellipsis')
    context = {'data_list': data_list}
    return render(request, 'time_table/load_data.html', context)


def schedule(request):
    now = datetime.now()
    date = date_list[datetime.today().weekday()]

    data_list = Data.objects.filter(sort='과제')
    today_data = Data.objects.filter(sort='과제', year=now.year, month=now.month, day=now.day)

    # 오늘 날짜 시간표 불러오기
    today_class = TimeTable.objects.filter(date=date)

    # 시간표에 들어갈 시간들
    time_list = ["09", "10", "11", "12", "13", "14", "15", "16", "17"]
    weekday = ['월', '화', '수', '목', '금']
    # 시간별로 묶어서 저장
    time_table = []
    for time in time_list:
        # 요일별로 묶어서 저장
        sametime = []
        for date in weekday:
            temp = TimeTable.objects.filter(start_h__lte=int(time), end_h__gte=int(time), date=date)
            if temp:
                sametime.append(temp)
            else:
                sametime.append('empty')
        time_table.append({time: sametime})  # 시간이랑 요일별로 묶어서 저장한거 딕셔너리로 함께 저장

    context = {'data_list': data_list, 'now': now, 'date': date,
               'today_data': today_data, 'today_class': today_class,
               'time_table': time_table}

    return render(request, 'template.html', context)


def list_schedule(request):
    now = datetime.now()
    date = date_list[datetime.today().weekday()]

    data_list = Data.objects.filter(sort='과제')
    today_data = Data.objects.filter(sort='과제', year=now.year, month=now.month, day=now.day)

    # 오늘 날짜 시간표 불러오기
    today_class = TimeTable.objects.filter(date=date)
    context = {'data_list': data_list, 'now': now, 'date': date,
               'today_data': today_data, 'today_class': today_class}
    return render(request, 'time_table/list_schedule.html', context)


def weekly_schedule(request):
    # 예시 데이터셋
    # TimeTable(prof='강재구', subject='오픈소스', date='목', start_h='13', end_h='15').save()
    # TimeTable(prof='노서영', subject='선형대수학', date='수', start_h='09', end_h='11').save()

    # 시간표에 들어갈 시간들
    time_list = ["09", "10", "11", "12", "13", "14", "15", "16", "17"]
    weekday = ['월', '화', '수', '목', '금']
    # 시간별로 묶어서 저장
    time_table = []
    for time in time_list:
        # 요일별로 묶어서 저장
        sametime = []
        for date in weekday:
            temp = TimeTable.objects.filter(start_h__lte=int(time), end_h__gte=int(time), date=date)
            if temp:
                sametime.append(temp)
            else:
                sametime.append('empty')
        time_table.append({time: sametime})  # 시간이랑 요일별로 묶어서 저장한거 딕셔너리로 함께 저장
    context = {'time_table': time_table}

    return render(request, 'time_table/weekly_schedule.html', context)


def crawling(request):
    if request.method == "GET":
        return render(request, 'load_data.html')
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
                            year = "".join(["20", contents[1]])
                            month = contents[2]
                            day = contents[3]
                            date = date_list[calendar.weekday(int("".join(["20", contents[1]])),
                                                              int(contents[2]), int(contents[3]))]
                            time = contents[4].split(':')
                            hour = time[0]
                            minute = time[1]
                    else:
                        content = details.find('div', class_="content").text.strip()

                    #       due_date = details.find('div', class_="due-date").text.strip()
                    #       summary = details.find('div', class_="content").text.strip()

                    # 중복된 데이터는 DB에 저장하지 않는다.
                    if Data.objects.filter(sort=sort, context_ellipsis=context_ellipsis, name=name,
                                           content=content).count() == 0:
                        Data(sort=sort, context_ellipsis=context_ellipsis, name=name,
                             content=content, year=year, month=month, day=day,
                             date=date, hour=hour, minute=minute).save()

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

                    # content - 성적 출력 최적화
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
                                year = "".join(["20", contents[1]])
                                month = contents[2]
                                day = contents[3]
                                date = date_list[calendar.weekday(int("".join(["20", contents[1]])),
                                                                  int(contents[2]), int(contents[3]))]
                                time = contents[4].split(':')
                                hour = time[0]
                                minute = time[1]
                        else:
                            content = details.find('div', class_="content").text.strip()

                        #       due_date = details.find('div', class_="due-date").text.strip()
                        #       summary = details.find('div', class_="content").text.strip()

                        # 중복된 데이터는 DB에 저장하지 않는다.
                        if Data.objects.filter(sort=sort, context_ellipsis=context_ellipsis, name=name,
                                               content=content).count() == 0:
                            Data(sort=sort, context_ellipsis=context_ellipsis, name=name,
                                 content=content, year=year, month=month, day=day,
                                 date=date, hour=hour, minute=minute).save()

    return redirect('time_table:table')
