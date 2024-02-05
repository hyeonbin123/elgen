from django.db import models

# Create your models here.

class Reply(models.Model):
    board_id = models.PositiveIntegerField() # 원글번호
    user_id = models.CharField(max_length=50)  # 댓글작성자 ID
    content = models.CharField(max_length=500)  # 댓글내용
    created_at = models.DateTimeField(auto_now_add=True)  # 댓글 DB등록시간
    modified_at = models.DateTimeField(null=True, blank=True)  # 댓글 DB수정시간
    split_filename = models.CharField(null=True, blank=True, max_length=100)  # split된 wav파일명

    class Meta:
        db_table = "reply"



class ReReply(models.Model):
    reply_id = models.PositiveIntegerField()  # 원댓글번호
    user_id = models.CharField(max_length=50)  # 대댓글작성자 ID
    content = models.CharField(max_length=300)  # 대대댓글 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 대댓글 DB등록시간

    class Meta:
        db_table = "reReply"
