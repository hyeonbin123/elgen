from glob import glob
from pydub import AudioSegment, silence
import os


#AUDIO_PATH = './data/*wav'
#SPLIT_AUDIO_PATH = './data/split_data'

AUDIO_PATH = 'C:/Users/user/Downloads/call2/*wav'
SPLIT_AUDIO_PATH = 'C:/Users/user/Downloads/call2'

audio_list = glob(AUDIO_PATH)

for audio_file in audio_list:
    audio = AudioSegment.from_wav(audio_file)
    audio_file_name = audio_file.split(os.sep)[-1].split('.')[0]
    split_audio_dir = SPLIT_AUDIO_PATH + os.sep + audio_file_name
    os.makedirs(split_audio_dir, exist_ok=True)
    speech_range = silence.detect_nonsilent(audio, min_silence_len=500, silence_thresh=-40, seek_step=1)
    # 0.5초 이상이되어야 묵음으로 간주, -40데시벨부터 묵음으로 간주, seek_step은 숫자가 클수록 더 큰범위로 잘라줌....작을수록 더 세밀하게 split)
    # out_audio2.wav상담사녹음파일은 silence_thresh=-50으로하니까 묵음인식이 안되어서 split이 안됨
    for i, [start, end] in enumerate(speech_range):
        split_audio = audio[start:end]
        print(f'{start / 1000} ~ {end / 1000}') #밀리초여서 1000으로 나눔
        split_audio_name = "{}{}{}_{:03d}.wav".format(split_audio_dir, os.sep, audio_file_name, i)
        split_audio.export(split_audio_name)
    print('-'*30)

