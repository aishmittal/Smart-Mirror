import cv2
import sys
import os
import time
from PIL import Image
import glob
import csv
import string
import random
import imageUpload as imup
import MSFaceAPI as msface

baseDir = '/home/aishwarya/Documents/Smart-Mirror/'
tmpDir = '/home/aishwarya/Documents/Smart-Mirror/tmp/'
cloudinary_dataset = 'http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/dataset/'
cloudinary_tmp = 'http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/tmp/'

# for capturing the faces using opencv and store the cropped face image in dataset directory
def face_capture(imgPath):
    
    # Camera 0 is the integrated web cam on my netbook
    camera_port = 1
    cascPath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath) 
    
    

    #Number of frames to throw away while the camera adjusts to light levels
    ramp_frames = 50
    
    cam = cv2.VideoCapture(camera_port) 
    face_cnt=0;
    while True:
        for i in xrange(ramp_frames):
            s, im = cam.read()   
        print("Taking image... ")
        ret,image = cam.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(120, 120),
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
        image_crop = image[my:my+mh,mx:mx+mw]
        cv2.imwrite(imgPath, image_crop)
        face_cnt=face_cnt+1
    
        if face_cnt==1:
            break    
    # When everything is done, release the capture
    cam.release()
    cv2.destroyAllWindows()


def face_upload(imgPath,fileName):
    try:
        print 'Uploading...' 
        imup.upload_image(imgPath,fileName)
    except Exception as e:
        print("Error: %s" % e.message)    

def face_identify(imageUrl):
    faceId=''
    personId=''
    personName=''
    try:
        faceId=msface.face_detect(imageUrl)
    except Exception as e:
        print("Error: %s" % e.message)
    if faceId=='':
        return personName
    try:
        personId=msface.face_identify(faceId)
    except Exception as e:
        print("Error: %s" % e.message)

    if personId=='':
        return personName

    with open('users.csv', "rb") as f:
        rd = csv.reader(f,delimiter=',')
        cnt=0
        for r in rd:
            if cnt>0:
                if personId==r[0]:
                    personName=r[1]
                    return personName
            cnt=cnt+1    
        
         

    

def id_generator(size=20, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    
    imageName=id_generator()+'.jpg'
    print('file name %s' % imageName)
    imgPath=tmpDir+imageName
    imgUrl=cloudinary_tmp+imageName
    try:
        print('Face Capturing Started')
        face_capture(imgPath)
        print('Face Capturing Completed')
    except Exception as e:
        print("Error: %s" % e.message)

    try:
        print('Uploading Started')
        face_upload(imgPath, imageName)
        print('Upload Completed')
    except Exception as e:
        print("Error: %s" % e.message)

    try:
        print('Face Identification Started')
        pname=face_identify(imgUrl)
        print('Face Identification Completed')
        print('Face Identified as: %s' % pname)
    except Exception as e:
        print("Error: %s" % e.message)    
    
        


                      

    
        
