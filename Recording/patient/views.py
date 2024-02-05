import ast
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, time
import math
from operator import itemgetter

from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from audio.models import Audio
from patient.models import newPatient, oldPatient
from user.models import User, Department


def calculate_page(pagenum, countperpage, total_count):
    button_num = 10
    end_page = (math.ceil(pagenum / button_num)) * button_num
    begin_page = (end_page - button_num) + 1
    prev = False if begin_page == 1 else True
    next = False if end_page * countperpage >= total_count else True
    if next == False :
        end_page = math.ceil(total_count / countperpage)
    nums = []
    for num in range(begin_page, end_page + 1):
        nums.append(num)
    calculate_list = dict(end_page=end_page, begin_page=begin_page, nums=nums, prev=prev, next=next)
    return calculate_list


class patientList(APIView):
    def get(self, request):
        user_id = request.session.get('id_session', None)
        if user_id is None:  # 세션이 존재하지않는다면 로그인 창 보여주기.
            return render(request, "user/login.html")
        else:
            user = User.objects.filter(user_id=user_id).values('is_admin', 'user_id', 'user_name').first()
            if user['is_admin'] != 'Y':
                return render(request, "audio/alert.html")

            pagenum = int(request.GET.get('pagenum', 1))  # 처음 페이지 들어가면 1 , 10이 기본값
            countperpage = int(request.GET.get('countperpage', 10))
            order = request.GET.get('order', 'desc')
            department = request.GET.get('department', 'all')
            #print('department: ', department)

            key = request.GET.get('key', 'name')
            value = request.GET.get('value', '')
            key_text = '성명'

            type = request.GET.get('type', 'recDate')
            type_name = '녹취일'
            start_date = request.GET.get('startdate', '')
            end_date = request.GET.get('enddate', '')

            if order == 'desc':
                order_by = '-patient_id'
            elif order == 'asc':
                order_by = 'patient_id'
            elif order == 'oldNum':
                order_by = F('old_patient_id').asc(nulls_last=True) #구환자번호가 없는 환자는 이 값이 null인데 null은 제일 마지막에 나오게 정렬되도록.
            elif order == 'regId':
                order_by = 'reg_id'
            elif order == 'name':
                order_by = 'patient_name'

            flag = False

            # 만료환자 여부
            is_deleted = request.GET.get('is_deleted', 'all')
            

            if value == '':
                if start_date == '': #날짜지정안됨
                    patient_list = newPatient.objects.filter(~Q(reg_id='99999999')).values('reg_id', 'patient_id', 'old_patient_id', 'patient_name', 'patient_gender', 'patient_age', 'registered_at', 'is_deleted', 'delete_date', 'is_requested').order_by(order_by)
                    
                    if is_deleted != 'all': #만료환자
                        patient_list = patient_list.filter(is_deleted=is_deleted)
                    
                    if department != 'all': #날짜 지정되지 않고 부서전체선택이 아니면
                        #audio_list = Audio.objects.filter(d_code=department).values('patient_id')
                        # print('audio_list: ', audio_list)
                        patient_id_list = []
                        reg_id_list = []

                        audio_list = Audio.objects.filter(d_code=department).values('patient_id').order_by('-patient_id').distinct()
                        for audio in list(audio_list):
                            patient_id_list.append(audio['patient_id'])

                        #print('patient_id_list: ', patient_id_list)

                        for patient_id in patient_id_list:
                            print('P: ', patient_id)
                            reg_id = newPatient.objects.filter(patient_id=patient_id).values('reg_id').first()['reg_id']
                            reg_id_list.append(reg_id)

                        patient_list = patient_list.filter(reg_id__in=reg_id_list)
                        if is_deleted != 'all':  # 만료환자
                            patient_list = patient_list.filter(is_deleted=is_deleted)

                else: #날짜가 지정됨
                    patient_list = []
                    first_date = datetime.strptime(start_date, '%Y-%m-%d')
                    last_date = datetime.strptime(end_date, '%Y-%m-%d')
                    if type == 'recDate':
                        last_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                        type_name = '녹취일'
                        audio_list = Audio.objects.filter(~Q(patient_id='00000')).filter(created_at__range=(first_date, last_date)).values('patient_id')

                        if department != 'all': #날짜검색을 이용하였고, 부서전체선택이 아니면
                            audio_list = audio_list.filter(d_code=department)

                        if audio_list.count() > 0:
                            for audio in audio_list:
                                new_p = newPatient.objects.filter(patient_id=audio['patient_id']).values('reg_id', 'patient_id', 'old_patient_id', 'patient_name', 'patient_gender', 'patient_age', 'registered_at', 'is_deleted', 'delete_date', 'is_requested').first()
                                #print('new_p: ', new_p)
                                if new_p is not None and new_p not in patient_list:
                                    patient_list.append(new_p)

                            if is_deleted != 'all':  # 만료환자
                                patient_list = patient_list.filter(is_deleted=is_deleted)

                            #이지점에서 patient_list를 정렬해주어야함
                            #print('patient_list: ', patient_list)
                            if len(patient_list) > 0:
                                if order == 'desc':
                                    patient_list = sorted(patient_list, key=itemgetter('patient_id'), reverse=True)  # 최신순으로 정렬
                                elif order == 'asc':
                                    patient_list = sorted(patient_list, key=itemgetter('patient_id'))
                                elif order == 'oldNum':
                                    patient_list = []
                                    flag = True # 이 정렬을 어떻게 해야할지 몰라서 일단 넘어감
                                elif order == 'regId':
                                    patient_list = sorted(patient_list, key=itemgetter('reg_id'))
                                elif order == 'name':
                                    patient_list = sorted(patient_list, key=itemgetter('patient_name'))

                    else: # elif type == 'regDate':
                        type_name = '동의서취득일'
                        patient_list = newPatient.objects.filter(~Q(reg_id='99999999')).filter(registered_at__range=(first_date, last_date)).values('reg_id', 'patient_id', 'old_patient_id', 'patient_name', 'patient_gender', 'patient_age', 'registered_at', 'is_deleted', 'delete_date').order_by(order_by)
                        if is_deleted != 'all':  # 만료환자
                            patient_list = patient_list.filter(is_deleted=is_deleted)
            else:
                if key == 'name':
                    patient_list = newPatient.objects.filter(~Q(reg_id='99999999')).filter(patient_name=value).values('reg_id', 'patient_id', 'old_patient_id', 'patient_name', 'patient_gender', 'patient_age', 'registered_at', 'is_deleted', 'delete_date', 'is_requested').order_by(order_by)
                elif key == 'regNum':
                    patient_list = newPatient.objects.filter(~Q(reg_id='99999999')).filter(reg_id=value).values('reg_id', 'patient_id', 'old_patient_id', 'patient_name', 'patient_gender', 'patient_age', 'registered_at', 'is_deleted', 'delete_date', 'is_requested').order_by(order_by)
                    key_text = '병원등록번호'
                elif key == 'patientNum':
                    patient_list = newPatient.objects.filter(~Q(reg_id='99999999')).filter(patient_id=value).values('reg_id', 'patient_id', 'old_patient_id', 'patient_name', 'patient_gender', 'patient_age', 'registered_at', 'is_deleted', 'delete_date', 'is_requested').order_by(order_by)
                    key_text = '연구번호'

                if is_deleted != 'all':  # 만료환자
                    patient_list = patient_list.filter(is_deleted=is_deleted)

            #print('patient_list: ', patient_list)

            # 녹취 거부대상자는 목록에서 제외
            patient_list = patient_list.filter(is_rejected=None)

            search_count = len(patient_list) # 검색(조회) 결과 개수
            patient_list = list(patient_list)

            #페이징
            paginator = Paginator(patient_list, countperpage)
            patient_list = paginator.get_page(pagenum)


            # 총녹음파일개수
            # [참고]일단 환자가 0명보단 않으니까 0명일 경우 ..발생할수있는 에러를 처리하지는 않았다.
            for patient in patient_list:
                #신환자번호로 조회
                total = Audio.objects.filter(patient_id=patient['patient_id']).values('patient_id').count()

                #구환자번호로 조회
                if patient['old_patient_id'] is not None:
                    #print('patient[old_patient_id]: ', patient['old_patient_id'])
                    old_nums = eval(patient['old_patient_id'])
                    old_total = 0
                    old_num_list = []
                    for old_num in old_nums:
                        #print(old_num)
                        old = Audio.objects.filter(patient_id=old_num).values('patient_id').count()
                        old_total += old
                        old_num_list.append(old_num)
                        patient['old_num_list'] = old_num_list

                    total += old_total
                patient['total'] = total
            #print(patient_list)

            #print('key: ', key)
            page_list = dict(count=search_count, pagenum=pagenum, countperpage=countperpage, order=order, department=department, key=key, value=value, key_text=key_text, type=type, type_name=type_name, start_date=start_date, end_date=end_date, is_deleted=is_deleted)
            #print(page_list)
            calculate_list = calculate_page(pagenum, countperpage, search_count)

            rec_department = Department.objects.filter(~Q(d_code='000')&~Q(d_code='998')&~Q(d_code='999')).order_by('d_code')
            department_list = list(rec_department)
            return render(request, "patient/patient_list.html", context=dict(user=user, param='patient_list', patient_list=patient_list, page_list=page_list, calculate_list=calculate_list, department_list=department_list, flag=flag))


def patient_record_list(request):
    reg_id = request.POST.get('reg_id', None)
    new_patient_id = newPatient.objects.filter(reg_id=reg_id).values('patient_id').first()['patient_id']
    old_patient_query = oldPatient.objects.filter(reg_id=reg_id).values('old_patient_id')

    new_audio_list = Audio.objects.filter(patient_id=new_patient_id).values('id', 'filename', 'created_at', 'play_time').order_by('-id')
    #print('new_audio_list: ', new_audio_list)
    total_list = []

    if new_audio_list.count() > 0:  # 신환자번호로 녹음된 녹음파일이 1개라도 있으면
        for new in new_audio_list:
            total_list.append(new)

    if old_patient_query.count() == 0: #구환자번호가 없으면
        return JsonResponse({'list': total_list}) # 신환자번호로 녹음된 파일이 1개도 없다면 빈 리스트를 리턴

    # 구환자번호가 존재할 경우
    for patient in list(old_patient_query):
        #print("patient['old_patient_id']: ", patient['old_patient_id'])
        old_audio_list = Audio.objects.filter(patient_id=patient['old_patient_id']).values('id', 'filename', 'created_at', 'play_time').order_by('-id')
        if old_audio_list.count() > 0:
            for old in old_audio_list:
                total_list.append(old)

    total_list = sorted(total_list, key=itemgetter('id'), reverse=True) #최신순으로 정렬
    return JsonResponse({'list': total_list})


def modify_patient(request):
    reg_id = request.POST.get('reg_id', None)
    name = request.POST.get('name', None)
    age = request.POST.get('age', None)
    gender = request.POST.get('gender', None)
    newPatient.objects.filter(reg_id=reg_id).update(patient_name=name, patient_age=age, patient_gender=gender)
    return HttpResponse(status=200)

def delete_patient(request):
    reg_id = request.POST.get('reg_id', None)
    patient = newPatient.objects.filter(reg_id=reg_id).values('patient_id')
    if patient is not None:
        delete_date = datetime.combine(timezone.now(), time.min) + timedelta(days=1)
        audio =  Audio.objects.filter(patient_id=patient.first()['patient_id']).values('patient_id')
        audio.update(is_deleted='Y', delete_date=delete_date, delete_reason='병원등록번호 삭제에 따른 파일삭제') #이 다음 실제파일도 삭제하여야함
        patient.update(is_requested='Y', request_date=delete_date)
    return HttpResponse(status=200)

def delete_cancel(request):
    reg_id = request.POST.get('reg_id', None)
    patient = newPatient.objects.filter(reg_id=reg_id).values('patient_id')
    if patient is not None:
        audio =  Audio.objects.filter(patient_id=patient.first()['patient_id']).values('patient_id')
        audio.update(is_deleted='N', delete_date=None, delete_reason=None)
        patient.update(is_requested=None, request_date=None)
    return HttpResponse(status=200)


#거부환자목록
def reject_patient_list(request):
    patient_list = newPatient.objects.filter(is_rejected='Y').values('patient_name', 'reg_id', 'patient_gender', 'patient_age', 'reject_date').order_by('-reject_date')
    return render(request, 'patient/reject_list.html', context=dict(patient_list=list(patient_list)))

#거부환자정보수정
def reject_patient_detail(request, reg_id):
    patient_list = newPatient.objects.filter(reg_id=reg_id).values('patient_name', 'reg_id', 'patient_gender', 'patient_age').first()
    return HttpResponse(status=200)

#동의서취득일수정
def modify_reg_date(request):
    reg_id = request.POST.get('reg_id', None)
    patient = newPatient.objects.filter(reg_id=reg_id).values('reg_id').first()
    if patient is not None:
        reg_date = request.POST.get('reg_date', None)
        reg_date = datetime.strptime(reg_date, '%Y-%m-%d')
        delete_date = reg_date + relativedelta(months=6)
        newPatient.objects.filter(reg_id=reg_id).values('reg_id').update(registered_at=reg_date, delete_date=delete_date)
    return HttpResponse(status=200)

#병원등록번호수정
def modify_reg_num(request):
    reg_id = request.POST.get('reg_id', None)
    prev_reg_id = request.POST.get('prev_reg_id', None)
    patient = newPatient.objects.filter(reg_id=reg_id).values('reg_id', 'is_rejected').first()
    if patient is not None:
        if patient['is_rejected'] is None:
            return JsonResponse(status=400, data=dict(message="이미 등록되어 있는 환자 번호입니다."))
        elif patient['is_rejected'] == 'Y':
            return JsonResponse(status=400, data=dict(message="녹취 거부 대상자로 등록된 번호입니다."))
        elif patient['is_rejected'] == 'N':
            newPatient.objects.filter(reg_id=reg_id).delete()

    newPatient.objects.filter(reg_id=prev_reg_id).values('reg_id').update(reg_id=reg_id)
    return HttpResponse(status=200)

#거부대상자목록에서 삭제
def reject_delete(request):
    reg_id = request.POST.get('reg_id', None)
    newPatient.objects.filter(reg_id=reg_id).update(is_rejected='N', reject_date=None)
    return HttpResponse(status=200)