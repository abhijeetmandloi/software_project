import numpy as np
import cv2
import time
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
first_read = True
cap = cv2.VideoCapture(0)
ret,img = cap.read()
start=time.time()
eaf=start
totalnft=0
lastime=0
totalft=0
fo=False
eo=False
blinkcount=0
while(ret):
    if(time.time()-start>=120):
        start=time.time()
        eaf=start
        totalnft=0
        lastime=0
        totalft=0
        fo=False
        eo=False
        blinkcount=0
    ret,img = cap.read()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray,5,1,1)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5,minSize=(200,200))
    if(len(faces)>0):
        if(fo==False):
            totalnft+=time.time()-lastime
        fo=True
        for (x,y,w,h) in faces:
            img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            roi_face = gray[y:y+h,x:x+w]
            roi_face_clr = img[y:y+h,x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_face,1.3,5,minSize=(50,50))
            if(len(eyes)>=2):
                print("----------------------")
                if(first_read):
                    first_read=False
                    start=time.time()-totalft
                if(eo==True):
                    eo=False
                        
                #     cv2.putText(img, "press s to begin", (100,100), cv2.FONT_HERSHEY_PLAIN, 3,(0,0,255),2)
                # else:
                #     print("----------------------")
            else:
                if(first_read):
                    cv2.putText(img, "No eyes detected", (100,100), cv2.FONT_HERSHEY_PLAIN, 3,(0,0,255),2)
                else:
                    if(eo==False):
                        eo=True
                        blinkcount+=1
                        print(time.time()-start)
                    # first_read=True
    else:
        if(fo==True):
            lasttime=time.time()
            fo==False
        # if(fo==True):
        #     eaf=time.time()-start
        #     totalnft=time.time()-start
        #     lastime=time.time()
        if(first_read==False):
            start=time.time()
        cv2.putText(img,"No face detected",(100,100),cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0),2)
    cv2.imshow('img',img)
    a = cv2.waitKey(1)
    if(a==ord('q')):
        break
    elif(a==ord('s') and first_read):
        first_read = False

cap.release()
cv2.destroyAllWindows()