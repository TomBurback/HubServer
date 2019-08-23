import speech_recognition as sr
import serial

import pyaudio
import struct
from datetime import datetime
import os
import platform
import sys

import soundfile

#!!! MUST BE UPDATED FOR SERVER !!!#
PATH_TO_PYTHON_BINDING = 'C:/Users/burbacktg/Documents/Porcupine/binding/python'
library_path = 'C:/Users/burbacktg/Documents/Porcupine/lib/windows/amd64/libpv_porcupine.dll' # Path to Porcupine's C library available under lib/${SYSTEM}/${MACHINE}/
model_file_path = 'C:/Users/burbacktg/Documents/Porcupine/lib/common/porcupine_params.pv' # It is available at lib/common/porcupine_params.pv
keyword_file_paths = ['C:/Users/burbacktg/Documents/Porcupine/keywords/porcupine_windows.ppn']
sensitivities = [0.5]

sys.path.append(os.path.join(os.path.dirname(__file__), PATH_TO_PYTHON_BINDING))

from porcupine import Porcupine

handle = Porcupine(library_path, model_file_path, keyword_file_paths=keyword_file_paths, sensitivities=sensitivities)

num_keywords = len(keyword_file_paths)

#Instantiate pyaudio
pa = pyaudio.PyAudio()
#Open audio stream
audio_stream = pa.open(
		rate=handle.sample_rate,
		channels=1,
		format=pyaudio.paInt16,
		input=True,
		frames_per_buffer=handle.frame_length)
print('Listening for keyword porcupine...')

while True:
        pcm = audio_stream.read(handle.frame_length)
        pcm = struct.unpack_from("h" * handle.frame_length, pcm)
        result = handle.process(pcm)
        if num_keywords == 1 and result:
            print('[%s] detected keyword' % str(datetime.now()))

#Open COM4 port
ser_port = serial.Serial('COM4')

#Instantiate recognizer
r = sr.Recognizer()

while True:
	#Listen to the microphone
	with sr.Microphone() as source:
		print("Please wait. Calibrating microphone...")  
		# listen for 5 seconds and create the ambient noise energy level  
		r.adjust_for_ambient_noise(source, duration=5)  
		print("Listening...")
		#Grab microphone data
		audioData = r.listen(source)
		#Try and recognize it
		try:
			text = r.recognize_sphinx(audioData)
			print("You said " + text)
			if("light" in text and "on" in text):
				ser_port.write(b'1')
			elif("light" in text and "off" in text):
				ser_port.write(b'0')
		except:
			print("Sorry, I didn't get that!")