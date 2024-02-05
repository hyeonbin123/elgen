from django.urls import path

import transcription.views as views
from transcription.views import Transcription, StreamView

urlpatterns = [
    path('<str:order>/<str:condition>/', Transcription.as_view()),
    path('stream/<str:split_filename>', StreamView.as_view()),
    path('regConfirmModal/', views.confirm_registration, name='confirmRegistration'),
    path('saveTxtFile/', views.save_txt_file, name='saveTxtFile'),
    path('stop/', views.stop_transcription, name='stopTranscription'),
    path('stopCancel/', views.stop_cancel_transcription, name='stopCancelTranscription'),
]