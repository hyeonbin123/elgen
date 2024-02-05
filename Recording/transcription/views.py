import os

from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views import View
from rest_framework import status
from rest_framework.views import APIView

from audio.models import Audio
from transcription.models import SplitAudio, Text


class Transcription(APIView):
    def post(self, request, order, condition):
        if order == '1':
            if condition == 'begin': #전사작업시작
                btn_html = request.POST.get('thisBtnHtml', None)
                board_id = request.POST.get('board_id', None)
                wav_filepath = request.POST.get('wav_filepath', None)

                if btn_html == '전사시작':
                    split_audio_list = SplitAudio.objects.filter(wav_filepath=wav_filepath).order_by('id')
                    for split_audio in split_audio_list:
                        Text.objects.create(split_filename=split_audio.split_filename)

                #전사재시작은 위의 과정을 거칠필요가없다. 바로 여기로 내려옴
                Audio.objects.filter(id=board_id).update(status='전사중')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'cancel': #전사초기화
                board_id = request.POST.get('board_id', None)
                wav_filepath = request.POST.get('wav_filepath', None)
                # print('wav_filepath: ', wav_filepath)

                split_audio_list = SplitAudio.objects.filter(wav_filepath=wav_filepath).order_by('id')
                for split_audio in split_audio_list:
                    Text.objects.filter(split_filename=split_audio.split_filename).delete()

                Audio.objects.filter(id=board_id).update(status='전송완료')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'regist':
                split_filename = request.POST.get('split_filename', None)
                text = request.POST.get('text', None)
                speaker1 = request.POST.get('radioVal', None)
                user_id = request.session.get('id_session', None)
                created_at = timezone.now()

                Text.objects.filter(split_filename=split_filename).update(text1=text, text1_user_cid=user_id, text1_created_at=created_at, speaker1=speaker1)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'modify':
                split_filename = request.POST.get('split_filename', None)
                text = request.POST.get('text', None)
                user_id = request.session.get('id_session', None)
                modified_at = timezone.now()
                speaker1 = request.POST.get('radioVal', None)

                Text.objects.filter(split_filename=split_filename).update(text1=text, text1_user_mid=user_id, text1_modified_at=modified_at, speaker1=speaker1)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'modifyCancel':
                split_filename = request.POST.get('split_filename', None)
                text = Text.objects.filter(split_filename=split_filename).first()
                return JsonResponse({'text': text.text1, 'speaker': text.speaker1})
            elif condition == 'completeCheck':
                wav_filepath = request.POST.get('wav_filepath', None)
                flag = False
                for object in SplitAudio.objects.filter(wav_filepath=wav_filepath):
                    text = Text.objects.filter(split_filename=object.split_filename).first()
                    if text.is_deleted == 'N' and text.is_sound == 'N':
                        if text.text1 is None:
                            flag = True
                            return HttpResponse(flag, status=status.HTTP_200_OK)
                    else: # 전사할수없는 경우(삭제나 소리 입력한경우)
                        continue
                return HttpResponse(flag, status=status.HTTP_200_OK)
            elif condition == 'complete':
                board_id = request.POST.get('board_id', None)
                Audio.objects.filter(id=board_id).update(status='전사완료')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'undo':
                split_filename = request.POST.get('split_filename', None)
                text = Text.objects.filter(split_filename=split_filename).first()
                if text.text1 == None or text.text1 == '':
                    split_audio = SplitAudio.objects.filter(split_filename=split_filename).first()
                    return_text = split_audio.text
                else:
                    return_text = text.text1
                return HttpResponse(return_text, status=status.HTTP_200_OK)
            elif condition == 'text':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_sound='N', sound=None, is_first_sound='N', first_sound=None)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'sound':
                split_filename = request.POST.get('split_filename', None)
                sound = request.POST.get('sound', None)
                Text.objects.filter(split_filename=split_filename).update(is_sound='Y', sound=sound, is_first_sound='Y', first_sound=sound, is_deleted='N', is_first_deleted='N')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'delete':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_deleted='Y', is_first_deleted='Y', is_sound='N', sound=None, is_first_sound='N', first_sound=None)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'deleteCancel':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_deleted='N', is_first_deleted='N')
                return HttpResponse(status=status.HTTP_200_OK)
        if order == '2':
            if condition == 'begin':
                board_id = request.POST.get('board_id', None)
                Audio.objects.filter(id=board_id).update(status='분석중')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'cancel': #분석초기화
                board_id = request.POST.get('board_id', None)
                wav_filepath = request.POST.get('wav_filepath', None)

                split_audio_list = SplitAudio.objects.filter(wav_filepath=wav_filepath).order_by('id')
                for split_audio in split_audio_list:
                    text = Text.objects.filter(split_filename=split_audio.split_filename).first()
                    Text.objects.filter(split_filename=split_audio.split_filename).update(text2=None, text2_user_cid=None, text2_created_at=None, text2_user_mid=None, text2_modified_at=None, text3=None, text3_user_cid=None, text3_created_at=None, text3_user_mid=None, text3_modified_at=None, is_requested='N', is_responded=None, is_deleted=text.is_first_deleted, is_sound=text.is_first_sound, sound=text.first_sound)
                Audio.objects.filter(id=board_id).update(status='전사완료', is_requested='N')
                return HttpResponse(status=status.HTTP_200_OK)

            elif condition == 'regist':
                split_filename = request.POST.get('split_filename', None)
                text = request.POST.get('text', None)
                speaker2 = request.POST.get('radioVal', None)
                user_id = request.session.get('id_session', None)
                created_at = timezone.now()

                Text.objects.filter(split_filename=split_filename).update(text2=text, text2_user_cid=user_id, text2_created_at=created_at, speaker2=speaker2)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'modify':
                split_filename = request.POST.get('split_filename', None)
                text = request.POST.get('text', None)
                user_id = request.session.get('id_session', None)
                modified_at = timezone.now()
                speaker2 = request.POST.get('radioVal', None)

                Text.objects.filter(split_filename=split_filename).update(text2=text, text2_user_mid=user_id, text2_modified_at=modified_at, speaker2=speaker2)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'modifyCancel':
                split_filename = request.POST.get('split_filename', None)
                text = Text.objects.filter(split_filename=split_filename).first()
                return JsonResponse({'text': text.text2, 'speaker': text.speaker2})
            elif condition == 'completeCheck':
                wav_filepath = request.POST.get('wav_filepath', None)
                flag = 'False'
                for object in SplitAudio.objects.filter(wav_filepath=wav_filepath):
                    text = Text.objects.filter(split_filename=object.split_filename).first()
                    if text.is_deleted == 'N' and text.is_sound == 'N':
                        #if text.text2 is None:
                        #    flag = 'True'
                        #    return HttpResponse(flag, status=status.HTTP_200_OK)
                        if text.is_requested == 'Y' and text.is_responded != 'Y':
                            flag = 'True2'
                            return HttpResponse(flag, status=status.HTTP_200_OK)
                    else: # 전사할수없는 경우(삭제나 소리 입력한경우)
                        continue
                return HttpResponse(flag, status=status.HTTP_200_OK)
            elif condition == 'complete':
                board_id = request.POST.get('board_id', None)
                Audio.objects.filter(id=board_id).update(status='분석완료')
                user_id = request.session.get('id_session', None)
                created_at = timezone.now()

                #flag = request.POST.get('flag', None) #boolean타입 아니고 str임
                #if flag == 'true': # split된 각각의 오디오파일 확인요청완료 작업을 해주어야함.
                Audio.objects.filter(id=board_id).update(is_requested='N')

                # 각파일별 is_requested, is_responded도 N으로 바꿔주기
                wav_filepath = request.POST.get('wav_filepath', None)
                split_filenames = SplitAudio.objects.filter(wav_filepath=wav_filepath).values('split_filename')

                for split_filename in split_filenames:

                    new_split_filename = split_filename['split_filename']
                    text = Text.objects.filter(split_filename=new_split_filename)
                    first_text = text.values('text1', 'text2').first()

                    if first_text['text2'] is None:
                        text.update(text2=first_text['text1'], text2_user_cid=user_id, text2_created_at=created_at)

                    text.update(is_requested='N')
                    text.update(is_responded='N')

                try:
                    getTxt(board_id)
                    # result = 'success'
                except:
                    # result = 'txtFail'
                    pass
                return HttpResponse(status=status.HTTP_200_OK)

            elif condition == 'confirm':
                board_id = request.POST.get('board_id', None)
                wav_filepath = request.POST.get('wav_filepath', None)
                filename = request.POST.get('split_filename', None)
                kind = request.POST.get('kind', None)

                if kind == 'confirm2':
                    Audio.objects.filter(id=board_id).update(is_requested='Y')
                    Text.objects.filter(split_filename=filename).update(is_requested='Y')

                    text = Text.objects.filter(split_filename=filename).first()
                    if text.is_responded == 'Y':
                        Text.objects.filter(split_filename=filename).update(is_responded='N')
                    return HttpResponse(status=status.HTTP_200_OK)

                else: #kind == 'cancel' (확인요청 취소)
                    Text.objects.filter(split_filename=filename).update(is_requested='N')
                    split_filenames = SplitAudio.objects.filter(wav_filepath=wav_filepath).values('split_filename')

                    flag = False

                    for split_filename in split_filenames:
                        new_split_filename = split_filename['split_filename']
                        is_requested = Text.objects.filter(split_filename=new_split_filename).values('is_requested').first()['is_requested']
                        #print('is_requested: ', is_requested)
                        if is_requested == 'Y':
                            flag = True
                            return HttpResponse(status=status.HTTP_200_OK) #여기 그냥 return으로 했다가 계속 에러남..

                    if flag == False:
                        Audio.objects.filter(id=board_id).update(is_requested='N')
                    return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'undo':
                split_filename = request.POST.get('split_filename', None)
                text = Text.objects.filter(split_filename=split_filename).first()
                if text.text2 == None or text.text2 == '':
                    if text.text1 == None or text.text1 == '':
                        split_audio = SplitAudio.objects.filter(split_filename=split_filename).first()
                        return_text = split_audio.text
                    else:
                        return_text = text.text1
                else:
                    return_text = text.text2

                #print('return_text: ', return_text)
                return HttpResponse(return_text, status=status.HTTP_200_OK)
            elif condition == 'text':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_sound='N', sound=None)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'sound':
                split_filename = request.POST.get('split_filename', None)
                sound = request.POST.get('sound', None)
                Text.objects.filter(split_filename=split_filename).update(is_sound='Y', sound=sound, is_deleted='N')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'delete':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_deleted='Y', is_sound='N', sound=None)
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'deleteCancel':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_deleted='N')
                return HttpResponse(status=status.HTTP_200_OK)
        if order == '3':
            if condition == 'regist':
                split_filename = request.POST.get('split_filename', None)
                text = request.POST.get('text', None)
                user_id = request.session.get('id_session', None)
                created_at = timezone.now()

                Text.objects.filter(split_filename=split_filename).update(text3=text, text3_user_cid=user_id,
                                                                          text3_created_at=created_at, is_responded='Y')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'modify':
                split_filename = request.POST.get('split_filename', None)
                text = request.POST.get('text', None)
                user_id = request.session.get('id_session', None)
                modified_at = timezone.now()

                Text.objects.filter(split_filename=split_filename).update(text3=text, text3_user_mid=user_id, text3_modified_at=modified_at, is_responded='Y')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'modifyCancel':
                split_filename = request.POST.get('split_filename', None)
                text3_dict = Text.objects.filter(split_filename=split_filename).values('text3').first()
                text3 = text3_dict['text3']
                return HttpResponse(text3, status=status.HTTP_200_OK)
            elif condition == 'completeCheck':
                wav_filepath = request.POST.get('wav_filepath', None)
                flag = 'False'
                for object in SplitAudio.objects.filter(wav_filepath=wav_filepath):
                    text = Text.objects.filter(split_filename=object.split_filename).first()
                    if text.is_requested == 'Y':
                        if text.text3 is None:
                            flag = 'True3'
                            return HttpResponse(flag, status=status.HTTP_200_OK)
                return HttpResponse(flag, status=status.HTTP_200_OK)
            elif condition == 'complete':
                board_id = request.POST.get('board_id', None)
                Audio.objects.filter(id=board_id).update(is_requested='N')

                #각파일별 is_requested, is_responded도 N으로 바꿔주기
                wav_filepath = request.POST.get('wav_filepath', None)
                split_filenames = SplitAudio.objects.filter(wav_filepath=wav_filepath).values('split_filename')

                for split_filename in split_filenames:
                    new_split_filename = split_filename['split_filename']
                    Text.objects.filter(split_filename=new_split_filename).update(is_requested='N')
                    Text.objects.filter(split_filename=new_split_filename).update(is_responded='N')

                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'undo':
                split_filename = request.POST.get('split_filename', None)
                text = Text.objects.filter(split_filename=split_filename).first()
                if text.text3 == None or text.text3 == '':
                    if text.text2 == None or text.text2 == '':
                        if text.text1 == None or text.text1 == '':
                            split_audio = SplitAudio.objects.filter(split_filename=split_filename).first()
                            return_text = split_audio.text
                        else:
                            return_text = text.text1
                    else:
                        return_text = text.text2
                else:
                    return_text = text.text3
                return HttpResponse(return_text, status=status.HTTP_200_OK)
            elif condition == 'text':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_sound='N', sound=None, is_responded='N')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'sound':
                split_filename = request.POST.get('split_filename', None)
                sound = request.POST.get('sound', None)
                Text.objects.filter(split_filename=split_filename).update(is_sound='Y', sound=sound, is_deleted='N', is_responded='Y')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'delete':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_deleted='Y', is_sound='N', sound=None, is_responded='Y')
                return HttpResponse(status=status.HTTP_200_OK)
            elif condition == 'deleteCancel':
                split_filename = request.POST.get('split_filename', None)
                Text.objects.filter(split_filename=split_filename).update(is_deleted='N', is_responded='N')
                return HttpResponse(status=status.HTTP_200_OK)


class StreamView(View):
    def get(self, request, split_filename):

        audio_file = SplitAudio.objects.filter(split_filename=split_filename).values('split_filepath').first()
        # print(audio_file)

        with open(audio_file['split_filepath'], 'rb') as af:
            response = HttpResponse(af.read(), content_type='audio/wav')
            response['Content-Disposition'] = 'attachment; filename=%s' % split_filename
            response['Accept-Ranges'] = 'bytes'
            response['X-Sendfile'] = split_filename
            response['Content-Length'] = os.path.getsize(audio_file['split_filepath'])
        return response



def getTxt(board_id):
    audio = Audio.objects.filter(id=board_id).values('wav_filepath').first()
    if audio is None:
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # 이게 맞는 응답인가..?
    else:
        script = ''
        list = SplitAudio.objects.filter(wav_filepath=audio['wav_filepath']).values('split_filename', 'start_time', 'end_time')
        for l in list:
            start_time = l['start_time']
            end_time = l['end_time']
            split_filename_num = os.path.splitext(l['split_filename'])[0].split('_')[-1]
            print(split_filename_num)

            text = Text.objects.filter(split_filename=l['split_filename']).values('text2', 'is_deleted', 'is_sound', 'sound').first()
            if text['is_deleted'] == 'Y':
                text_area = '[전사할 텍스트 없음] 삭제된 파일입니다.'
            elif text['is_sound'] == 'Y':
                text_area = '[전사할 텍스트 없음] ' + str(text['sound'])
            else:
                text_area = str(text['text2'])

            trans = split_filename_num + ' [' + start_time + ' ~ ' + end_time + '] ' + text_area + '\n'
            script += trans

    # 서버로 txt파일 업로드
    text_filepath = os.path.splitext(audio['wav_filepath'])[0] + '.txt'
    f = open(text_filepath, 'w', encoding='UTF8')
    f.write(script)
    f.close()


def confirm_registration(request):
    board_id = request.POST.get('board_id', None)
    order = request.POST.get('order', None)

    text_number = 'text' + order
    audio = Audio.objects.filter(id=board_id).values('wav_filepath').first()
    if audio is None:
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # 이게 맞는 응답인가..?

    split_audio_object_list = SplitAudio.objects.filter(wav_filepath=audio['wav_filepath']).values('split_filename').order_by('id')

    split_num_list = []
    for object in split_audio_object_list:
        registerd_object = Text.objects.filter(split_filename=object['split_filename']).values('split_filename', text_number, 'is_sound', 'is_deleted').first()
        if registerd_object[text_number] is None and registerd_object['is_sound'] == 'N' and registerd_object['is_deleted'] == 'N': #미등록 조건이 이거밖에 없으려나..?
            split_num = os.path.splitext(registerd_object['split_filename'])[0].split('_')[-1]
            split_num_list.append(split_num)

    return JsonResponse({'list': split_num_list})


def save_txt_file(request):
    status = request.POST.get('status', None)
    wav_filepath = request.POST.get('wav_filepath', None)

    split_audio_object_list = SplitAudio.objects.filter(wav_filepath=wav_filepath).values('split_filename', 'split_filepath', 'text').order_by('id')

    if status == '전송완료' or status == '전사중':
        for object in split_audio_object_list:
            txt_filepath = str(os.path.splitext(object['split_filepath'])[0]) + '.txt'

            if object['text'] != '':
                with open(txt_filepath, 'w', encoding='UTF-8') as f:
                    f.write(object['text'])
            else:
                if os.path.isfile(txt_filepath):
                    os.remove(txt_filepath)
                continue

        return HttpResponse(status=200)



    for object in split_audio_object_list:
        if status == '전사완료' or status == '분석중':
            text = 'text1'
        else:  # status == '분석완료':
            text = 'text2'

        transcription = Text.objects.filter(split_filename=object['split_filename']).values(text, 'text3', 'is_deleted', 'is_sound').first()
        txt_filepath = str(os.path.splitext(object['split_filepath'])[0]) + '.txt'

        if transcription['is_deleted'] == 'N' and transcription['is_sound'] == 'N':
            if status == '분석완료' and transcription['text3'] is not None:
                text = 'text3'

            #print(text)
            with open(txt_filepath, 'w', encoding='UTF-8') as f:
                f.write(transcription[text])

        else:
            if os.path.isfile(txt_filepath):
                os.remove(txt_filepath)
            continue

    return HttpResponse(status=200)


def stop_transcription(request):
    board_id = request.POST.get('board_id', None)
    status = Audio.objects.filter(id=board_id).values('status').first()['status']
    Audio.objects.filter(id=board_id).update(status='전사보류', prev_status=status)
    return HttpResponse(status=200)

def stop_cancel_transcription(request):
    board_id = request.POST.get('board_id', None)
    prev_status = Audio.objects.filter(id=board_id).values('prev_status').first()['prev_status']
    Audio.objects.filter(id=board_id).update(status=prev_status, prev_status=None)
    return HttpResponse(status=200)



