from pydub import AudioSegment, silence
import os


#AUDIO_PATH = './data/*wav'
#SPLIT_AUDIO_PATH = './data/split_data'

#audio_file = 'C:\\Users\\user\\Downloads\\call2\\out_audio2.wav'
#SPLIT_AUDIO_PATH = 'C:\\Users\\user\\Downloads\\call2\\split'

audio_file = 'D:\\local_recording\\output.wav'
SPLIT_AUDIO_PATH = 'D:\\local_recording\\split'


audio = AudioSegment.from_wav(audio_file)
audio_file_name = audio_file.split(os.sep)[-1].split('.')[0]
split_audio_dir = SPLIT_AUDIO_PATH + os.sep + audio_file_name
os.makedirs(split_audio_dir, exist_ok=True)
speech_range = silence.detect_nonsilent(audio, min_silence_len=500, silence_thresh=-40, seek_step=1)
for i, [start, end] in enumerate(speech_range):
    split_audio = audio[start:end]
    #print(f'{start / 1000} ~ {end / 1000}')
    split_audio_name = "{}{}{}_{:03d}.wav".format(split_audio_dir, os.sep, audio_file_name, i)
    split_audio.export(split_audio_name)


'''
#패딩 코드 추가(먼저 250밀리초만큼 총길이를 더 늘려준후, 그다음 양쪽을 500밀리초(0.5초) 늘려서 잘라준다) 
for audio_file in audio_list:
    audio = AudioSegment.from_wav(audio_file)
    audio_file_name = audio_file.split(os.sep)[-1].split('.')[0]
    split_audio_dir = SPLIT_AUDIO_PATH + os.sep + audio_file_name
    os.makedirs(split_audio_dir, exist_ok=True)
    speech_range = silence.detect_nonsilent(audio, min_silence_len=500, silence_thresh=-40, seek_step=1)
    pad_ms = 500
    add_end_ms = 250
    pad_silence = AudioSegment.silent(duration=pad_ms)
    for i, [start, end] in enumerate(speech_range):
        split_audio = audio[start:end+add_end_ms]
        print(f'{start / 1000} ~ {end / 1000}')
        split_audio_name = "{}{}{}_{:03d}.wav".format(split_audio_dir, os.sep, audio_file_name, i)
        padded = pad_silence + split_audio + pad_silence
        padded.export(split_audio_name, format='wav')
'''


