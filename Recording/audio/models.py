from django.db import models
from config import settings

# Create your models here.

class Audio(models.Model):
    #Primary Key 설정안하면 sequence primary key(id 컬럼)이 자동으로 생성됨.
    filename = models.CharField(max_length=50) #파일명
    created_at = models.DateTimeField(auto_now_add=True) #파일 DB등록시간 # 해당 레코드 생성시 현재 시간 자동저장)
    user_id = models.CharField(max_length=50) #녹취인 ID
    play_time = models.CharField(null=True, max_length=20) #녹취파일 재생시간
    filepath = models.CharField(max_length=300) #녹취파일 저장경로

    number_of_people = models.CharField(max_length=10) #총 녹취인원
    patient_id = models.CharField(max_length=10) #환자 번호

    #patient_gender = models.CharField(max_length=10) #환자 성별
    #patient_age = models.CharField(max_length=10) #환자 연령
    is_deleted = models.CharField(default='N', max_length=10) #삭제 여부
    delete_date = models.DateTimeField(null=True, blank=True) #삭제 날짜
    is_local_upload = models.CharField(default='N', max_length=10)  # 로컬 업로드 여부
    delete_reason = models.CharField(null=True, blank=True, max_length=40)  # 삭제 사유
    wav_filepath = models.CharField(null=True, blank=True, max_length=300)  # wav파일로 변환된 녹취파일 저장경로

    is_split = models.CharField(null=True, blank=True, max_length=10)
    status = models.CharField(null=True, max_length=20) #전사 상태
    prev_status = models.CharField(null=True, max_length=20)  # 전사보류 하기 직전 전사 상태
    is_requested = models.CharField(default='N', max_length=10)  # 확인요청 여부

    d_code = models.CharField(default='998', max_length=30) # 부서
    doctor_id = models.CharField(default='998-01', max_length=15)  # 의사 번호

    class Meta:
        db_table = "audio"



class Patient(models.Model):
    patient_id = models.CharField(max_length=10)  #환자 번호
    patient_gender = models.CharField(max_length=10) #환자 성별
    patient_age = models.CharField(max_length=10) #환자 연령
    is_deleted = models.CharField(default='N', max_length=10)  #삭제 여부
    delete_date = models.DateTimeField(null=True, blank=True)  #삭제 날짜
    class Meta:
        db_table = "patient"



class Doctor(models.Model):
    d_code = models.CharField(max_length=30)
    doctor_id = models.CharField(max_length=15)  # 의사 번호
    doctor_name = models.CharField(max_length=15) # 의사 이름

    class Meta:
        db_table = "doctor"
