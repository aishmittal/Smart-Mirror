import cv2
import sys
import os
import time
from PIL import Image
import glob
import csv
import imageUpload as imup
import MSFaceAPI as msface

baseDir = '/home/aishwarya/Documents/Smart-Mirror/'
cloudinary_dataset = 'http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/dataset'
cloudinary_tmp = 'http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/tmp'
total_face_cnt = 8
camera_port = 1 
# for capturing the faces using opencv and store the cropped face image in dataset directory
def face_capture(outputDir):
    face_cnt=-2
    # Camera 0 is the integrated web cam on my netbook
    cascPath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath) 
    tmpDir = '/home/aishwarya/Documents/Smart-Mirror-Project/tmp'
    #Number of frames to throw away while the camera adjusts to light levels
    ramp_frames = 50
    
    cam = cv2.VideoCapture(camera_port) 

    while True:
        for i in xrange(ramp_frames):
            s, im = cam.read()
            cv2.imshow('Video', im)
        if face_cnt>0:
            print("Taking image... %d" % face_cnt)
        ret,image = cam.read()
        
        
        # A nice feature of the imwrite method is that it will automatically choose the
        # correct format based on the file extension you provide. Convenient!
        
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
            
        image_crop = image[my:my+mh,mx:mx+mw]
        if face_cnt>0:
            file = outputDir +'/'+'img_%d.jpg'% face_cnt
            cv2.imwrite(file, image_crop)
        cv2.rectangle(image, (mx, my), (mx+mw, my+mh), (0, 255, 0), 2)
        cv2.imshow('Video', image)
        #wait for 1 seconds
        #time.sleep(1)  
        face_cnt = face_cnt +1
        if face_cnt == total_face_cnt+1:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

      

    # When everything is done, release the capture
    cam.release()
    cv2.destroyAllWindows()

# upoloading the images to the cloudinary 
def face_upload(dirPath,personName):
    i=1
    for file in os.listdir(dirPath):
        imagePath=os.path.join(dirPath,file)
        try:
            print 'Uploading... %d' %i
            imup.upload_person_image(imagePath,file,personName)
            i=i+1
        except Exception as e:
            print("Error: %s" % e.message)         


def create_person(personName,udata):
    return msface.create_person(personName,udata)

def add_person_faces(pid,personName):
    cloudinary_dir= cloudinary_dataset+'/'+personName+'/'
    for i in range(1,total_face_cnt+1):
        image_url=cloudinary_dir+'img_%d.jpg' % i
        print 'Adding face..... %d'%i
        try:
            msface.add_person_face(pid,image_url)
            print 'Added face..... %d'%i
        except Exception as e:
            print("Error: %s" % e.message)     
    


if __name__ == '__main__':
    
    firstname = raw_input("Enter the first name: ")
    lastname = raw_input("Enter the last name: ")
    dob = raw_input("Enter date of birth (DD/MM/YYYY): ")
    gender = raw_input("Enter gender (M/F): ")
    person_name = firstname + "_" + lastname
    directory=baseDir+'dataset/'+person_name
    personId=''
    print directory
    
    if os.path.isdir(directory)==False:
        try:
            original_umask = os.umask(0)
            os.makedirs(directory)
        finally:
            os.umask(original_umask)    
    
    try:
        print('Face Capturing Started')
        face_capture(directory)
        print('Face Capturing Completed')
    except Exception as e:
        print("Error: %s" % e.message)     

    try:
        print('Uploading to Cloudinary')
        face_upload(directory,person_name)
        print('Upload Completed')
    except Exception as e:
        print("Error: %s" % e.message)

    try:
        print('Creating Person')
        udata=firstname+' '+lastname
        personId=create_person(person_name,udata)
        print('Person Created')
    except Exception as e:
        print("Error: %s" % e.message)
    

    with open('users.csv', "a") as f:
        writer = csv.writer(f,delimiter=',')
        fields=[personId,person_name,firstname,lastname,dob,gender]
        print fields
        writer.writerow(fields)
 
    try:
        add_person_faces(personId,person_name)
    except Exception as e:
        print("Error: %s" % e.message)
        
