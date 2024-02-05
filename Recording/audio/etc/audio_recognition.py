'''
import speech_recognition as sr

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300

filepath = "C:/audio2/dypiston/k/dypiston_0001_k_F_50.weba"
audio_recog = sr.AudioFile(filepath)

with audio_recog as source:
    audio = recognizer.record(source)

text = recognizer.recognize_google(audio_data=audio, language="ko-KR")

print(text)
'''
import math
import os
import wave

from moviepy.video.io import ffmpeg_tools

path = "C:/Users/user/Downloads/00560.m4a"
path2 = "C:/Users/user/Downloads/00560.wav"
ffmpeg_tools.ffmpeg_extract_audio(path, path2, fps=16000)



'''
def get_duration(audio_path):
    audio = wave.open(audio_path)
    frames = audio.getnframes()
    rate = audio.getframerate()
    duration = frames / float(rate)
    return duration


file_path = "C:/Users/user/Downloads/cnuh_audio"
for file in os.listdir(file_path):
    full_file_path = file_path + '/' + file
    duration = math.floor(get_duration(full_file_path))



    mm, ss = divmod(duration, 60)
    # Get hours
    hh, mm = divmod(mm, 60)
    print(file, '-> ', hh,'시간 ',mm,'분 ',ss, '초')
'''