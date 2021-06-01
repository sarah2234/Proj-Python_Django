from django.db import models
from django.contrib.auth.models import User


# 시간표, 과제, 개인일정 같은 DB로 통합
class Data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sort = models.CharField(max_length=20)  # 종류(시간표, 과제, 개인일정)
    name = models.TextField()               # 교수님, 제목, 제목
    context = models.TextField()            # 과목, 과목, 내용
    content = models.TextField()            # 요일, 내용, 요일
    time = models.DateTimeField(null=True)  # null, 마감일, 일정시간
    start_h = models.IntegerField(null=True)         # 시작시간, null, 시작시간
    end_h = models.IntegerField(null=True)           # 끝시간, null, 끝시간
    # start_m = models.IntegerField(null=True)         # 시작시간, null, 시작시간
    # end_m = models.IntegerField(null=True)           # 시작시간, null, 시작시간
    valid = models.IntegerField(default=1)  # 제출 기한 전에 완료한 과제 표시하지 않기

    def __str__(self):
        return self.sort + " " + self.name + " " + self.context


# 비교과 활동 저장할 모델
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.TextField()  # 활동명
    registration_date = models.TextField()  # 모집기간
    activity_date = models.TextField()  # 활동기간
    department = models.TextField()  # 운영부서

    def __str__(self):
        return self.name

