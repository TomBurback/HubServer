import speech_recognition as sr

r = sr.Recognizer()

audio = sr.AudioFile('/home/server/Documents/HubServer/Speech_Recogintion_Tests/OSR_us_000_0030_8k.wav')

with audio as source:
	audioData = r.record(source)
text = r.recognize_google(audioData)
print(text)
