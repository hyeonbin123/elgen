from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


# Create your models here.

class User(models.Model):
    #username = None
    user_id = models.CharField(unique=True, max_length=20) #사용자 아이디
    user_name = models.CharField(max_length=10) #사용자 이름
    password = models.TextField() #비밀번호
    c_code = models.CharField(max_length=30)  # 회사코드
    d_code = models.CharField(null=True, max_length=30) #부서코드
    request_admin = models.CharField(default='N', max_length=10) # 일반회원, 전사알바생, 관리자 구분해서 요청받음
    is_admin = models.CharField(default='N', max_length=10) #위의 요청에 따라 다른 권한을 줌
    registered_at = models.DateField(auto_now_add=True) #가입일

    #objects = UserManager()

    #REQUIRED_FILEDS = []
    #USERNAME_FIELD = 'user_id'
    #def __str__(self):
    #    return self.user_id

    # DB 테이블 이름 설정
    class Meta:
        db_table = "user"
        #verbose_name = "사용자"
        #verbose_name_plural = "사용자"


class Company(models.Model):
    c_code = models.CharField(primary_key=True, unique=True, max_length=30)
    c_name = models.CharField(unique=True, max_length=30)
    order = models.PositiveIntegerField(null=True)

    class Meta:
        db_table = "company"


class Department(models.Model):
    d_code = models.CharField(primary_key=True, unique=True, max_length=30)
    d_name = models.CharField(unique=True, max_length=30)

    class Meta:
        db_table = "department"
