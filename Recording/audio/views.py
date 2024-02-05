import ast
from ast import literal_eval
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.views import View
from moviepy.video.io import ffmpeg_tools
from pydub import AudioSegment, silence

import speech_recognition as sr
import datetime
import os
import librosa
import time
import math

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone, dateformat
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from django.core.paginator import Paginator

from audio import models
from audio.models import Audio, Patient, Doctor
from patient.models import newPatient, oldPatient
from transcription.models import SplitAudio, Text
from user.models import User, Department, Company
from reply.models import Reply as rep
from reply.models import ReReply as reRep

import io
from google.cloud import speech
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.STATICFILES_DIRS[0] + '/key/gstt-361008-6dc7a7828ba2.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.STATICFILES_DIRS[0] + '/key/etri-gstt-9311fa8960a1.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\user\Desktop\elgen\Recording\sage-reach-408201-407a3f9dd6a2.json'


class PagingList(APIView):
    def get(self, request, countperpage=10, pagenum=1, department='dept', startdate='from', enddate='to', condition='all', pstatus='all', patientnum='patient', order='new'):
        # print('order: ', order)

        user_id = request.session.get('id_session', None)  # id_session에서 가져오는 값이 id 변수에 담기는데, id_session에 값이 없으면 id값을 None으로 주겠다.
        #print('user_id: ', user_id)
        if user_id is None:  # 세션이 존재하지않는다면 로그인 창 보여주기.
            return render(request, "user/login.html")
        user = User.objects.filter(user_id=user_id).values('is_admin', 'user_id', 'user_name').first() #여기추가
        if user['is_admin'] == 'N':
            return render(request, "audio/alert.html")

        # 삭제요청이 하루지난 파일은 삭제(혹시 에러날까봐 예외처리함)
        try:
            delete_audio_list = Audio.objects.filter(is_deleted='Y').values('is_deleted', 'delete_date', 'id', 'wav_filepath', 'filepath')
            if delete_audio_list.count() > 0:
                for delete_audio in delete_audio_list:
                    if delete_audio['delete_date'] <= timezone.now():
                        reply_delete_list = rep.objects.filter(board_id=delete_audio['id']).values('id')

                        if reply_delete_list.count() > 0:
                            for reply in reply_delete_list:
                                reRep.objects.filter(reply_id=reply['id']).delete()  # 해당 글의 대댓글 DB에서 삭제
                            rep.objects.filter(board_id=delete_audio['id']).delete()  # 해당 글의 댓글 DB에서 삭제

                        if delete_audio['wav_filepath'] is not None:
                            split_delete_list = SplitAudio.objects.filter(wav_filepath=delete_audio['wav_filepath']).values('split_filename', 'split_filepath', 'id')

                            if split_delete_list.count() > 0:  # split했다면
                                for split in split_delete_list:
                                    text = Text.objects.filter(split_filename=split['split_filename']).values('id').first()
                                    if text is not None:  # 전사했다면
                                        Text.objects.filter(id=text['id']).delete() # 전사 DB 삭제
                                    if os.path.exists(split['split_filepath']):
                                        os.remove(split['split_filepath'])  # split된 실제파일 삭제
                                        split_dirname = os.path.dirname(split['split_filepath'])
                                        try:
                                            if os.path.exists(split_dirname):  # 상위폴더가 비었으면 상위폴더도 삭제
                                                os.rmdir(split_dirname)
                                                split_dir_dirname = os.path.dirname(split_dirname)
                                                if os.path.exists(split_dir_dirname):  # 상위폴더(=split폴더)가 비었으면 상위폴더도 삭제
                                                    os.rmdir(split_dir_dirname)
                                        except:
                                            pass
                                    SplitAudio.objects.filter(id=split['id']).delete()  # split DB삭제

                            if os.path.exists(delete_audio['wav_filepath']):
                                os.remove(delete_audio['wav_filepath'])  # 변환한 wav 파일 삭제
                                wav_dirname = os.path.dirname(delete_audio['wav_filepath'])
                                try:
                                    if os.path.exists(wav_dirname):  # 상위폴더가 비었으면 상위폴더도 삭제
                                        os.rmdir(wav_dirname)
                                except:
                                    pass

                        if os.path.exists(delete_audio['filepath']):
                            os.remove(delete_audio['filepath'])  # 실제 파일(.weba) 삭제(파일 업로드일 경우는 .wav일 경우도 있음.. 하지만 위에서 미리 삭제되고 이 지점에는 없겠지.)
                            audio_dirname = os.path.dirname(delete_audio['filepath'])
                            try:
                                if os.path.exists(audio_dirname):  # 상위폴더가 비었으면 상위폴더도 삭제
                                    os.rmdir(audio_dirname)
                                    audio_dir_dirname = os.path.dirname(audio_dirname)
                                    if os.path.exists(audio_dir_dirname):  # 상위폴더(날짜)가 비었으면 상위폴더도 삭제
                                        os.rmdir(audio_dir_dirname)
                                        audio_dir_dir_dirname = os.path.dirname(audio_dir_dirname)
                                        if os.path.exists(audio_dir_dir_dirname):  # 상위폴더(월)가 비었으면 상위폴더도 삭제
                                            os.rmdir(audio_dir_dir_dirname)
                            except:
                                pass
                        Audio.objects.filter(id=delete_audio['id']).delete()  # DB에서 삭제
                        print('delete_audio["id"]: ', delete_audio['id'])
                        continue
        except Exception as e:
            print(e)

        patient_delete_list = newPatient.objects.filter(request_date__lte=timezone.now(), is_requested='Y')
        if patient_delete_list.count() > 0:
            patient_delete_list.delete()

        # 전사진행상태
        if pstatus == 'transferComplete':
            status = '전송완료'

        elif pstatus == 'transcription':
            status = '전사중'
        elif pstatus == 'transcriptionComplete':
            status = '전사완료'
        elif pstatus == 'analysis':
            status = '분석중'
        elif pstatus == 'analysisComplete':
            status = '분석완료'
        elif pstatus == 'transcriptionStop':
            status = '전사보류'

        if order == 'new':
            order_by = '-id'
        elif order == 'old':
            order_by = 'id'

        sql = Audio.objects.values('id', 'filename', 'created_at', 'user_id', 'play_time', 'filepath', 'patient_id', 'wav_filepath', 'is_deleted', 'is_local_upload', 'is_split', 'status', 'is_requested', 'd_code', 'doctor_id').order_by(order_by)
        total_record_count = sql.count()

        doctor_list= []
        doctor_id = ''
        if department != 'dept':  # 부서 전체선택이 아니라면
            if '-' in department: #의사로 조회
                doctor_id = department
                department = doctor_id.split('-')[0]
                sql = sql.filter(doctor_id=doctor_id)
            else: #부서로 조회
                sql = sql.filter(d_code=department)

            # 부서별 의료진 목록(셀렉트창에서 보여주려고)
            doctor = Doctor.objects.filter(d_code=department).values('doctor_id', 'doctor_name').order_by('doctor_id')
            if doctor.count() > 0:
                doctor_list = list(doctor)

        # 여기코드추가함
        if patientnum != 'patient':
            sql = sql.filter(patient_id=patientnum)


        if pstatus == 'all':

            if startdate == 'from' and enddate == 'to':  # 1.날짜선택안함
                if condition == 'all':  # 1-1. 로컬업로드파일,삭제요청파일,확인요청파일,나에게확인요청파일 체크 안함 (제일 기본의 경우)
                    audio_object_list = sql
                    # print(audio_object_list)
                elif condition == 'local':  # 1-2. 로컬업로드파일 체크
                    audio_object_list = sql.filter(is_local_upload='Y', is_deleted='N')
                    # print(audio_object_list.count())
                elif condition == 'delete':  # 1-3. 삭제요청파일 체크
                    audio_object_list = sql.filter(is_deleted='Y')
                elif condition == 'confirm':  # 1-4. 확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y')
                elif condition == 'userConfirm':  # 1-5. 나에게확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y', user_id=user_id)
            else:  # 2.날짜선택함
                first_date = modify_date(startdate)
                last_date = modify_date(enddate) + datetime.timedelta(days=1)

                if condition == 'all':  # 2-1. 로컬업로드파일,삭제요청파일,확인요청파일,나에게확인요청파일 체크 안함 (제일 기본의 경우)
                    audio_object_list = sql.filter(created_at__range=(first_date, last_date))
                elif condition == 'local':  # 2-2. 로컬업로드파일 체크
                    audio_object_list = sql.filter(is_local_upload='Y', is_deleted='N',
                                                   created_at__range=(first_date, last_date))
                elif condition == 'delete':  # 2-3. 삭제요청파일 체크
                    audio_object_list = sql.filter(is_deleted='Y',
                                                   created_at__range=(first_date, last_date))
                elif condition == 'confirm':  # 2-4. 확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y',
                                                   created_at__range=(first_date, last_date))
                elif condition == 'userConfirm':  # 2-5. 나에게확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y', user_id=user_id,
                                                   created_at__range=(first_date, last_date))

        else:  # 상태: 전체 이외의 상태(전송완료, 전사중, 전사완료...)

            if startdate == 'from' and enddate == 'to':  # 1.날짜선택안함
                if condition == 'all':  # 1-1. 로컬업로드파일,삭제요청파일,확인요청파일,나에게확인요청파일 체크 안함 (제일 기본의 경우)
                    audio_object_list = sql.filter(status=status)
                elif condition == 'local':  # 1-2. 로컬업로드파일 체크
                    audio_object_list = sql.filter(is_local_upload='Y', is_deleted='N', status=status)
                elif condition == 'delete':  # 1-3. 삭제요청파일 체크
                    audio_object_list = sql.filter(is_deleted='Y', status=status)
                elif condition == 'confirm':  # 1-4. 확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y', status=status)
                elif condition == 'userConfirm':  # 1-5. 나에게확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y', user_id=user_id, status=status)
            else:  # 2.날짜선택함
                first_date = modify_date(startdate)
                last_date = modify_date(enddate) + datetime.timedelta(days=1)

                if condition == 'all':  # 2-1. 로컬업로드파일,삭제요청파일,확인요청파일,나에게확인요청파일 체크 안함 (제일 기본의 경우)
                    audio_object_list = sql.filter(created_at__range=(first_date, last_date), status=status)
                elif condition == 'local':  # 2-2. 로컬업로드파일 체크
                    audio_object_list = sql.filter(is_local_upload='Y', is_deleted='N',
                                                   created_at__range=(first_date, last_date), status=status)
                elif condition == 'delete':  # 2-3. 삭제요청파일 체크
                    audio_object_list = sql.filter(is_deleted='Y',
                                                   created_at__range=(first_date, last_date), status=status)
                elif condition == 'confirm':  # 2-4. 확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y',
                                                   created_at__range=(first_date, last_date), status=status)
                elif condition == 'userConfirm':  # 2-5. 나에게확인요청파일 체크
                    audio_object_list = sql.filter(is_requested='Y', user_id=user_id,
                                                   created_at__range=(first_date, last_date), status=status)


        total_count = audio_object_list.values('id').count()
        # print('total_count: ', total_count)
        paginator = Paginator(audio_object_list, countperpage)
        audio_object_list = paginator.get_page(pagenum)  # 1번페이지에 해당하는 오디오리스트 출력, 2번페이지에 해당하는 오디오리스트 출력
        calculate_list = calculate_page(pagenum, countperpage, total_count)

        # print('len(audio_object_list): ', len(audio_object_list))

        # 총 녹취 시간 구하기!
        audio_object_list2 = Audio.objects.filter(is_deleted='N').order_by('-id').values('play_time')

        total_seconds = 0
        for audio2 in audio_object_list2:
            if audio2['play_time'] is not None:
                duration2 = audio2['play_time'].split(':')
                hour = int(duration2[0])
                minute = int(duration2[1])
                second = int(duration2[2])

                duration_to_seconds = hour * 60 * 60 + minute * 60 + second
                total_seconds += duration_to_seconds

        # get min and seconds first
        mm, ss = divmod(total_seconds, 60)
        # Get hours
        hh, mm = divmod(mm, 60)

        get_duration = dict(hh=hh, mm=mm, ss=ss, total_seconds=total_seconds)
        # ------------------------------------------------총 녹취 시간 구하기 끝

        audio_list = []

        for audio in audio_object_list:
            #audio_user = User.objects.filter(user_id=audio['user_id']).values('user_name').first() #녹취인(로그인한사람. 주로 간호사쌤) 정보
            audio_user = Doctor.objects.filter(doctor_id=audio['doctor_id']).values('doctor_name').first() #의료진 정보
            if audio_user is None:
                user_name = '무명'
            else:
                user_name = audio_user['doctor_name']
            patient_department = Department.objects.filter(d_code=audio['d_code']).values('d_name').first()  # 부서

            #여기추가2
            if 'n' in audio['patient_id']:
                table = models.Patient
            else:
                table = newPatient

            patient_info = table.objects.filter(patient_id=audio['patient_id']).values('patient_gender', 'patient_age').first()  # 녹취환자 정보
            if patient_info is None:
                patient_gender = '성별'
                patient_age = '연령'
            else:  # 여기추가2
                patient_gender = patient_info['patient_gender']

                if patient_info['patient_gender'] == 'M':
                    patient_gender = '남성'
                elif patient_info['patient_gender'] == 'F':
                    patient_gender = '여성'

                patient_age = patient_info['patient_age']

                if not '대' in patient_info['patient_age']:
                    patient_age = patient_info['patient_age'] + '세'

            reply_count = rep.objects.filter(board_id=audio['id']).values('id').count()  # 해당글의 총댓글수
            # print('reply_count: ', reply_count)

            if audio['wav_filepath'] is not None:
                wav_filename = os.path.basename(audio['wav_filepath'])
            else:
                wav_filename = None


            # filepath_date 변수 만들기 (파일 경로 중에 날짜 경로부분만 가져온다)
            if 'local_upload' in audio['filepath']:
                filepath_rsplit = audio['filepath'].rsplit('\\', 5)
                filepath_date = filepath_rsplit[1] + os.sep + filepath_rsplit[2] + os.sep + filepath_rsplit[3] + os.sep + 'local_upload'
            else:
                filepath_rsplit = audio['filepath'].rsplit('\\', 4)
                filepath_date = filepath_rsplit[1] + os.sep + filepath_rsplit[2] + os.sep + filepath_rsplit[3]

            # 지금 로그인한 사용자에게 확인요청 들어온 글 알려주기
            request_flag = False
            if audio['user_id'] == user_id and audio['is_requested'] == 'Y':
                request_flag = True

            audio_list.append(dict(id=audio['id'], d_name=patient_department['d_name'], filename=audio['filename'], user_name=user_name,
                                   filepath=audio['filepath'], created_at=audio['created_at'], play_time=audio['play_time'],
                                   patient_id=audio['patient_id'], patient_gender=patient_gender,
                                   patient_age=patient_age, is_deleted=audio['is_deleted'],
                                   filepath_date=filepath_date, is_local_upload=audio['is_local_upload'],
                                   wav_filename=wav_filename, is_split=audio['is_split'],
                                   status=audio['status'], is_requested=audio['is_requested'],
                                   request_flag=request_flag, reply_count=reply_count))

        page_list = dict(countperpage=countperpage, pagenum=pagenum, department=department, doctor_id=doctor_id, startdate=startdate, enddate=enddate, condition=condition, pstatus=pstatus, patientnum=patientnum, order=order)

        #부서명
        department_object_list = Department.objects.filter(~Q(d_code='999')).values('d_code', 'd_name').order_by('d_code')
        department_list = []

        if len(department_object_list) > 0 :
            for department_object in department_object_list:
                department_list.append(department_object)

        patient_count = newPatient.objects.filter(~Q(patient_id='00000'), is_rejected=None).values('id').count()
        record_info_list = {'total_count':total_count, 'total_record_count':total_record_count, 'patient_count':patient_count}
        return render(request, "audio/recording_list.html", context=dict(user_id=user_id, get_duration=get_duration, is_admin=user['is_admin'], audios=audio_list, page_list=page_list, calculate_list=calculate_list, department_list=department_list, record_info_list=record_info_list, user=user, param='recording_list', doctor_list=doctor_list)) #여기추가


def modify_date(date):
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    return date

def calculate_page(pagenum, countperpage, total_count):
    button_num = 10 #버튼 한페이지에 10개만 보여줌
    #print('total_count: ', total_count)
    end_page = (math.ceil(pagenum / button_num)) * button_num
    #print('end_page: ', end_page)
    begin_page = (end_page - button_num) + 1
    #print('begin_page: ', begin_page)
    prev = False if begin_page == 1 else True
    #print('prev: ', prev)
    next = False if end_page * countperpage >= total_count else True
    #print('next: ', next)
    if next == False :
        end_page = math.ceil(total_count / countperpage)
        #print('end_page: ', end_page)

    nums = []
    for num in range(begin_page, end_page + 1):
        nums.append(num)

    #print('nums: ', nums)

    calculate_list = dict(end_page=end_page, begin_page=begin_page, nums=nums, prev=prev, next=next)
    return calculate_list

def get_file_download_list(request):
    startdate = request.POST.get('startdate', None)
    enddate = request.POST.get('enddate', None)
    if startdate is None or enddate is None:
        return JsonResponse({'message': 'Fail'})

    first_date = modify_date(startdate)
    last_date = modify_date(enddate) + datetime.timedelta(days=1)
    audio_object_list = Audio.objects.filter(created_at__range=(first_date, last_date)).filter(~Q(wav_filepath=None)).values('wav_filepath')
    audio_list = []
    if len(audio_object_list) > 0:
        for audio in audio_object_list:
            filename = audio['wav_filepath'].split('\\')[-1]
            text_filepath = os.path.splitext(audio['wav_filepath'])[0] + '.txt'
            if os.path.isfile(text_filepath):
               text_filename = os.path.basename(text_filepath)
            else:
                text_filename = None

            # filepath_date 변수 만들기 (파일 경로 중에 날짜 경로부분만 가져온다)
            if 'local_upload' in audio['wav_filepath']:
                SPLIT_TIMES = 5
            else:
                SPLIT_TIMES = 4

            filepath_rsplit = audio['wav_filepath'].rsplit('\\', SPLIT_TIMES)
            filepath_date = ''

            for i in range(1, SPLIT_TIMES):
                if i == SPLIT_TIMES - 1: #path 마지막에는 \\붙일 필요없음
                    filepath_date += filepath_rsplit[i]
                else:
                    filepath_date += filepath_rsplit[i] + os.sep

            audio_list.append(dict(filename=filename, text_filename=text_filename, filepath_date=filepath_date))

    return JsonResponse({'message': 'success', 'audio_list': audio_list})


class Detail(APIView):
    def get(self, request, num, countperpage, pagenum, department, startdate, enddate, condition, pstatus, patientnum, order_by):
        #print('order: ', order_by)

        user_id = request.session.get('id_session', None)  # id_session에서 가져오는 값이 id 변수에 담기는데, id_session에 값이 없으면 id값을 None으로 주겠다.
        #print('user_id: ', user_id)
        split_pagenum = int(request.GET.get('split_pagenum', 1)) # 처음 detail페이지 들어가면 1 , 10이 기본값..
        split_countperpage = int(request.GET.get('split_countperpage', 10))
        split_file_requested = request.GET.get('split_file_requested', 'N')
        split_text3 = request.GET.get('split_text3', 'N')


        if user_id is None:  # 세션이 존재하지않는다면 로그인 창 보여주기.
            return render(request, "user/login.html")
        user = User.objects.filter(user_id=user_id).values('is_admin', 'c_code').first()
        if user['is_admin'] == 'N':
            return render(request, "audio/alert.html")

        audio = Audio.objects.filter(id=num).values('id', 'filename', 'created_at', 'user_id', 'filepath', 'is_deleted', 'delete_date', 'is_local_upload', 'number_of_people', 'patient_id', 'delete_reason', 'status', 'wav_filepath', 'is_requested', 'd_code', 'doctor_id').first()
        audio_user = User.objects.filter(user_id=audio['user_id']).values('d_code', 'user_name').first()  # 녹취인 정보

        doctor_user = Doctor.objects.filter(doctor_id=audio['doctor_id']).values('doctor_name').first()  # 의료진 정보
        if doctor_user is None:
            doctor_name = '무명'
        else:
            doctor_name = doctor_user['doctor_name']

        user_department = Department.objects.filter(d_code=audio['d_code']).values('d_name').first()  # 부서

        # 환자정보
        if 'n' in audio['patient_id']:
            table = models.Patient
        else:
            table = newPatient

        patient_info = table.objects.filter(patient_id=audio['patient_id']).values('patient_gender', 'patient_age').first()  # 녹취환자 정보
        if patient_info is None:
            patient_gender = '성별'
            patient_age = '연령'
        else:  # 여기추가2
            patient_gender = patient_info['patient_gender']

            if patient_info['patient_gender'] == 'M':
                patient_gender = '남성'
            elif patient_info['patient_gender'] == 'F':
                patient_gender = '여성'

            patient_age = patient_info['patient_age']

            if not '대' in patient_info['patient_age']:
                patient_age = patient_info['patient_age'] + '세'

        # 녹취인 ID 리스트
        user_object_list = User.objects.filter(c_code='03').values('id', 'user_id').order_by('id')
        cnuh_user_list = []

        if len(user_object_list) > 0 :
            for user_object in user_object_list:
                cnuh_user_list.append(user_object)

        # 부서 리스트
        department_object_list = Department.objects.filter(~Q(d_code='999'), ~Q(d_code='000')).values('d_code', 'd_name').order_by('d_code')
        department_list = []

        if len(department_object_list) > 0 :
            for department_object in department_object_list:
                department_list.append(department_object)

        # 댓글 부분
        reply_object_list = rep.objects.filter(board_id=num).order_by('-id')

        # 댓글 페이징
        reply_pagenum = 1
        reply_countperpage = 10 #해당글에 처음 들어가면 1번페이지의 댓글과 10개씩보기가 기본 설정되어있어서 1,10으로 값을 넣어줌
        total_count = reply_object_list.count() #해당 글에 달린 댓글 개수

        calculate_list = calculate_page(reply_pagenum, reply_countperpage, total_count)

        begin_index = (reply_pagenum - 1) * reply_countperpage
        end_index = (reply_pagenum * reply_countperpage)
        #print(begin_index, end_index)

        if reply_pagenum == calculate_list['end_page'] and calculate_list['next'] is False:
            end_index = total_count


        # 전사부분
        order = Company.objects.filter(c_code=user['c_code']).values('order').first()['order']
        split_audio_object_list = []

        if audio['wav_filepath'] is not None: # .weba에서 .wav로 변환한 경우
            wav_filename = os.path.basename(audio['wav_filepath'])
            split_audio_object_list = SplitAudio.objects.filter(wav_filepath=audio['wav_filepath']).values('id', 'split_filename', 'text', 'start_time', 'end_time', 'word_list').order_by('id') #split하지 않았다면 count()는 0을 출력한다.
            filename_list = []

            if split_file_requested == 'Y': #확인요청 들어온 리스트만 보여줌 (split_file_requested == 'N'이면 이 if문은 패스하고 지나감)
                for object in split_audio_object_list:
                    requested_object = Text.objects.filter(split_filename=object['split_filename']).values('split_filename', 'is_requested').first()
                    if requested_object['is_requested'] == 'Y':
                        filename_list.append(requested_object['split_filename'])
                split_audio_object_list = split_audio_object_list.filter(split_filename__in=filename_list) #확인요청 들어온 것만 리스트에 담음
            
            if split_text3 == 'Y':
                for object in split_audio_object_list:
                    requested_object = Text.objects.filter(split_filename=object['split_filename']).values('split_filename', 'text3').first()
                    if requested_object['text3'] is not None:
                        filename_list.append(requested_object['split_filename'])
                split_audio_object_list = split_audio_object_list.filter(split_filename__in=filename_list) #충남대병원 답변만 리스트에 담음


        else: # .weba에서 .wav로 변환하지 않았을 경우
            wav_filename = None

        #print('wav_filename: ', wav_filename)

        split_audio_list = []
        is_requested_total = 0
        is_not_empty_requested_total = 0
        is_responded_total = 0
        is_empty_text_total = 0

        # 전사 페이징
        #split_pagenum = 1
        #split_countperpage = 10

        #split_total_count = split_audio_object_list.count() #count()는 0을 반환하지못하나봄..0 나오면 에러남. 그래서 밑의 코드로 수정. #왜그러지..? 0나와야하는데..
        split_total_count = len(split_audio_object_list)

        split_calculate_list = []
        begin_index2 = 0
        end_index2 = 0

        if split_total_count > 0:
            split_calculate_list = calculate_page(split_pagenum, split_countperpage, split_total_count)

            begin_index2 = (split_pagenum - 1) * split_countperpage
            end_index2 = (split_pagenum * split_countperpage)
            #print(begin_index2, end_index2)

            if split_pagenum == split_calculate_list['end_page'] and split_calculate_list['next'] is False:
                end_index2 = split_total_count
                #print(end_index2)

            #print('split_calculate_list: ', split_calculate_list)

        get_full_text_list = []
        if len(split_audio_object_list) > 0 and split_audio_object_list.count() > 0: #두개중 한 조건식만 사용해도 될것같은데..혹시몰라서 두개 다 작성
            # 전체 stt된 텍스트 보기 위해서 (밑에서 페이징처리하면 전체 stt된 텍스트를 볼수 없다. 페이징처리한 만큼의 내용만 출력. 그래서 이렇게 전체를 반복문으로 돌림(페이징처리안하고))
            for split_audio in split_audio_object_list:
                full_text = Text.objects.filter(split_filename=split_audio['split_filename']).values('text1', 'text2', 'text3', 'is_deleted', 'is_sound').first()
                if full_text is None:
                    full_text1 = None
                    full_text2 = None
                    full_text3 = None
                    full_text_is_deleted = None
                    full_text_is_sound = None
                else:
                    full_text1 = full_text['text1']
                    full_text2 = full_text['text2']
                    full_text3 = full_text['text3']
                    full_text_is_deleted = full_text['is_deleted']
                    full_text_is_sound = full_text['is_sound']

                get_full_text_list.append(dict(text=split_audio['text'], text1=full_text1, text2=full_text2, text3=full_text3, is_deleted=full_text_is_deleted, is_sound=full_text_is_sound))
            # 페이징처리
            for i in range(begin_index2, end_index2):
            #for split_audio in split_audio_object_list:
                split_only_filename = os.path.splitext(wav_filename)[0]
                split_filename_num = split_audio_object_list[i]['split_filename'].split('_')[-1].split('.')[0]

                split_filename = split_audio_object_list[i]['split_filename']

                text = Text.objects.filter(split_filename=split_filename).values('text1', 'text2', 'text3', 'is_requested', 'is_responded', 'is_deleted', 'sound', 'is_sound', 'is_first_deleted', 'is_first_sound', 'first_sound', 'speaker1', 'speaker2').first()


                if text is None: #아직 전사시작되기 전 상황(전송완료 상황)
                    text1 = None
                    text2 = None
                    text3 = None
                    is_requested = None
                    is_responded = None
                    is_deleted = None
                    is_sound = None
                    sound = None

                    is_first_deleted = None
                    is_first_sound = None
                    first_sound = None

                    speaker1 = None
                    speaker2 = None
                else:
                    #text1_dict = Text.objects.filter(split_filename=split_filename).values('text1').first()
                    #text1 = text1_dict['text1']
                    # 상태는 전사중이지만 아직 해당 텍스트에 대한 전사를 안해서 text1이 null이라면 여기서는 None을 출력하고 detail.html의 템플릿태그에서는 null을 출력함.
                    text1 = text['text1']
                    text2 = text['text2']

                    is_requested = text['is_requested']
                    if is_requested == 'Y':
                        is_requested_total += 1

                    text3 = text['text3']

                    is_responded = text['is_responded']
                    if is_responded == 'Y':
                        is_responded_total += 1

                    is_deleted = text['is_deleted']
                    is_sound = text['is_sound']
                    sound = text['sound']

                    if is_deleted == 'Y' or is_sound == 'Y':
                        is_empty_text_total += 1

                    is_not_empty_requested = Text.objects.filter(split_filename=split_filename, is_requested='Y', is_deleted='N', is_sound='N').values('is_requested').first()
                    #print('is_not_empty_requested: ', is_not_empty_requested)
                    if is_not_empty_requested is not None:
                        is_not_empty_requested_total += 1

                    #print('is_not_empty_requested_total: ', is_not_empty_requested_total)

                    is_first_deleted = text['is_first_deleted']
                    is_first_sound = text['is_first_sound']
                    first_sound = text['first_sound']

                    speaker1 = text['speaker1']
                    speaker2 = text['speaker2']


                word_list = split_audio_object_list[i]['word_list']
                if word_list is not None and word_list != '':
                    word_list = literal_eval(word_list)

                split_audio_list.append(dict(id=split_audio_object_list[i]['id'],
                                        split_only_filename=split_only_filename,
                                        split_filename=split_audio_object_list[i]['split_filename'],
                                        split_filename_num=split_filename_num,
                                        text=split_audio_object_list[i]['text'],
                                        start_time=split_audio_object_list[i]['start_time'],
                                        end_time=split_audio_object_list[i]['end_time'],
                                        word_list=word_list,
                                        text1=text1,
                                        text2=text2,
                                        text3=text3,
                                        is_requested=is_requested,
                                        is_responded=is_responded,
                                        is_deleted=is_deleted,
                                        is_sound=is_sound,
                                        sound=sound,
                                        is_first_deleted=is_first_deleted,
                                        is_first_sound=is_first_sound,
                                        first_sound=first_sound,
                                        speaker1=None,
                                        speaker2=None))

        else:
            print('0임')

        #print('len(split_audio_list): ', len(split_audio_list))

        #다시 댓글 부분
        reply_list = []

        if total_count > 0:
            for i in range(begin_index, end_index):
            #for reply in reply_object_list:

                if reply_object_list[i].split_filename is not None:
                    split_filename_num = reply_object_list[i].split_filename.split('_')[-1].split('.')[0]
                else: #댓글 작성할 때 기타 선택했을때
                    split_filename_num = None

                re_reply_object_list = reRep.objects.filter(reply_id=reply_object_list[i].id).order_by('id')  # 해당 댓글의 대댓글목록 출력

                #print('re_reply_object_list: ', re_reply_object_list) #여기까지는 잘 출력함....

                re_reply_list = []
                for re_reply in re_reply_object_list:
                    re_re_reply_list = []
                    re_re_reply_list.append(dict(id=re_reply.id,
                                              reply_id=re_reply.reply_id,
                                              user_id=re_reply.user_id,
                                              content=re_reply.content,
                                              created_at=re_reply.created_at))
                    re_reply_list.append(re_re_reply_list)
                    #print('re_re_reply_list: ', re_re_reply_list)
                #print('re_reply_list!!!: ', re_reply_list)

                reply_list.append(dict(id=reply_object_list[i].id,
                                       user_id=reply_object_list[i].user_id,
                                       content=reply_object_list[i].content,
                                       created_at=reply_object_list[i].created_at,
                                       modified_at=reply_object_list[i].modified_at,
                                       split_filename_num=split_filename_num,
                                       re_reply_list=re_reply_list))
        #endif문


        audio_list = []

        # filepath_date 변수 만들기 (파일 경로 중에 날짜 경로부분만 가져온다)
        if 'local_upload' in audio['filepath']:
            filepath_rsplit = audio['filepath'].rsplit('\\', 5)
            filepath_date = filepath_rsplit[1] + '/' + filepath_rsplit[2] + '/' + filepath_rsplit[3] + '/' + 'local_upload'
        else:
            filepath_rsplit = audio['filepath'].rsplit('\\', 4)
            filepath_date = filepath_rsplit[1] + '/' + filepath_rsplit[2] + '/' + filepath_rsplit[3]

        audio_list.append(dict(id=audio['id'],
                               user_id=audio['user_id'],
                               d_name=user_department['d_name'],
                               filename=audio['filename'],
                               user_name=audio_user['user_name'],
                               doctor_name=doctor_name,
                               filepath=audio['filepath'],
                               created_at=audio['created_at'],
                               patient_id=audio['patient_id'],
                               patient_gender=patient_gender,
                               patient_age=patient_age,
                               number_of_people=audio['number_of_people'],
                               is_deleted=audio['is_deleted'],
                               delete_date=audio['delete_date'],
                               is_local_upload=audio['is_local_upload'],
                               delete_reason=audio['delete_reason'],
                               wav_filepath=audio['wav_filepath']))

        is_deleted = audio['is_deleted']
        status = audio['status']

        is_requested = audio['is_requested']

        total_list = dict(is_requested_total=is_requested_total, is_responded_total=is_responded_total,is_empty_text_total=is_empty_text_total, is_not_empty_requested_total=is_not_empty_requested_total)

        page_list = dict(countperpage=countperpage, pagenum=pagenum, department=department, startdate=startdate, enddate=enddate, condition=condition, pstatus=pstatus, patientnum=patientnum, order=order_by)
        reply_page_list = dict(reply_countperpage=reply_countperpage, reply_pagenum=reply_pagenum, total_count=total_count)
        split_page_list = dict(split_countperpage=split_countperpage, split_pagenum=split_pagenum, split_total_count=split_total_count, split_calculate_list=split_calculate_list, split_file_requested=split_file_requested, split_text3=split_text3)

        return render(request, "audio/recording_detail.html", context=dict(audio_list=audio_list, page_list=page_list, reply_list=reply_list, user_id=user_id, c_code=user['c_code'], is_admin=user['is_admin'], order=order, wav_filename=wav_filename, filepath_date=filepath_date, split_audio_list=split_audio_list, status=status, is_requested=is_requested, total_list=total_list, reply_page_list=reply_page_list, calculate_list=calculate_list, is_deleted=is_deleted, split_page_list=split_page_list, get_full_text_list=get_full_text_list, department_list=department_list, cnuh_user_list=cnuh_user_list))



class Patient(APIView):
    def post(self, request, condition):
        if condition == 'check': #여기추가2 #거부환자 잡아주는 로직 만들기
            reg_id = json.loads(request.body)

            if reg_id != None:
                patient = newPatient.objects.filter(reg_id=reg_id).values('registered_at', 'patient_id', 'patient_name', 'patient_gender', 'patient_age', 'is_deleted', 'delete_date', 'is_rejected').first()
                today = datetime.datetime.today().strftime('%Y-%m-%d')

                if patient != None: #기존에 등록되어 있는 환자
                    datetime_string = "2022-11-14"
                    datetime_format = "%Y-%m-%d"
                    datetime_result = datetime.datetime.strptime(datetime_string, datetime_format)

                    #print('patient: ', patient)
                    if patient['is_rejected'] == 'Y': # 거부환자
                        registered_at = None
                    elif patient['is_rejected'] == 'N': # 거부취소환자
                        registered_at = today
                        print(patient['patient_gender'])
                    else: # 거부환자 아닌 일반환자
                        if patient['registered_at'] < datetime_result.date() and patient['delete_date'] is None: #11월 14일 이전 등록환자는 동의서취득 다시 받아야함
                            registered_at = today
                        else:
                            registered_at = patient['registered_at']


                    # 기존에 등록되어 있는 환자의 녹취이력보기(#여기추가4)
                    new_patient_id = newPatient.objects.filter(reg_id=reg_id).values('patient_id').first()['patient_id']
                    old_patient_query = oldPatient.objects.filter(reg_id=reg_id).values('id', 'old_patient_id').order_by('-id')
                    new_audio_list = Audio.objects.filter(patient_id=new_patient_id).values('id', 'd_code', 'filename', 'created_at').order_by('-id')

                    total_list = []
                    if new_audio_list.count() > 0:  # 신환자번호로 녹음된 녹음파일이 1개라도 있으면

                        for new in new_audio_list:
                            new_dic = {}
                            dep = Department.objects.filter(d_code=new['d_code']).values('d_name').first()['d_name']
                            new_dic['department'] = dep
                            #s = new['filename'].split('_')[2] #업로드했을땐 또 다름(어떻게해야할까...ㅠㅠㅠ)
                            #rec_date = s[0:4] + '-' + s[4:6] + '-' + s[6:8] + ' ' + s[8:10] + ':' + s[10:12] + ':' + s[12:14]
                            new_dic['date'] = dateformat.format(new['created_at'], 'y-m-d H:i')
                            total_list.append(new_dic)
                    if old_patient_query.count() > 0: # 구환자번호가 존재할 경우
                        for old_patient in list(old_patient_query):
                            old_audio_list = Audio.objects.filter(patient_id=old_patient['old_patient_id']).values('id', 'd_code', 'filename', 'created_at')
                            if old_audio_list.count() > 0:
                                for old in old_audio_list:
                                    old_dic = {}
                                    dep = Department.objects.filter(d_code=old['d_code']).values('d_name').first()['d_name']
                                    old_dic['department'] = dep
                                    #s = old['filename'].split('_')[2]
                                    #rec_date = s[0:4] + '-' + s[4:6] + '-' + s[6:8] + ' ' + s[8:10] + ':' + s[10:12] + ':' + s[12:14]
                                    old_dic['date'] = dateformat.format(old['created_at'], 'y-m-d H:i')
                                    total_list.append(old_dic)
                    total_list = sorted(total_list, key=itemgetter('date'), reverse=True)  # 최신순으로 정렬
                    return JsonResponse({'registered_at': registered_at, 'patient_id': patient['patient_id'], 'patient_name': patient['patient_name'], 'patient_gender': patient['patient_gender'], 'patient_age': patient['patient_age'], 'is_deleted': patient['is_deleted'], 'list': total_list, 'is_new': False, 'is_rejected': patient['is_rejected']})

                else: #기존에 등록되어 있지 않은 환자(신규환자)
                    p_list = newPatient.objects.filter(~Q(patient_id=None), ~Q(patient_id='')).values('patient_id')
                    p_new_list = []
                    for l in p_list:
                        try:
                            p_new_list.append(int(l['patient_id']))
                        except:
                            continue
                    new_num = '{:05d}'.format(findSmallestMissing(p_new_list))
                    return JsonResponse({'registered_at': today, 'patient_id': new_num, 'patient_name': None, 'patient_gender': None, 'patient_age': None, 'is_deleted': None, 'list': None, 'is_new': True, 'is_rejected': None})
            else:
                return JsonResponse({'registered_at': None, 'patient_id': None, 'patient_name': None, 'patient_gender': None, 'patient_age': None, 'is_deleted': None, 'list': None, 'is_new': None, 'is_rejected': None})

        elif condition == 'regist2': #여기추가214
            reg_id = request.POST.get('reg_id', None)
            name = request.POST.get('name', None)
            age = request.POST.get('age', None)
            gender = request.POST.get('gender', None)

            if name == '':
                name = None
            if age == '':
                age = None
            if gender == '':
                gender = None

            today = datetime.datetime.today().date()

            patient = newPatient.objects.filter(reg_id=reg_id).first()
            if patient is None:
                newPatient.objects.create(reg_id=reg_id, patient_name=name, patient_gender=gender, patient_age=age, is_deleted=None, delete_date=None, is_rejected='Y', reject_date=today)
                newPatient.objects.filter(reg_id=reg_id).update(registered_at=None)
            else:
                newPatient.objects.filter(reg_id=reg_id).update(patient_name=name, patient_gender=gender, patient_age=age, is_deleted=None, delete_date=None, is_rejected='Y', reject_date=today)
            return HttpResponse(status=status.HTTP_200_OK)

        elif condition == 'expiration2':
            reg_id = request.POST.get('reg_id', None)
            name = request.POST.get('name', None)
            age = request.POST.get('age', None)
            gender = request.POST.get('gender', None)

            if name == '':
                name = None
            if age == '':
                age = None
            if gender == '':
                gender = None

            today = datetime.datetime.today().date()

            patient = newPatient.objects.filter(reg_id=reg_id).first()
            if patient is None:
                newPatient.objects.create(reg_id=reg_id, patient_name=name, patient_gender=gender, patient_age=age, is_deleted=None, delete_date=None, is_expiration='Y', expiration_date=today)
                newPatient.objects.filter(reg_id=reg_id).update(registered_at=None)
            else:
                newPatient.objects.filter(reg_id=reg_id).update(patient_name=name, patient_gender=gender, patient_age=age, is_deleted=None, delete_date=None, is_expiration='Y', expiration_date=today)
            return HttpResponse(status=status.HTTP_200_OK)

        elif condition == 'update': #환자정보수정
            gender = request.POST.get('gender', None)
            age = request.POST.get('age', None)
            patient_id = request.POST.get('patient_id', None)

            models.Patient.objects.filter(patient_id=patient_id).update(patient_gender=gender, patient_age=age) #환자정보 수정
            return HttpResponse(status=status.HTTP_200_OK)

        elif condition == 'insert': #여기추가3

            #old_filepath = 'C:/Users/user/Downloads/old.txt'
            #old_filepath = '/home/elgen/devOps/old.txt'
            #new_filepath = 'C:/Users/user/Downloads/new3.txt'
            '''
            new_filepath = '/home/elgen/devOps/new3.txt'
            with open(new_filepath, 'r', encoding='UTF8') as f:
                lines = f.readlines()
                for line in lines:
                    dict_line = ast.literal_eval(line)
                    print(dict_line['patient_id'])
                    print(dict_line['doctor_id'])
                    Audio.objects.filter(patient_id=dict_line['patient_id']).update(doctor_id=dict_line['doctor_id'])
            '''
            audio_list = Audio.objects.values('patient_id')
            for audio in audio_list:
                if 'n' in audio['patient_id']:
                    print(audio['patient_id'])
            return HttpResponse(status=status.HTTP_200_OK)
        elif condition == 'insert2': #여기추가3
            first_date = datetime.date(2022, 8, 31)
            after = first_date + relativedelta(months=6)
            print('after: ', after)
            '''
            last_date = datetime.date(2023, 1, 20)
            new = newPatient.objects.filter(registered_at__range=(first_date, last_date)).values('registered_at')
            for n in new:
                #print('new: ', n['registered_at'])
                delete_date = n['registered_at'] + relativedelta(months=6)
                newPatient.objects.filter(registered_at=n['registered_at']).update(delete_date=delete_date)
            '''
            return HttpResponse(status=status.HTTP_200_OK)
        elif condition == 'insert3':
            return HttpResponse(status=status.HTTP_200_OK)
        elif condition == 'check2': #여기추가214
            reg_id = json.loads(request.body)
            patient = newPatient.objects.filter(reg_id=reg_id).values('patient_name', 'patient_gender', 'patient_age', 'is_rejected').first()
            if patient is None: #존재하지 않는 등록번호
                return JsonResponse({'patient_name': None, 'patient_gender': None, 'patient_age': None, 'is_rejected': None, 'is_new': True})
            # 존재하는 등록번호
            return JsonResponse({'patient_name': patient['patient_name'], 'patient_gender': patient['patient_gender'], 'patient_age': patient['patient_age'], 'is_rejected': patient['is_rejected'], 'is_new': False})
        elif condition == 'delete2': #여기추가214 (여기 있는 애들 ㄷ ㅏ patient views.py로 이동시키기)
            reg_id = request.POST.get('reg_id', None)
            newPatient.objects.filter(reg_id=reg_id).update(is_rejected='N', reject_date=None)
            return HttpResponse(status=status.HTTP_200_OK)

class File(APIView):
    def post(self, request, condition):
        if condition == 'delete':
            num = request.POST.get('num', None)
            audio = Audio.objects.filter(id=num).first()
            if audio.is_requested == 'Y':
                message = 'fail'
                return HttpResponse(message, status=status.HTTP_200_OK)


            delete_reason = request.POST.get('reason', None)
            delete_date = datetime.datetime.combine(timezone.now(), datetime.time.min) + datetime.timedelta(days=1)
            #delete_date = datetime.datetime.combine(timezone.now(), datetime.time.min) + datetime.timedelta(hours=11, minutes=12)

            # timezone.now()는 현재 날짜와 시간을 출력
            # datetime.datetime.combine(timezone.now(), datetime.time.min)은 현재 날짜의 자정을 출력
            # datetime.timedelta(days=1)은 하루 후(24시간 후)를 출력
            # 즉 delete_date는 다음날 자정을 출력

            Audio.objects.filter(id=num).update(is_deleted='Y', delete_date=delete_date, delete_reason=delete_reason)
            message = 'success'
            return HttpResponse(message, status=status.HTTP_200_OK)

        elif condition == 'cancel':
            num = request.POST.get('num', None)
            patient_id = Audio.objects.filter(id=num).values('patient_id').first()['patient_id']
            is_delete_requested = newPatient.objects.filter(patient_id=patient_id).values('is_requested').first()['is_requested']
            list = {}
            if is_delete_requested == 'Y': #환자를 삭제요청했을 경우 글 삭제취소가 안됨
                message = 'fail'
            else:
                Audio.objects.filter(id=num).update(is_deleted='N', delete_date=None, delete_reason=None)
                message = 'success'
            list['patient_id'] = patient_id
            list['message'] = message
            return Response(list, status=status.HTTP_200_OK)
        elif condition == 'check_delete':
            delete_files = json.loads(request.body)
            for delete_file in delete_files:
                audio = Audio.objects.filter(id=delete_file).first()
                if audio.is_requested == 'Y':
                    return JsonResponse({'message': 'fail'})

            return JsonResponse({'message': 'success'})
        elif condition == 'multi_delete':
            delete_files = json.loads(request.body)
            delete_date = datetime.datetime.combine(timezone.now(), datetime.time.min) + datetime.timedelta(days=1)

            for delete_file in delete_files:
                num = delete_file['num']
                delete_reason = delete_file['reason']
                Audio.objects.filter(id=num).update(is_deleted='Y', delete_date=delete_date, delete_reason=delete_reason)

            return JsonResponse({'None': None}) #어떤 값을 리턴해야할지 몰라서 이렇게 넣음...

        elif condition == 'upload': #로컬 파일 업로드!!
            user_id = request.session.get('id_session', None)
            getlist = request.POST.getlist('arr[]', None)
            #print('getlist: ', getlist)

            new_list = []

            for index, value in enumerate(getlist):
                list = value.split(',')
                #print('list: ', list)
                filename = list[0]
                #print('filename: ', filename)


                audio = Audio.objects.filter(filename=filename).first() #DB에 동일한 파일명이 있는지 조회

                # 파일확장자가 .weba인 애들을 업로드할때 이 파일과 동일한 이름의 .wav파일이 있는지 확인해봐야함..(weba로 서버업로드되어서 wav로 변환되어서 사용하고 있을 가능성이 있어서)
                name, ext = os.path.splitext(filename)
                wav_flag = False
                if ext == '.weba':
                    wav_filename = name + '.wav'
                    audio2 = Audio.objects.filter(filename=wav_filename).first()
                    if audio2 != None:
                        wav_flag = True

                if audio != None or wav_flag == True: #원래 존재하는 오디오파일임
                    list.append('Y')
                    new_list.append(list)
                    continue

                list.append('N')
                new_list.append(list)

                filepath = self.get_filepath(request, filename)

                file = request.FILES.getlist('fileUpload[]', None)[index]  # 다중 파일을 가져올때는 getlist 사용. 그중에서 해당인덱스의 파일을 업로드
                # 서버에 오디오 파일 업로드
                f = open(filepath, 'wb')
                f.write(file.read())
                f.close()

                # 오디오 파일 길이 가져오기
                try:
                    sound = AudioSegment.from_file(filepath)
                    duration = sound.duration_seconds
                    duration = math.floor(duration)  # 밀리초 내림(버림)
                    duration = time.strftime('%H:%M:%S', time.gmtime(duration))  # seconds to hh:mm:ss
                except:
                    duration = None

                if ext == '.wav':
                    wav_filepath = filepath
                    is_split = 'N'
                else: # ext == '.weba':
                    wav_filepath = None
                    is_split = None

                # db에 저장
                Audio.objects.create(filename=filename,
                                     user_id=user_id,
                                     play_time=duration,
                                     filepath=filepath,
                                     patient_id=list[1],
                                     number_of_people=list[2],
                                     is_local_upload='Y',
                                     wav_filepath=wav_filepath,
                                     is_split=is_split,
                                     status='전송완료')

            '''
            #반복문 순회해서 각각의 파일을 서버로 업로드하는 코드 (다중파일 업로드)
            for file in request.FILES.getlist('fileUpload[]', None):  # 다중 파일을 가져올때는 getlist 사용해야하고, 반복문으로 각각 순회해야함
                # print('file: ', file) #파일명을 출력

                # 서버에 오디오 파일 업로드
                f = open(filepath, 'wb')
                f.write(file.read())
                f.close()
            '''
            return Response(status=200, data=dict(audio_file_info=new_list))
        elif condition == 'convert':
            audio_id = request.POST.get('audio_id', None)

            filepath = Audio.objects.filter(id=audio_id).values('filepath').first().get('filepath')
            filename = Audio.objects.filter(id=audio_id).values('filename').first().get('filename')
            play_time = Audio.objects.filter(id=audio_id).values('play_time').first().get('play_time')

            name, ext = os.path.splitext(filepath)
            wav_filepath = name + '.wav'

            name, ext = os.path.splitext(filename)
            wav_filename = name + '.wav'

            try:
                ffmpeg_tools.ffmpeg_extract_audio(filepath, wav_filepath, fps=16000)
                #sound = AudioSegment.from_file(filepath) #이 코드도 작동함
                #sound = sound.set_channels(1)
                #duration2 = sound.duration_seconds
                #print('duration: ', duration2)
                #sound.export(wav_filepath, format="wav")
                #b = os.path.getsize(wav_filepath)
                #print('b: ', b)

                #print(mediainfo(wav_filepath))

                # 혹시나 녹음파일 업로드할때 오디오 파일 길이를 못가져왔다면 이 시점에서 가져오기
                if play_time is None:
                    duration = App.file_duration(self, wav_filepath)
                    #print('durarion: ', duration)

                    h, m, s = [int(x) for x in duration.split(':')]
                    total_seconds = math.floor(datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds())

                    # DB 업데이트
                    Audio.objects.filter(id=audio_id).update(wav_filepath=wav_filepath, play_time=duration, is_split='N')
                else:
                    duration = play_time
                    total_seconds = None
                    # DB 업데이트
                    Audio.objects.filter(id=audio_id).update(wav_filepath=wav_filepath, is_split='N') #이미 오디오의길이는 db에 저장되어있으니 update할 필요 없음
                    
                return JsonResponse({'wav_filename': wav_filename, 'duration': duration, 'total_seconds': total_seconds})

            except Exception as e:
                print(e)
                #print('wav파일 변환에 실패하였습니다.')
                return HttpResponse(status=500)

        elif condition == 'split':
            audio_id = request.POST.get('audio_id', None)
            wav_filepath = Audio.objects.filter(id=audio_id).values('wav_filepath').first().get('wav_filepath')
            #print('wav_filepath: ', wav_filepath)

            self.split_audio(wav_filepath) #플라스크 사용 전의 방식

            #플라스크 서버 사용
            '''
            data = {'audio': wav_filepath}
            req = requests.post(url=r'http://127.0.0.1:9801/SP', json=data)

            text = req.text
            text_list = text.split('+*+*+')
            print('text_list: ', text_list)
            print('text_list[0] : ', text_list[0])

            for split_info in text_list:
                #dict_split_info = literal_eval(split_info) #str을 dict형식으로 바꿈
                json_acceptable_string = split_info.replace("'", "\"")
                dict_split_info = json.loads(json_acceptable_string)

                wav_file = dict_split_info['wav_file']
                split_audio_name = dict_split_info['split_audio_name']
                split_filename = dict_split_info['split_filename']
                text = dict_split_info['text']

                start = dict_split_info['start']
                end = dict_split_info['end']
                start_time = self.get_duration(float(start))
                end_time = self.get_duration(float(end))

                SplitAudio.objects.create(wav_filepath=wav_file, split_filepath=split_audio_name,
                                          split_filename=split_filename, text=text, start_time=start_time,
                                          end_time=end_time)
            '''
            Audio.objects.filter(id=audio_id).update(is_split='Y')

            return HttpResponse(status=status.HTTP_200_OK)


    # 플라스크 사용 전의 방식
    def split_audio(self, audio_file):
        SPLIT_AUDIO_PATH = os.path.dirname(audio_file) + os.sep + 'split'
        #print('SPLIT_AUDIO_PATH: ', SPLIT_AUDIO_PATH)
        if not os.path.isdir(SPLIT_AUDIO_PATH):
            os.makedirs(SPLIT_AUDIO_PATH)

        audio = AudioSegment.from_wav(audio_file)
        audio_file_name = audio_file.split(os.sep)[-1].split('.')[0]
        split_audio_dir = SPLIT_AUDIO_PATH + os.sep + audio_file_name
        os.makedirs(split_audio_dir, exist_ok=True)
        speech_range = silence.detect_nonsilent(audio, min_silence_len=500, silence_thresh=-40, seek_step=1)
        pad_ms = 500
        add_end_ms = 250
        pad_silence = AudioSegment.silent(duration=pad_ms)

        for i, [start, end] in enumerate(speech_range):
            split_audio = audio[start:end + add_end_ms]
            print(f'{start / 1000} ~ {end / 1000}')
            split_audio_name = "{}{}{}_{:03d}.wav".format(split_audio_dir, os.sep, audio_file_name, i)
            padded = pad_silence + split_audio + pad_silence
            padded.export(split_audio_name, format='wav')
            #out_f = padded.export(split_audio_name, format='wav')
            #out_f.close()

            response = transcribe_file(split_audio_name)
            text = ''
            word_list = []
            for result in response.results:
                text = result.alternatives[0].transcript
                words = result.alternatives[0].words
                for word in words:
                    word_info = [word.word, word.start_time.total_seconds(), word.end_time.total_seconds()]
                    word_list.append(word_info)

            if len(word_list) == 0:
                str_word_list = ''
            else:
                str_word_list = str(word_list)

            split_filename = "{}_{:03d}.wav".format(audio_file_name, i)

            start_time = self.get_duration(start)
            end_time = self.get_duration(end)

            SplitAudio.objects.create(wav_filepath=audio_file, split_filepath=split_audio_name, split_filename=split_filename, text=text, start_time=start_time, end_time=end_time, word_list=str_word_list)


    def get_duration(self, total_milliseconds):
        total_seconds = math.floor(total_milliseconds/1000)

        # get min and seconds first
        mm, ss = divmod(total_seconds, 60)
        # Get hours
        hh, mm = divmod(mm, 60)

        hh = format(hh, '02')
        mm = format(mm, '02')
        ss = format(ss, '02')

        get_duration = str(hh) + ':' + str(mm) + ':' + str(ss)

        return get_duration



    def speech_to_text(self, split_filepath):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        try:
            audio_recog = sr.AudioFile(split_filepath)
            with audio_recog as source:
                audio_data2 = recognizer.record(source)
            text = recognizer.recognize_google(audio_data=audio_data2, language="ko-KR")
        except Exception as e:
            text = ''
            #print(e)
        return text



    def get_filepath(self, request, filename):
        only_filename = os.path.splitext(filename)[0]
        file_extension = os.path.splitext(filename)[1]

        today = str(datetime.date.today())
        date_dir_path = today.replace('-', os.sep)
        save_dir = settings.MEDIA_ROOT + os.sep + date_dir_path + os.sep + 'local_upload'
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        filepath = save_dir + os.sep + filename

        # 업로드한 파일명이 겹치면 원래파일명에 (2),(3)...이런식으로 숫자를 붙여 저장 (실수로 같은 파일 업로드할수도 있으니)
        # 이렇게 하지 않으면 윈도우같은 경우는 파일이 덮어씌워진다.
        '''
        i = 2  # 초기식
        while os.path.isfile(filepath):  # 이미 존재하는 파일명이면 while문 안으로 들어감
            filepath = save_dir + os.sep + only_filename + '(' + str(i) + ')' + file_extension # 반복할 코드
            filename = only_filename + '(' + str(i) + ')' + file_extension
            i += 1  # 변화식
        '''
        return filepath


def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
        enable_word_time_offsets=True
    )

    response = client.recognize(config=config, audio=audio)

    return response


class App(APIView):
    def __init__(self):
        print('__init__ 호출')

    def __del__(self):
        print("객체가 없어졌어요!")

    def get(self, request):
        return redirect('/list')
        # user_id = request.session.get('id_session', None) #id_session에서 가져오는 값이 id 변수에 담기는데, id_session에 값이 없으면 id값을 None으로 주겠다.
        # #print('user_id: ', user_id)
        # if user_id is None:  # 세션이 존재하지않는다면 로그인 창 보여주기.
        #     return render(request, "user/login.html")
        # else:
            # return redirect('/list')
            # user = User.objects.filter(user_id=user_id).first()
            # #print('user: ', user)
            # if user.is_admin == 'T':
            #     #return render(request, "audio/alert.html")
            #     return redirect('/list')
            # else:
            #     #동의서 만료일 처리 부분
            #     today = datetime.datetime.today().date()
            #     yesterday = today - datetime.timedelta(days=1)
            #     expire_list = newPatient.objects.filter(delete_date__lte=yesterday, is_deleted='N').values('is_deleted', 'delete_date')
            #     if expire_list.count() > 0:
            #         expire_list.update(is_deleted='Y')

            #     audio_object_list = Audio.objects.filter(user_id=user_id, is_requested='Y')
            #     audio_id_list = []

            #     if audio_object_list.count() > 0:

            #         for audio_object in audio_object_list:
            #             #print('audio_object: ', audio_object.id)
            #             audio_id_list.append(audio_object.id)

            #     #print('audio_id_list: ', audio_id_list)
            #     department = Department.objects.filter(~Q(d_code='000')&~Q(d_code='998')&~Q(d_code='999')).order_by('d_code')#여기추가3
            #     department_list = list(department) #여기추가2
            #     return render(request, "audio/main.html", context=dict(user=user, audio_id_list=audio_id_list, param='main', department_list=department_list)) #여기추가2

    def main(self, request, name, id): #매개값으로 id가 꼭 필요한걸까..?
        if name == 'upload':
            #file = request.FILES['data'].read() # blob데이터 가져오기
            file = request.FILES['data'] # blob데이터 가져오기

            list = self.get_name(request, id, None)
            filepath = list[2]
            
            # 서버에 오디오 파일 업로드
            f = open(filepath, 'wb')
            f.write(file.read()) #file.read() 이렇게 해볼까...(원래는 f.write(file)이었음..)
            f.close()

            # 오디오 파일 길이 가져오기
            try:
                sound = AudioSegment.from_file(filepath)
                duration = sound.duration_seconds
                duration = math.floor(duration)  # 밀리초 내림(버림)
                duration = time.strftime('%H:%M:%S', time.gmtime(duration))  # seconds to hh:mm:ss
            except:
                duration = None


            department = request.POST.get('department', None)
            doctor = request.POST.get('doctor', None)

            # db에 저장
            reg_id = request.POST.get('reg_id', None)
            new = newPatient.objects.filter(reg_id=reg_id).values('reg_id', 'registered_at', 'delete_date', 'is_rejected').first()
            name = request.POST.get('name', None)
            gender = request.POST.get('gender', None)
            age = request.POST.get('age', None)
            if new is None:
                #print('여기 들어옴!!!')
                try:
                    newPatient.objects.create(reg_id=reg_id, patient_id=list[3], patient_name=name, patient_gender=gender, patient_age=age)
                except Exception as e: #db에 똑같은 환자번호가 insert되어서 에러날때..(지금 로직은 녹음 중지할때 /patient/check 해줘서 이런 에러 날가능성은 거의 없음)
                    #print("e: ", e)
                    p_list = newPatient.objects.filter(~Q(patient_id=None), ~Q(patient_id='')).values('patient_id')
                    p_new_list = []
                    for l in p_list:
                        try:
                            p_new_list.append(int(l['patient_id']))
                        except:
                            continue
                    new_num = '{:05d}'.format(findSmallestMissing(p_new_list))

                    newPatient.objects.create(reg_id=reg_id, patient_id=new_num, patient_name=name, patient_gender=gender, patient_age=age)

                    new_list = self.get_name(request, id, new_num)
                    Audio.objects.create(filename=new_list[0], user_id=list[1], play_time=duration, filepath=new_list[2],
                                         patient_id=new_num, number_of_people=list[6], status='전송완료', d_code=department, doctor_id=doctor)
                    #업로드된 실제 filepath에서 맞는 filepath로 파일을 이동시켜줘야함
                    os.replace(list[2], new_list[2])
                    return HttpResponse(filepath, status=status.HTTP_200_OK)

            else: #혹시 기존등록한 환자 정보 수정할까봐 이렇게 처리함 #여기추가214

                # 11월 14일 이전 등록 환자는 등록날짜 갱신해줘야함(삭제날짜도)
                date = datetime.date(2022, 11, 14)
                if new['is_rejected'] is None and new['registered_at'] < date and new['delete_date'] is None:
                    str_reg_date = request.POST.get('reg_date', None)
                    reg_date = datetime.datetime.strptime(str_reg_date, '%Y-%m-%d').date()
                    delete_date = reg_date + relativedelta(months=6)
                    newPatient.objects.filter(reg_id=reg_id).update(registered_at=reg_date, delete_date=delete_date)

                #거부취소환자의 경우도 등록날짜와 삭제날짜 갱신해줘야함, 환자번호 부여해주기
                if new['is_rejected'] == 'N':
                    str_reg_date = request.POST.get('reg_date', None)
                    reg_date = datetime.datetime.strptime(str_reg_date, '%Y-%m-%d').date()
                    delete_date = reg_date + relativedelta(months=6)

                    p_list = newPatient.objects.filter(~Q(patient_id=None), ~Q(patient_id='')).values('patient_id')
                    p_new_list = []
                    for l in p_list:
                        try:
                            p_new_list.append(int(l['patient_id']))
                        except:
                            continue
                    new_num = '{:05d}'.format(findSmallestMissing(p_new_list))
                    newPatient.objects.filter(reg_id=reg_id).update(registered_at=reg_date, delete_date=delete_date, patient_id=new_num, is_rejected=None)
                    if list[3] == '':
                        list[3] = new_num

            Audio.objects.create(filename=list[0], user_id=list[1], play_time=duration, filepath=list[2], patient_id=list[3],
                                 number_of_people=list[6], status='전송완료', d_code=department, doctor_id=doctor)

            return HttpResponse(filepath, status=status.HTTP_200_OK)
        elif name == 'delete': #녹음삭제 요청
            self.delete_audio(request, id)  # db에 update (is_deleted를 N에서 Y로 바꿈)
            return HttpResponse(status=status.HTTP_200_OK)

    def get_name(self, request, id, new_num):
        user_id = request.session.get('id_session', None)
        list = []

        doctor = request.POST.get('doctor', None)
        gender = request.POST.get('gender', None)
        age = request.POST.get('age', None)
        count = request.POST.get('count', None)
        patient_id = request.POST.get('patient_id', None)
        if new_num is not None:
            patient_id = new_num

        filename = doctor + '_' + user_id + '_' + id + '_' + patient_id + '_' + count + '.weba'

        #이 코드는 wav파일을 날짜별로 저장하기 전에 사용했던 코드
        #filepath = settings.MEDIA_ROOT + os.sep + filename
        #print('filepath: ', filepath)

        #wav파일 날짜별로 저장
        today = str(datetime.date.today())
        date_dir_path = today.replace('-', os.sep)
        #print('date_dir_path: ', date_dir_path)
        save_dir = settings.MEDIA_ROOT + os.sep + date_dir_path
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        filepath = save_dir + os.sep + filename
        list.extend([filename, user_id, filepath, patient_id, gender, age, count, save_dir])
        return list


    def get_filename(self, request, id):
        user_id = request.session.get('id_session', None)
        doctor = request.POST.get('doctor', None)
        patient_id = request.POST.get('patient_id', None)
        count = request.POST.get('count', None)
        filename = doctor + '_' + user_id + '_' + id + '_' + patient_id + '_' + count + '.weba'
        return filename

    def file_duration(self, filepath):
        duration = librosa.get_duration(filename=filepath)
        duration = math.floor(duration)  # 밀리초 내림(버림)
        duration = time.strftime('%H:%M:%S', time.gmtime(duration))  # seconds to hh:mm:ss
        return duration

    def delete_audio(self, request, id):
        filename = self.get_filename(request, id)
        print('filename: ', filename)
        delete_date = datetime.datetime.combine(timezone.now(), datetime.time.min) + datetime.timedelta(days=1)


        Audio.objects.filter(filename=filename).update(is_deleted='Y', delete_date=delete_date)



class StreamView(View):
    def get(self, request, wav_filename):
        name, ext = os.path.splitext(wav_filename)
        filename = name + '.weba'

        audio_file = Audio.objects.filter(filename=filename).values('wav_filepath').first()
        if audio_file is None:
            audio_file = Audio.objects.filter(filename=wav_filename).values('wav_filepath').first()

        with open(audio_file['wav_filepath'], 'rb') as af:
            response = HttpResponse(af.read(), content_type='audio/wav')
            response['Content-Disposition'] = 'attachment; filename=%s' % wav_filename
            response['Accept-Ranges'] = 'bytes'
            response['X-Sendfile'] = wav_filename
            response['Content-Length'] = os.path.getsize(audio_file['wav_filepath'])
        return response


def get_patient_list(request):
    department = request.POST.get('department', '')

    if department == '':
        regex =r'^[9][0-9]{4}$'
    elif department == '001':
        regex= r'^[3,6-9][0-9]{4}$'
    elif department == '002':
        regex = r'^[0-5,7-9][0-9]{4}$'
    elif department == '003':
        regex = r'^[0-2,4-9][0-9]{4}$'
    else:
        regex = r'^[0-9][0-9]{4}$'

    patient_info = models.Patient.objects.filter(~Q(patient_id__regex=regex)).values('patient_id', 'patient_gender', 'patient_age').order_by('patient_id') #녹취환자 정보
    patient_list = []
    for patient in patient_info:
        patient_list.append(patient)

    if len(patient_list) == 0:
        return JsonResponse({'message': 'fail'})

    return JsonResponse({'message': 'success', 'patient_list': patient_list})

def get_patient_info(request, num):
    audio = Audio.objects.filter(id=num).values('patient_id', 'number_of_people', 'd_code', 'doctor_id').first()
    patient = newPatient.objects.filter(patient_id=audio['patient_id']).values('reg_id', 'registered_at', 'patient_name', 'patient_age', 'patient_gender').first()
    patient['registered_at'] = dateformat.format(patient['registered_at'], 'Y-m-d')
    record = {}
    record.update(audio)
    record.update(patient)
    record['number_of_people'] = int(record['number_of_people'])

    department = Department.objects.filter(Q(d_code='001') | Q(d_code='002') | Q(d_code='003')).order_by('d_code')
    department_list = list(department)
    doctor = Doctor.objects.filter(d_code=audio['d_code']).values('doctor_id', 'doctor_name')
    doctor_list = list(doctor)
    return render(request, 'audio/recording_info.html', context=dict(record=record, department_list=department_list, doctor_list=doctor_list))

def mod_patient_info(request, num):
    is_reg_area = json.loads(request.POST.get('regNumArea', 'false'))
    is_pat_area = json.loads(request.POST.get('patientArea', 'false'))
    is_rec_area = json.loads(request.POST.get('recordArea', 'false'))
    is_new = json.loads(request.POST.get('isNew', 'false'))
    reg_id = request.POST.get('regNum', '99999999')
    name = request.POST.get('name', '')
    age = request.POST.get('age', '1')
    gender = request.POST.get('gender', 'M')
    count = request.POST.get('count', '1')
    department = request.POST.get('department', '998')
    doctor = request.POST.get('doctor', '998-01')

    if is_reg_area: #등록번호수정
        if is_new: #새로등록하는환자
            p_list = newPatient.objects.filter(~Q(patient_id=None), ~Q(patient_id='')).values('patient_id')
            p_new_list = []
            for l in p_list:
                try:
                    p_new_list.append(int(l['patient_id']))
                except:
                    continue
            patient_id = '{:05d}'.format(findSmallestMissing(p_new_list))
            newPatient.objects.create(reg_id=reg_id, patient_id=patient_id, patient_name=name, patient_gender=gender, patient_age=age)
        else: #기존에등록한환자
            patient_id = newPatient.objects.filter(reg_id=reg_id).values('patient_id').first()['patient_id']

        Audio.objects.filter(id=num).values('id').update(patient_id=patient_id) #오디오파일에 환자연구번호 수정하기
    
    if is_pat_area: #환자정보수정
        if not is_new: #새로등록하는환자가 아니면
            newPatient.objects.filter(reg_id=reg_id).values('reg_id').update(patient_name=name, patient_gender=gender, patient_age=age)

    if is_rec_area: #녹취정보수정
        Audio.objects.filter(id=num).values('id').update(number_of_people=count, d_code=department, doctor_id=doctor)

    #DB접근, 실제경로파일 수정, DB수정(wav파일을 localupload한 경우는 count만 바꾸어주고 그어느것도 손대지않음, weba는 기본적으로 녹취웹에서 다운된 거라고 가정하고 코드작성함)
    audio = Audio.objects.filter(id=num).values('is_local_upload', 'number_of_people', 'filename', 'filepath', 'wav_filepath', 'patient_id', 'doctor_id').first()

    if audio['is_local_upload'] == 'Y' and '.wav' in audio['filename']:
        return HttpResponse(status=200)
    elif not is_reg_area and is_pat_area and not is_rec_area: #환자정보만 수정할경우 파일명이 바뀔 필요는 없음
        #print('여기여기여기~~~~')
        return HttpResponse(status=200)
    else:
        # 여기서부터 실경로로 접근해서 파일명바꾸고 db수정도 해야함. 글고 전사테이블명까지 다 조회해서 다 고쳐야함
        audio_filename = audio['filepath'].split('_')
        only_filepath = os.path.dirname(audio['filepath']) + os.sep + audio['doctor_id'] + '_' + audio_filename[1] + '_' + audio_filename[2] + '_' + audio['patient_id'] + '_' + count
        new_weba_filepath = only_filepath + '.weba'
        os.rename(audio['filepath'], new_weba_filepath)

        Audio.objects.filter(id=num).values('id').update(filepath=new_weba_filepath, filename=os.path.basename(new_weba_filepath))

        if audio['wav_filepath'] is None: #wav파일 변환 전
            return HttpResponse(status=200)

        # wav파일 변환 후
        new_wav_filepath = only_filepath + '.wav'
        os.rename(audio['wav_filepath'], new_wav_filepath)

        Audio.objects.filter(id=num).values('id').update(wav_filepath=new_wav_filepath)

        split_audio_list = SplitAudio.objects.filter(wav_filepath=audio['wav_filepath']).values('wav_filepath', 'split_filename', 'split_filepath')
        if len(split_audio_list) == 0: # 아직 split되기전..
            return HttpResponse(status=200)

        # split된 이후
        SplitAudio.objects.filter(wav_filepath=audio['wav_filepath']).values('wav_filepath').update(wav_filepath=new_wav_filepath)

        base_path = os.path.dirname(new_wav_filepath)
        only_wav_filename = os.path.splitext(os.path.basename(new_wav_filepath))[0]
        split_base_path = base_path + os.sep + 'split' + os.sep + os.path.splitext(os.path.basename(audio['filename']))[0]
        new_split_base_path = base_path + os.sep + 'split' + os.sep + only_wav_filename
        os.rename(split_base_path, new_split_base_path)

        flag = False
        for split_audio in split_audio_list:

            split_filename = only_wav_filename + '_' + split_audio['split_filename'].split('_')[-1]
            split_filepath = new_split_base_path + os.sep + split_filename
            os.rename(new_split_base_path + os.sep + split_audio['split_filename'], split_filepath)
            SplitAudio.objects.filter(split_filename=split_audio['split_filename']).values('split_filename').update(split_filepath=split_filepath, split_filename=split_filename)


            if flag is False:
                text = Text.objects.filter(split_filename=split_audio['split_filename']).values('split_filename').first()
                if text is None:
                    flag = True #한번 전사테이블에 해당 split컬럼이 존재하지 않는걸 안다면 더이상 여기 들어올필요가 없어서 flag변수를 두었다.
                else:
                    Text.objects.filter(split_filename=split_audio['split_filename']).values('split_filename').update(split_filename=split_filename)

    return HttpResponse(status=200)


def get_user_dept(request):
    d_code = request.POST.get('d_code', None)
    user_object_list = User.objects.filter(d_code=d_code).values('user_id')
    list = []

    if len(user_object_list) > 0 :
        for user in user_object_list:
            list.append(dict(user_id=user['user_id']))

    return JsonResponse({'list': list})


def mod_record_info(request):
    num = request.POST.get('num', None)
    user_id = request.POST.get('id', None)

    # db update
    Audio.objects.filter(id=num).values('id').update(user_id=user_id)

    audio = Audio.objects.filter(id=num).values('is_local_upload', 'number_of_people', 'filename', 'filepath', 'wav_filepath', 'doctor_id').first()

    if audio['is_local_upload'] == 'Y' and '.wav' in audio['filename']:
        return HttpResponse(status=200)
    else:
        audio_filename = audio['filepath'].split('_')
        path = os.path.split(audio_filename[0])

        only_filepath = path[0] + os.sep +  audio['doctor_id'] + '_' + user_id + '_' + audio_filename[2] + '_' + audio_filename[3] + '_' + os.path.splitext(audio_filename[4])[0]
        new_weba_filepath = path[0] + os.sep +  audio['doctor_id'] + '_' + user_id + '_' + audio_filename[2] + '_' + audio_filename[3] + '_' + audio_filename[4]
        os.rename(audio['filepath'], new_weba_filepath)

        Audio.objects.filter(id=num).values('id').update(filepath=new_weba_filepath, filename=os.path.basename(new_weba_filepath))

        if audio['wav_filepath'] is None: #wav파일 변환 전
            return HttpResponse(status=200)


        # wav파일 변환 후
        new_wav_filepath = only_filepath + '.wav'
        os.rename(audio['wav_filepath'], new_wav_filepath)

        Audio.objects.filter(id=num).values('id').update(wav_filepath=new_wav_filepath)

        split_audio_list = SplitAudio.objects.filter(wav_filepath=audio['wav_filepath']).values('wav_filepath', 'split_filename', 'split_filepath')
        if len(split_audio_list) == 0: # 아직 split되기전..
            return HttpResponse(status=200)

        # split된 이후
        SplitAudio.objects.filter(wav_filepath=audio['wav_filepath']).values('wav_filepath').update(wav_filepath=new_wav_filepath)

        base_path = os.path.dirname(new_wav_filepath)
        only_wav_filename = os.path.splitext(os.path.basename(new_wav_filepath))[0]
        split_base_path = base_path + os.sep + 'split' + os.sep + os.path.splitext(os.path.basename(audio['filename']))[0]
        new_split_base_path = base_path + os.sep + 'split' + os.sep + only_wav_filename
        os.rename(split_base_path, new_split_base_path)

        flag = False
        for split_audio in split_audio_list:

            split_filename = only_wav_filename + '_' + split_audio['split_filename'].split('_')[-1]
            split_filepath = new_split_base_path + os.sep + split_filename
            os.rename(new_split_base_path + os.sep + split_audio['split_filename'], split_filepath)
            SplitAudio.objects.filter(split_filename=split_audio['split_filename']).values('split_filename').update(split_filepath=split_filepath, split_filename=split_filename)


            if flag is False:
                text = Text.objects.filter(split_filename=split_audio['split_filename']).values('split_filename').first()
                if text is None:
                    flag = True #한번 전사테이블에 해당 split컬럼이 존재하지 않는걸 안다면 더이상 여기 들어올필요가 없어서 flag변수를 두었다.
                else:
                    Text.objects.filter(split_filename=split_audio['split_filename']).values('split_filename').update(split_filename=split_filename)

    return HttpResponse(status=200)


#확인요청현황부분

# 역대 확인요청 중 응답한거 출력
# sql문
# 1) is_requested = 'N' and text3 is Not None (확인요청이 N상태이면서 text3 필드가 내용이있음 --> 이미 응답하고 확인요청완료된거임)
# 2) is_requested = 'Y' and is_responded = 'Y' (확인요청도 들어오고 그에따른 응답도 한 상태. 아직 완료는 안 한 상황)
# 1)과 2)중 한가지만 만족하면 됨 (즉 or임)
def get_confirm_list(request):
    text_object_list = Text.objects.filter(Q(Q(is_requested='Y')&Q(is_responded='Y'))|Q(Q(is_requested='N')&Q(~Q(text3=None)))).values('split_filename', 'text3').order_by('id')

    if len(text_object_list) == 0:
        return JsonResponse({'message': 'fail'})
    list = []

    for text in text_object_list:
        split_num = os.path.splitext(text['split_filename'])[0].split('_')[-1]
        split_audio = SplitAudio.objects.filter(split_filename=text['split_filename']).values('wav_filepath').first()
        audio = Audio.objects.filter(wav_filepath=split_audio['wav_filepath']).values('id', 'filename', 'patient_id').first()
        filename = os.path.splitext(audio['filename'])[0] + '.wav'

        list.append(dict(patient_id=audio['patient_id'], filename=filename, id=audio['id'], split_num=split_num, text=text['text3']))

    sorted_list = sort_list_by_patient_id(list) #환자번호로 정렬
    return JsonResponse({'message': 'success', 'list': sorted_list})

# 역대 확인요청 중 응답안한거 출력
# sql문
# is_requested = 'Y' and (is_responded = 'N' or is_responded = null) (확인요청은 들어왔으나 아직 응답하지 않은 경우)
def get_confirm_list2(request):
    text_object_list = Text.objects.filter(Q(is_requested='Y')&Q(~Q(is_responded='Y'))).values('split_filename', 'text2').order_by('id')

    if len(text_object_list) == 0:
        return JsonResponse({'message': 'fail'})
    list = []

    for text in text_object_list:
        split_num = os.path.splitext(text['split_filename'])[0].split('_')[-1]
        split_audio = SplitAudio.objects.filter(split_filename=text['split_filename']).values('wav_filepath').first()
        audio = Audio.objects.filter(wav_filepath=split_audio['wav_filepath']).values('id', 'filename', 'patient_id').first()
        filename = os.path.splitext(audio['filename'])[0] + '.wav'

        list.append(dict(patient_id=audio['patient_id'], filename=filename, id=audio['id'], split_num=split_num, text=text['text2']))

    sorted_list = sort_list_by_patient_id(list) #환자번호로 정렬
    return JsonResponse({'message': 'success', 'list': sorted_list})


def sort_list_by_patient_id(list):
    return sorted(list, key=lambda k: k['patient_id'])


#여기추가2
def select_doctor(request):
    department = request.POST.get('value', None)
    #print(department)
    doctor = Doctor.objects.filter(d_code=department).values('doctor_id', 'doctor_name')
    doctor_list = list(doctor)
    return JsonResponse({'list': doctor_list})

def convert_weba_to_wav(request):
    weba_list = Audio.objects.filter(wav_filepath=None).values('id', 'filepath')
    if weba_list.count() > 0:
        for weba in weba_list:
            name, ext = os.path.splitext(weba['filepath'])
            wav_filepath = name + '.wav'
            try:
                ffmpeg_tools.ffmpeg_extract_audio(weba['filepath'], wav_filepath, fps=16000)
                Audio.objects.filter(id=weba['id']).update(wav_filepath=wav_filepath, is_split='N')
            except Exception as e:
                print(e)
                # print('wav파일 변환에 실패하였습니다.')
                continue
    return HttpResponse(status=200)


def findSmallestMissing(nums, left=None, right=None):
    # 좌우 초기화
    if left is None and right is None:
        (left, right) = (0, len(nums) - 1)

    # 기본 조건
    if left > right:
        return left

    mid = left + (right - left) // 2

    # 중간 인덱스가 해당 값과 일치하면 불일치
    # 는 오른쪽 절반에 있습니다.
    if nums[mid] == mid:
        return findSmallestMissing(nums, mid + 1, right)

    # 불일치는 왼쪽 절반에 있습니다.
    else:
        return findSmallestMissing(nums, left, mid - 1)