from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Department, Company


# Create your views here.

class Join(APIView):
    def get(self, request):
        user_id = request.session.get('id_session', None)
        #print('user_id: ', user_id)
        if user_id is not None:
            return redirect('/')

        #회사명
        company_object_list = Company.objects.values('c_code', 'c_name').order_by('c_code')
        company_list = []

        if len(company_object_list) > 0 :
            for company_object in company_object_list:
                company_list.append(company_object)

        #부서명
        department_object_list = Department.objects.filter(~Q(d_code='999')).values('d_code', 'd_name').order_by('d_code')
        department_list = []

        if len(department_object_list) > 0 :
            for department_object in department_object_list:
                department_list.append(department_object)

        return render(request, "user/join.html", context=dict(company_list=company_list, department_list=department_list))

    # 회원가입
    def post(self, request):
        # form태그로 전송할 때
        #id = request.data.get('id', None)
        #name = request.data.get('name', None)
        #password = request.data.get('password', None)
        #c_code = request.POST['company']
        id = request.POST.get('id', None)
        name = request.POST.get('name', None)
        password = request.POST.get('password', None)
        c_code = request.POST.get('c_code', None)


        if c_code == '01' or c_code == '02':
            d_code = '999'
        else:
            #d_code = request.POST['department'] #form태그로 전송할 때
            d_code = request.POST.get('d_code', None)

        user_type = request.POST.get('user_type', None)


        # User테이블에 값 넣기
        User.objects.create(user_id=id,
                            user_name=name,
                            password=make_password(password), # 패스워드를 암호화함
                            c_code=c_code,
                            d_code=d_code,
                            request_admin=user_type)

        #return render(request, "user/login.html") #redirect해야하나??
        return Response(status=200)  # 성공


class Login(APIView):
    def get(self, request):
        user_id = request.session.get('id_session', None)
        if user_id is not None:
            return redirect('/')
        return render(request, "user/login.html")

    def post(self, request):
        id = request.data.get('id', None)
        password = request.data.get('password', None)

        user = User.objects.filter(user_id=id).first()
        #print('user객체: ', user)
        
        if user is None: #가입하지 않은 사용자라면(user_id가 존재하지 않음)
            return Response(status=400, data=dict(message="존재하지 않는 아이디입니다."))
        else: #가입되어 있는 사용자라면(user_id 존재)
            if check_password(password, user.password): #지금 입력받은 password와 user객체 안에 있는 password가 같다면..(check_password가 알아서 암호 풀어주나봄..)
                request.session['id_session'] = user.user_id #id_session을 생성 #그냥 id로 해도 돼.

                is_admin = user.is_admin
                return Response(is_admin, status=200)  # 성공
                #return redirect('/') #이건 form태그일때
            else:
                return Response(status=400, data=dict(message="비밀번호가 일치하지 않습니다."))


class Logout(APIView):
    def get(self, request):
        request.session.flush()
        return redirect('/')
        #return render(request, "user/login.html") #위의 코드랑 이 코드랑 둘다가능...


class Check(APIView):
    def post(self, request, condition):
        if condition == 'user':
            id = request.POST.get('id', None)
            user = User.objects.filter(user_id=id).first()
            if user is None:
                message = 'success'
            else:
                message = 'fail'
            return Response(message, status=200)
        elif condition == 'password':
            pw = request.POST.get('pw', None)
            conPw = request.POST.get('conPw', None)

            if conPw == pw:
                message = 'success'
            else:
                message = 'fail'
            return Response(message, status=200)

