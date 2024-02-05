from dateutil.relativedelta import relativedelta
from django.db import models
from datetime import datetime

class oldPatient(models.Model):
    reg_id = models.CharField(max_length=15)  # 등록 번호
    old_patient_id = models.CharField(max_length=15)

    class Meta:
        db_table = "old_patient"

def now_plus():
    return datetime.now() + relativedelta(months=6)

class newPatient(models.Model):
    reg_id = models.CharField(unique=True, max_length=15)  # 등록 번호
    registered_at = models.DateField(auto_now_add=True, null=True)  # 등록일 #처음에는 얘 없애고 migate한다음에 값넣은후 얘 다시 넣고 migrate하기
    patient_id = models.CharField(unique=True, max_length=15, null=True)  # 환자 번호 #sequence로 자동증가해야되는데 일단 기존 있는 애들은 ...
    old_patient_id = models.CharField(null=True, default=None, max_length=50)
    patient_name = models.CharField(null=True, max_length=15)  # 환자 이름
    patient_gender = models.CharField(null=True, max_length=10) #환자 성별
    patient_age = models.CharField(null=True, blank=True, max_length=10) #환자 연령
    is_deleted = models.CharField(default='N', null=True, max_length=10)  #삭제 여부
    delete_date = models.DateField(default=now_plus, null=True, blank=True)  #삭제 날짜

    is_rejected = models.CharField(default=None, null=True, max_length=10)  #거부 여부
    reject_date = models.DateField(default=None, null=True, blank=True)  #거부 날짜

    is_requested = models.CharField(default=None, null=True, max_length=10)  #삭제 요청 여부
    request_date = models.DateField(default=None, null=True, blank=True)  #삭제 요청 날짜

    is_expiration = models.CharField(default=None, null=True, max_length=10)  #
    expiration_date = models.DateField(default=None, null=True, blank=True)  #

    class Meta:
        db_table = "new_patient"
