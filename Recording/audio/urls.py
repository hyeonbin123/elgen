from django.urls import path
import audio.views as views
from audio.views import App, Detail, File, PagingList, Patient, StreamView

app = App()
#print(app.chunk)
#del app
urlpatterns = [
    path('', app.as_view()),
    # path('list', List.as_view()),
    path('list/', PagingList.as_view()),
    path('list/<int:countperpage>/<int:pagenum>/<str:department>/<str:startdate>/<str:enddate>/<str:condition>/<str:pstatus>/<str:patientnum>/<str:order>', PagingList.as_view()),
    path('detail/<str:num>/<int:countperpage>/<int:pagenum>/<str:department>/<str:startdate>/<str:enddate>/<str:condition>/<str:pstatus>/<str:patientnum>/<str:order_by>', Detail.as_view()),
    path('file/<str:condition>', File.as_view()),
    path('rec/<str:name>/<str:id>', app.main),
    path('patient/<str:condition>', Patient.as_view()),
    path('stream/<str:wav_filename>', StreamView.as_view()),
    # path('list/fileDownloadList', views.get_file_download_list, name='fileDownloadList'),
    path('list/patientList', views.get_patient_list, name='patientList'),
    path('list/confirmList', views.get_confirm_list, name='confirmList'),
    path('list/confirmList2', views.get_confirm_list2, name='confirmList2'),
    path('detail/getPatientInfo/<str:num>', views.get_patient_info, name='getPatientInfo'),
    path('detail/modPatientInfo/<str:num>', views.mod_patient_info, name='modPatientInfo'),
    path('detail/getUserDept', views.get_user_dept, name='getUserDept'),
    path('detail/modRecordInfo', views.mod_record_info, name='modRecordInfo'),
    path('doctor', views.select_doctor, name='selectDoctor'),
    path('list/convert', views.convert_weba_to_wav, name='convert'),
]