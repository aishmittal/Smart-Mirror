import multiprocessing
import Tkinter as tk
import cv2
import sys
import os
import time
from PIL import Image
import glob

cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)
baseDir = '/home/aishwarya/Documents/Smart-Mirror-Project/'

e = multiprocessing.Event()
p = None



# -------begin capturing and saving video
def startrecording(e):
    cap = cv2.VideoCapture(0)
    person_name='tmp'
    directory=baseDir+'dataset/'+person_name 
    face_cnt=1
    total_face_cnt = 5  
    cascPath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)
    
    #fourcc = cv2.cv.CV_FOURCC(*'XVID')
    #out = cv2.VideoWriter('output.avi',fourcc,  20.0, (640,480))
    while(cap.isOpened()):
        if e.is_set():
            cap.release()
            cv2.destroyAllWindows()
            e.clear()
        
        print("Taking image... %d" % face_cnt)
        ret,image = cap.read()
        
        
        # A nice feature of the imwrite method is that it will automatically choose the
        # correct format based on the file extension you provide. Convenient!
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        
        # Draw a rectangle around the faces
        max_area = 0
        mx = 0
        my = 0 
        mh = 0 
        mw = 0
        for (x, y, w, h) in faces:
            #cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if w*h > max_area:
                mx = x
                my = y
                mh = h
                mw = w
                max_area=w*h

        cv2.imshow('Video', image)    
        
        if max_area >= 1000 :
            
            
            image_crop = image[my:my+mh,mx:mx+mw]
            file = directory +'/'+'img_%d.jpg'% face_cnt
            face_cnt = face_cnt +1
            cv2.imwrite(file, image_crop)
    
        #wait for 1 seconds
        time.sleep(1)  
        if face_cnt == total_face_cnt+1:
            break


        
        

def start_recording_proc():
    global p
    p = multiprocessing.Process(target=startrecording, args=(e,))
    p.start()

# -------end video capture and stop tk
def stoprecording():
    e.set()
    p.join()


if __name__ == "__main__":
    # -------configure window
    root = tk.Tk()
    root.geometry("%dx%d+0+0" % (100, 100))
    startbutton=tk.Button(root,width=10,height=1,text='START',command=start_recording_proc)
    stopbutton=tk.Button(root,width=10,height=1,text='STOP', command=stoprecording)
    startbutton.pack()
    stopbutton.pack()

    # -------begin
    root.mainloop()