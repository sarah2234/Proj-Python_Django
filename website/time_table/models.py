from django.db import models


# 블랙보드 Stream에서 읽어온 값들을 정리할 클래스
class Data(models.Model):
    sort = models.CharField(max_length=20)  # 종류(공지사항, 과제, ..)
    context_ellipsis = models.TextField()  # 과목
    name = models.TextField()  # 제목
    content = models.TextField()  # 내용

    def __str__(self):
        return self.context_ellipsis + " " + self.sort
