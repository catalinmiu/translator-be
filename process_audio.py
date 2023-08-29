import datetime
import threading
import time

import gtts
import torch
from deep_translator import GoogleTranslator
from playsound import playsound
import sounddevice as sd
import whisper
from scipy.io.wavfile import write
from pydub import AudioSegment
import os

import db


def record(sec, fs=44100):
    print("record----")
    recording = sd.rec(int(sec * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    return (fs, recording)

def save_recording_to_file(recording, fs):
    recordings_name_folder = "recordings/"
    file_name = "recordings/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S.wav")
    write(file_name, fs, recording)
    sound = AudioSegment.from_file(file_name)
    new_file_name_compressed = f"compressed_{file_name[len(recordings_name_folder):-4]}.mp3"
    sound.export(new_file_name_compressed, format="mp3", bitrate="16k")
    os.remove(file_name)
    return new_file_name_compressed

# return file_name

def speech_to_text(file_name):
    model = whisper.load_model("medium", in_memory=True)
    print(file_name)
    result = model.transcribe(file_name)
    print(result["text"])
    os.remove(file_name)
    return result["text"]

def increase_audio_speed(file_name):
    speed = 1.28

    sound = AudioSegment.from_file(file_name)
    so = sound.speedup(speed, 150, 25)
    new_file_name = file_name[:-4] + '_Out.mp3'
    so.export(new_file_name, format = 'mp3')
    os.remove(file_name)
    return new_file_name

def translate_text(transcribed_text, target_language):
    print("translate_text")
    return GoogleTranslator(source='auto', target=target_language).translate(transcribed_text)

def text_to_speech(text, target_language, initial_file_name):
    tts = gtts.gTTS(text, lang=target_language)
    file_name = f"target_language_audio/{target_language}/{initial_file_name}"
    tts.save(file_name)
    return file_name

target_languages = ['ro']

queue = []

def process_recording(recording, fs):
    file_name = save_recording_to_file(recording, fs)
    transcribed_text = speech_to_text(file_name)
    for lang in target_languages:
        translated = translate_text(transcribed_text, lang)
        try:
            increased_audio_file_name = increase_audio_speed(text_to_speech(translated, lang, file_name))
            db.insert_recording(increased_audio_file_name, lang)
        except:
            pass

def play_translated_audio():
    while True:
        if len(queue) >= 1:
            file_name = queue.pop()
            playsound(file_name)
        time.sleep(3)

# y = threading.Thread(target=play_translated_audio)
# y.start()

while True:
    (fs, recording) = record(60)
    x = threading.Thread(target=process_recording, args=(recording, fs))
    x.start()

# import torch
# device = torch.device("mps") if torch.backends.mps.is_available() else "cpu"
#
# print(device)





