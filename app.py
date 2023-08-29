import base64
import glob
import io
import json
import logging
import subprocess
import time
from datetime import datetime
from flask_cors import CORS
from flask import Flask, Response, render_template, request
import pyaudio
import os

from pydub import AudioSegment
from starlette.responses import JSONResponse

import db

app = Flask(__name__)
CORS(app)


CHUNK = 1024


def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o


def get_last_file():
    dir_name = 'target_language_audio/'
    # Get list of all files in a given directory sorted by name
    list_of_files = sorted( filter( os.path.isfile,
                                    glob.glob(dir_name + '*') ) )
    return list_of_files[-1]

last_file1 = f'target_language_audio/{get_last_file()}'

AUDIO_FILES = ['target_language_audio/compressed_20230809-224427_Out.mp3', 'target_language_audio/compressed_20230809-224457_Out.mp3']  # Lista cu numele fișierelor audio

CURRENT_FILE_INDEX = 0


def get_next_audio_file(last_date_added):
    return db.get_last_recording_by_language(last_date_added)
    # global CURRENT_FILE_INDEX
    # next_file = AUDIO_FILES[CURRENT_FILE_INDEX]
    # CURRENT_FILE_INDEX = (CURRENT_FILE_INDEX + 1) % len(AUDIO_FILES)
    # return next_file


def calculate_duration(file_path):
    with open(file_path, "rb") as audio_file:
        audio_data = io.BytesIO(audio_file.read())
    audio = AudioSegment.from_file(audio_data)
    duration_seconds = len(audio) / 1000  # Durata în secunde
    return duration_seconds


@app.route('/audio')
def audio_stream():
    last_date_added = request.args.get('last_date_added')
    if last_date_added is not None:
        last_date_added = datetime.strptime(last_date_added, '%Y-%m-%d %H:%M:%S.%f')

    audio_file, date_added = get_next_audio_file(last_date_added)
    if audio_file == None:
        audio_file, date_added = get_next_audio_file(None)
    audio = AudioSegment.from_file(audio_file)
    audio_data = io.BytesIO()
    audio.export(audio_data, format="mp3")

    duration = calculate_duration(audio_file)

    audio_base64 = base64.b64encode(audio_data.getvalue()).decode("utf-8")

    response_data = {
        "audio": audio_base64,
        "duration": duration,
        "last_date_added": date_added
    }

    return json.dumps(response_data, indent=4, sort_keys=True, default=str)




# while True:
#         audio_file, date_added = get_next_audio_file(last_date_added)
#         if date_added is None or date_added == last_date_added:
#             # time.sleep(3)
#             continue
#         else:
#             last_date_added = date_added
#         cmd = [
#             'ffmpeg',
#             '-re',
#             '-i', audio_file,
#             '-f', 'mp3',
#             'pipe:1'
#         ]
#
#         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         yield process.stdout.read()
#
#         # time.sleep(30)  # Așteaptă 30 de secunde înainte de a trece la următorul fișier
#

@app.route('/')
def index():
    """Video streaming home page."""
    print("index")
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='192.168.1.171', debug=True, threaded=True,port=5003)
