"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from config import settings
from patient import views
from patient.views import patientList
from reply.views import Reply, ReReply
from user.views import Login, Join, Logout, Check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('audio.urls')),
    path('transcription/', include('transcription.urls')),

    path('join', Join.as_view()),
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('check/<str:condition>', Check.as_view()),

    path('reply/<str:condition>', Reply.as_view()),
    path('reReply/<str:condition>/<str:reply_id>', ReReply.as_view()),

    path('patientList/', patientList.as_view()),
    path('patientList/recList', views.patient_record_list, name='patientRecList'),
    path('patientList/modify', views.modify_patient, name='modifyPatient'),
    path('patientList/delete', views.delete_patient, name='deletePatient'),
    path('patientList/rejectList', views.reject_patient_list, name='rejectPatientList'),
    path('patientList/modRegDate', views.modify_reg_date, name='modifyRegDate'),
    path('patientList/deleteCancel', views.delete_cancel, name='deleteCancel'),
    path('patientList/modifyRegNum', views.modify_reg_num, name='modifyRegNum'),
    path('patientList/rejectDelete', views.reject_delete, name='rejectDelete'),
    path('patientList/rejectDetail/<str:reg_id>', views.reject_patient_detail, name='rejectDetail'),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
