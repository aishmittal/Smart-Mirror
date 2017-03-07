import multiprocessing
import Tkinter as tk
import cv2
import sys
import os
import time
from PIL import Image
import glob
import thread
import speech_recognition as sr
# -------begin capturing and saving video
def start_video_recording(tmp):
        
    cascPath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)

    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


def start_speech_recording(tmp): 
# Record Audio
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
     
    # Speech recognition using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("You said: " + r.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def start_tk(tmp):
    root = tk.Tk()
    root.geometry("%dx%d+0+0" % (100, 100))
    startbutton=tk.Button(root,width=10,height=1,text='START')
    stopbutton=tk.Button(root,width=10,height=1,text='STOP')
    startbutton.pack()
    stopbutton.pack()
    # -------begin
    root.mainloop()
        
if __name__ == "__main__":
    # -------configure window
    
    try:
        #thread.start_new_thread( start_video_recording, (1, ) )
        thread.start_new_thread( start_speech_recording, (2, ) )
        thread.start_new_thread( start_tk, (3, ) )
    except:
        print "Error: unable to start thread"

    while 1:
       pass    