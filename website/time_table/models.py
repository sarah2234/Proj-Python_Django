from django.db import models


# 시간표, 과제, 개인일정 같은 DB로 통합
class Data(models.Model):
    sort = models.CharField(max_length=20)  # 종류(시간표, 과제, 개인일정)
    name = models.TextField()               # 교수님, 제목, 제목
    context = models.TextField()            # 과목, 과목, 내용
    content = models.TextField()            # 요일, 내용, 요일
    time = models.DateTimeField(null=True)  # null, 마감일, 일정시간
    start_h = models.IntegerField(null=True)         # 시작시간, null, 시작시간
    end_h = models.IntegerField(null=True)           # 시작시간, null, 시작시간

    def __str__(self):
        return self.sort + " " + self.name + " " + self.context


# 비교과 활동 저장할 모델
class Activity(models.Model):
    name = models.TextField()  # 활동명
    registration_date = models.TextField()  # 모집기간
    activity_date = models.TextField()  # 활동기간
    department = models.TextField()  # 운영부서

    def __str__(self):
        return self.name

# # 블랙보드 Stream에서 읽어온 값들 저장할 모델 - 과제에 초점이 맞춰져 있음
# class Data(models.Model):
#     sort = models.CharField(max_length=20)  # 종류(공지사항, 과제, ..)
#     context_ellipsis = models.TextField()  # 과목
#     name = models.TextField()  # 제목
#     content = models.TextField()  # 내용
#     time = models.DateTimeField(null=True)
#
#     def __str__(self):
#         return self.context_ellipsis + " " + self.sort
#
#
# # 수업 시간표 저장할 모델
# class TimeTable(models.Model):
#     prof = models.TextField()  # 교수님
#     subject = models.TextField()  # 과목명
#     date = models.CharField(max_length=10, default='요일')
#     start_h = models.IntegerField()
#     end_h = models.IntegerField()
#
#     def __str__(self):
#         return self.subject + " - " + self.prof
#
#

