import collections
import contextlib
import sys
import wave
import os
import webrtcvad
import speech_recognition as sr


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
                start = f'{i*0.03:.2f}'
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
                end = f'{round(i*0.03, 2):.2f}'
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
        end = f'{round(i*0.03, 2):.2f}'
        yield [b''.join([f.bytes for f in voiced_frames]), start, end]


audio_file = 'C:/Users/user/Downloads/001_kinuw87_20220818113644_00013_1.wav'
SPLIT_AUDIO_PATH = 'C:/Users/user/Downloads'


def splitter(wav_file):
    audio_file_name = wav_file.split('/')[-1].split('.')[0]
    split_audio_dir = SPLIT_AUDIO_PATH + '/' + audio_file_name
    os.makedirs(split_audio_dir, exist_ok=True)
    audio, sample_rate = read_wave(wav_file)
    vad = webrtcvad.Vad(1)
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, 300, vad, frames)
    for i, [segment, start, end] in enumerate(segments):
        split_audio_name = "{}{}{}_{:03d}.wav".format(split_audio_dir, '/', audio_file_name, i)
        # print('Writing {}'.format(split_audio_name))
        print(split_audio_name)
        print(f'{start} ~ {end}')
        write_wave(split_audio_name, segment, sample_rate)
        text = speech_to_text(split_audio_name)
        print(text)


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
        #print(e)
    return text


if __name__ == '__main__':
    splitter(audio_file)
