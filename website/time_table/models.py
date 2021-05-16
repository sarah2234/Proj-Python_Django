from django.db import models


# 블랙보드 Stream에서 읽어온 값들을 정리할 클래스
class Data(models.Model):
    sort = models.CharField(max_length=20)  # 종류(공지사항, 과제, ..)
    context_ellipsis = models.TextField()  # 과목
    name = models.TextField()  # 제목
    content = models.TextField()  # 내용
    # time = models.DateTimeField(input_formats=["%Y년 %m월 %d일 %A %H:%M"])  # 마감기한
    year = models.CharField(max_length=10, default='년')
    month = models.CharField(max_length=10, default='월')
    day = models.CharField(max_length=10, default='일')
    date = models.CharField(max_length=10, default='요일')
    hour = models.CharField(max_length=10, default='시')
    minute = models.CharField(max_length=10, default='분')

    def __str__(self):
        return self.context_ellipsis + " " + self.sort
