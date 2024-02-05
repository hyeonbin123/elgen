import datetime
import math
import os
import sys

import librosa
import speech_recognition as sr

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from audio.models import Audio, SplitAudio, Reply, ReReply, Text

import schedule
import time

from django.core.management.base import BaseCommand
from django.utils import timezone
from moviepy.video.io import ffmpeg_tools

import collections
import contextlib
import wave
import webrtcvad




def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""

    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    start = 0
    end = 0
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    i = 0
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        # sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                start = f'{i * 0.03:.2f}'
                triggered = True
                # sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                # sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                end = f'{round(i * 0.03, 2):.2f}'
                triggered = False
                yield [b''.join([f.bytes for f in voiced_frames]), start, end]
                ring_buffer.clear()
                voiced_frames = []
        i += 1
    # if triggered:
    # sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    # sys.stdout.write('\n')
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        end = f'{round(i * 0.03, 2):.2f}'
        yield [b''.join([f.bytes for f in voiced_frames]), start, end]


#audio_file = 'C:/Users/user/Downloads/call2/out_audio2.wav'
#SPLIT_AUDIO_PATH = 'C:/Users/user/Downloads/call2'

def splitter(wav_file):
    print('wav_file: ', wav_file)
    SPLIT_AUDIO_PATH = os.path.dirname(wav_file) + os.sep + 'split'
    print('SPLIT_AUDIO_PATH: ', SPLIT_AUDIO_PATH)
    if not os.path.isdir(SPLIT_AUDIO_PATH):
        os.makedirs(SPLIT_AUDIO_PATH)

    audio, sample_rate = read_wave(wav_file)
    audio_file_name = wav_file.split(os.sep)[-1].split('.')[0]
    split_audio_dir = SPLIT_AUDIO_PATH + os.sep + audio_file_name
    os.makedirs(split_audio_dir, exist_ok=True)

    vad = webrtcvad.Vad(1)
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, 300, vad, frames)
    for i, [segment, start, end] in enumerate(segments):
        split_audio_name = "{}{}{}_{:03d}.wav".format(split_audio_dir, os.sep, audio_file_name, i)
        split_filename = "{}_{:03d}.wav".format(audio_file_name, i)

        # print('Writing {}'.format(split_audio_name))
        #print('split_audio_name: ', split_audio_name)
        #print(f'{start} ~ {end}')

        write_wave(split_audio_name, segment, sample_rate)
        text = speech_to_text(split_audio_name)
        #print(text)

        start_time = get_duration(start)
        #print('start_time: ', start_time)
        end_time = get_duration(end)
        #print('end_time: ', end_time)

        SplitAudio.objects.create(wav_filepath=wav_file, split_filepath=split_audio_name,
                                  split_filename=split_filename, text=text, start_time=start_time, end_time=end_time)


def speech_to_text(split_filepath):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    try:
        audio_recog = sr.AudioFile(split_filepath)
        with audio_recog as source:
            audio_data2 = recognizer.record(source)
        text = recognizer.recognize_google(audio_data=audio_data2, language="ko-KR")
    except Exception as e:
        text = ''
        # print(e)
    return text

def get_duration(total_seconds):
    total_seconds = math.floor(float(total_seconds))

    # get min and seconds first
    mm, ss = divmod(total_seconds, 60)
    # Get hours
    hh, mm = divmod(mm, 60)

    hh = format(hh, '02')
    mm = format(mm, '02')
    ss = format(ss, '02')

    get_duration = str(hh) + ':' + str(mm) + ':' + str(ss)

    return get_duration

def file_duration(filepath):
    duration = librosa.get_duration(filename=filepath)
    duration = math.floor(duration)  # 밀리초 내림(버림)
    duration = time.strftime('%H:%M:%S', time.gmtime(duration))  # seconds to hh:mm:ss
    return duration


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('배치실행')

        delete_audio_list = Audio.objects.filter(is_deleted='Y')

        if len(delete_audio_list) > 0 :

            for delete_audio in delete_audio_list:

                # 삭제요청한지 익일자정이 지난 파일은 지우기
                if delete_audio.delete_date is not None:
                    # print('audio.delete_date: ', audio.delete_date)
                    # print('timezone.now(): ', timezone.now())
                    if delete_audio.delete_date <= timezone.now():

                        reply_delete_list = Reply.objects.filter(board_id=delete_audio.id)
                        for reply in reply_delete_list:
                            ReReply.objects.filter(reply_id=reply.id).delete()  # 해당 글의 대댓글 DB에서 삭제

                        reply_delete_list.delete()  # 해당 글의 댓글 DB에서 삭제

                        if delete_audio.wav_filepath is not None:
                            split_delete_list = SplitAudio.objects.filter(wav_filepath=delete_audio.wav_filepath)

                            if split_delete_list.count() != 0:  # split했다면
                                for split in split_delete_list:
                                    text = Text.objects.filter(split_filename=split.split_filename).first()
                                    if text is not None:  # 전사했다면
                                        text.delete()  # 전사 DB 삭제
                                    if os.path.exists(split.split_filepath):
                                        os.remove(split.split_filepath)  # split된 실제파일 삭제
                                        split_dirname = os.path.dirname(split.split_filepath)
                                        try:
                                            if os.path.exists(split_dirname):  # 상위폴더가 비었으면 상위폴더도 삭제
                                                os.rmdir(split_dirname)
                                                split_dir_dirname = os.path.dirname(split_dirname)
                                                if os.path.exists(split_dir_dirname):  # 상위폴더(=split폴더)가 비었으면 상위폴더도 삭제
                                                    os.rmdir(split_dir_dirname)
                                        except:
                                            pass
                                split_delete_list.delete()  # split DB삭제

                            if os.path.exists(delete_audio.wav_filepath):
                                os.remove(delete_audio.wav_filepath)  # 변환한 wav 파일 삭제
                                wav_dirname = os.path.dirname(delete_audio.wav_filepath)
                                try:
                                    if os.path.exists(wav_dirname):  # 상위폴더가 비었으면 상위폴더도 삭제
                                        os.rmdir(wav_dirname)
                                except:
                                    pass

                        if os.path.exists(delete_audio.filepath):
                            os.remove(delete_audio.filepath)  # 실제 파일(.weba) 삭제(파일 업로드일 경우는 .wav일 경우도 있음.. 하지만 위에서 미리 삭제되고 이 지점에는 없겠지.)
                            audio_dirname = os.path.dirname(delete_audio.filepath)
                            try:
                                if os.path.exists(audio_dirname):  # 상위폴더(날짜)가 비었으면 상위폴더도 삭제
                                    os.rmdir(audio_dirname)
                                    audio_dir_dirname = os.path.dirname(audio_dirname)
                                    if os.path.exists(audio_dir_dirname):  # 상위폴더(월)가 비었으면 상위폴더도 삭제
                                        os.rmdir(audio_dir_dirname)
                                        audio_dir_dir_dirname = os.path.dirname(audio_dir_dirname)
                                        if os.path.exists(audio_dir_dir_dirname):  # 상위폴더(연도)가 비었으면 상위폴더도 삭제
                                            os.rmdir(audio_dir_dir_dirname)
                            except:
                                pass
                        delete_audio.delete()  # DB에서 삭제
                        continue

        
        audio_list = Audio.objects.filter(created_at__gte = timezone.now() - datetime.timedelta(hours=24))

        if len(audio_list) > 0 :

            for audio in audio_list:





                name, ext = os.path.splitext(audio.filepath)
                if ext == '.weba' and os.path.isfile(audio.filepath): #실제 파일이 존재한다면
                    wav_filepath = name + '.wav'
                    if not os.path.isfile(wav_filepath): #weba는 있지만 wav는 존재하지않는다면
                        ffmpeg_tools.ffmpeg_extract_audio(audio.filepath, wav_filepath, fps=16000)
                        # 오디오 파일 길이 가져오기
                        duration = file_duration(wav_filepath)

                        # DB 업데이트
                        Audio.objects.filter(filepath=audio.filepath).update(wav_filepath=wav_filepath, play_time=duration, is_split='N')

                        #split
                        splitter(wav_filepath)
                        Audio.objects.filter(filepath=audio.filepath).update(is_split='Y')
                        #split_filename = "{}_{:03d}.wav".format(audio_file_name, i)

                        print("{} split 완료".format(audio.filename))

                    else: #weba와 wav 둘다 존재
                        if audio.is_split is None or audio.is_split == 'N': #wav가 존재하지만 split이 되지않았다면
                            # split
                            splitter(audio.filepath)
                            Audio.objects.filter(filepath=audio.filepath).update(is_split='Y')

                            print("{} split 완료".format(audio.filename))
                        else:
                            continue

                elif ext == '.wav' and os.path.isfile(audio.filepath):  # wav파일을 로컬업로드했을 경우
                    if audio.is_split is None or audio.is_split == 'N':
                        # split
                        splitter(audio.filepath)
                        Audio.objects.filter(filepath=audio.filepath).update(is_split='Y')

                        print("{} split 완료".format(audio.filename))
                    else:
                        continue
                else:
                    continue


command = Command()

# 10초에 한번씩 실행
# schedule.every(10).seconds.do(job)
# 10분에 한번씩 실행
# schedule.every(10).minutes.do(job)
# 매 시간 실행
# schedule.every().hour.do(job)
# 매일 10:30 에 실행
schedule.every().day.at("00:05").do(command.handle)
# 매주 월요일 실행
# schedule.every().monday.do(job)
# 매주 수요일 13:15 에 실행
# schedule.every().wednesday.at("13:15").do(job)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)








