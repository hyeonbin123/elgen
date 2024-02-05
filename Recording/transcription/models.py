from django.db import models

# Create your models here.

class SplitAudio(models.Model):
    wav_filepath = models.CharField(max_length=300)  # wav파일로 변환된 녹취파일 저장경로
    split_filename = models.CharField(max_length=100)  # split된 wav파일명
    split_filepath = models.CharField(max_length=300)  # split된 wav파일 저장경로
    text = models.TextField(null=True, blank=True) # 전사텍스트
    start_time = models.CharField(null=True, max_length=20)  # split파일 시작시간
    end_time = models.CharField(null=True, max_length=20)  # split파일 종료시간
    word_list = models.TextField(default=None, null=True)

    class Meta:
        db_table = "split_audio"


class Text(models.Model):
    split_filename = models.CharField(max_length=100)  # split된 wav파일명
    text1 = models.TextField(default=None, null=True, blank=True)  # 전사텍스트
    text1_user_cid = models.CharField(default=None, null=True, max_length=50)
    text1_created_at = models.DateTimeField(default=None, null=True)
    text1_user_mid = models.CharField(default=None, null=True, max_length=50)
    text1_modified_at = models.DateTimeField(default=None, null=True)

    text2 = models.TextField(default=None, null=True, blank=True)  # 전사텍스트
    text2_user_cid = models.CharField(default=None, null=True, max_length=50)
    text2_created_at = models.DateTimeField(default=None, null=True)
    text2_user_mid = models.CharField(default=None, null=True, max_length=50)
    text2_modified_at = models.DateTimeField(default=None, null=True)

    text3 = models.TextField(default=None, null=True, blank=True)  # 전사텍스트
    text3_user_cid = models.CharField(default=None, null=True, max_length=50)
    text3_created_at = models.DateTimeField(default=None, null=True)
    text3_user_mid = models.CharField(default=None, null=True, max_length=50)
    text3_modified_at = models.DateTimeField(default=None, null=True)

    is_requested = models.CharField(default='N', max_length=10)  # 확인요청 여부
    is_responded = models.CharField(default=None, null=True, max_length=10)  # 확인요청에 대한 응답여부

    is_deleted = models.CharField(default='N', max_length=10)  # 삭제 여부
    is_sound = models.CharField(default='N', max_length=10)  # 의미있는 소리 여부
    sound = models.CharField(default=None, null=True, max_length=40) #무슨 의미있는 소리

    is_first_deleted = models.CharField(default='N', max_length=10)  # 삭제 여부
    is_first_sound = models.CharField(default='N', max_length=10)  # 의미있는 소리 여부
    first_sound = models.CharField(default=None, null=True, max_length=40)  # 무슨 의미있는 소리

    speaker1 = models.CharField(null=True, max_length=10) #화자1
    speaker2 = models.CharField(null=True, max_length=10) #화자2

    class Meta:
        db_table = "text"
