import io
from flask import Flask,render_template,Response, current_app
import cv2
import time
import psycopg2
import os
from flask_sqlalchemy import SQLAlchemy
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime


# Adding postgres URI for Database connection
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/blink'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


#creating variable to pass to html files to display blinks and percentage 
with app.app_context():
    current_app.config["blink"] = 4
    current_app.config["percentage"] = 86
    
    
#capturing video from local webcam
camera=cv2.VideoCapture(0)


#connecting database using psycopg library
db = SQLAlchemy(app)
conn = psycopg2.connect("postgresql://postgres:1234@localhost:5432/blink")
cur = conn.cursor()


#importing face and eye cascade files
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')


#initializing all the global variables
start=time.time()
eaf=start
f_r = True
totalnft=0
lastime=0
totalft=0
fo=False
eo=False
blinkcount=0
i=1


#creating a model class for our blink_data table
class blink_data(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    USERNAME = db.Column(db.String(50), nullable=False)
    BLINK_COUNT = db.Column(db.Integer, nullable=False)
    TIMEDURATION = db.Column(db.Integer, nullable=False)
    TIME = db.Column(db.String(50), nullable=False)
    SESSIONDATE = db.Column(db.String(50), nullable=False)
    
    #creating constructor to initialze the variable

    def __init__(self,ID, USERNAME, BLINK_COUNT,TIMEDURATION,TIME,SESSIONDATE):
        self.ID = ID
        self.USERNAME = USERNAME
        self.BLINK_COUNT = BLINK_COUNT
        self.TIMEDURATION = TIMEDURATION
        self.TIME = TIME
        self.SESSIONDATE = SESSIONDATE
        
        
#creating a model class for our screentime table
class screentime(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    USERNAME = db.Column(db.String(50), nullable=False)
    PERCENTAGE = db.Column(db.Integer, nullable=False)
    TIMEDURATION = db.Column(db.Integer, nullable=False)
    TIME = db.Column(db.String(50), nullable=False)
    SESSIONDATE = db.Column(db.String(50), nullable=False)

    #creating constructor to initialze the variable
    def __init__(self, ID,USERNAME, PERCENTAGE,TIMEDURATION,TIME,SESSIONDATE):
        self.ID = ID
        self.USERNAME = USERNAME
        self.PERCENTAGE = PERCENTAGE
        self.TIMEDURATION = TIMEDURATION
        self.TIME = TIME
        self.SESSIONDATE = SESSIONDATE
        
        
# method to write call model and apply bussiness logic to it
def generate_imgs():
    while True:
        
        
        # initialing opencv cascade models
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
        
        
        #adding value to the global variable
        start=time.time()
        eaf=start
        f_r = False
        totalnft=0
        lastime=0
        totalft=0
        bi=[]
        fo=False
        eo=False
        i=1
        blinkcount=0
        ret, img = camera.read()  # read the camera img
        
        
        #checking if the camera has read the image or not
        if not ret:
            break
        else:
            
            # running the loop while camera is on
            while(ret):
                
                
                # bussiness logic for inserting data into table after every given time
                if(time.time()-start>=10):
                    print("data entry")
                    
                    
                    # inserting values in all the app config page
                    with app.app_context():
                        
                        pe=int(((10-totalnft)*10))
                        pe=pe%101
                        current_app.config["percentage"]=pe
                    
                    
                    #fetching last primary key id from the table
                    cur.execute('SELECT id FROM blink_data')
                    p=1
                    id = cur.fetchall()
                    for i in id:
                        if(i[0]>p):
                            p=i[0]
                    c=p+1 #storing the new primary key id
                    
                    
                    #counting all the blink in the given time
                    q=set(bi)
                    blinkcount=len(q)
                    
                    # inserting values in all the app config variables
                    with app.app_context():
                        current_app.config["blink"]=blinkcount
                    
                    
                    # getting current date and time
                    now = datetime.now()
                    d=str(now)[:10]
                    t=str(now)[11:19]
                    
                    
                    #inserting data in blink_data table
                    cur.execute('INSERT INTO blink_data (ID, USERNAME, BLINK_COUNT,TIMEDURATION,TIME,SESSIONDATE)'
                        'VALUES (%s,%s, %s, %s, %s,%s)',
                        (c,"atul",blinkcount,120,t,d))
                    
                    
                    #inserting data in screentime table
                    cur.execute('INSERT INTO screentime (ID, USERNAME, PERCENTAGE,TIMEDURATION,TIME,SESSIONDATE)'
                        'VALUES (%s,%s, %s, %s, %s,%s)',
                        (c,"atul",pe,120,t,d))
                    conn.commit()
                    
                    # reinitializing all the variables for second time batch
                    start=time.time()
                    eaf=start
                    totalnft=0
                    lastime=time.time()
                    totalft=0
                    bi=[]
                    fo=True
                    eo=False
                    blinkcount=0
                    
                    
                # converting camera video into images
                ret, img = camera.read()
                
                
                # converting image into grayscale to apply model
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray,5,1,1)
                
                
                # passing gray image in face cascade model
                faces = face_cascade.detectMultiScale(gray, 1.3, 5,minSize=(200,200))
                
                # if no. of faces are more than 0 then apply eye cascade
                if(len(faces)>0):
                    
                    # adding total time when face was not visible
                    if(fo==False):
                        totalnft+=time.time()-lastime
                        fo=True
                        
                    # getting the cordinate of faces
                    for (x,y,w,h) in faces:
                        img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                        roi_face = gray[y:y+h,x:x+w]
                        roi_face_clr = img[y:y+h,x:x+w]
                        
                        # passing gray image in eye cascade model
                        eyes = eye_cascade.detectMultiScale(roi_face,1.3,5,minSize=(50,50))
                        if(len(eyes)>=2):
                            
                            if(f_r==False):
                                f_r=True
                                totalnft=0
                            if(eo==True):
                                eo=False
                                    
                        else:
                            if(f_r==False):
                                cv2.putText(img, "No eyes detected", (100,100), cv2.FONT_HERSHEY_PLAIN, 3,(0,0,255),2)
                            else:
                                if(eo==False):
                                    eo=True
                                    # counting blinks
                                    blinkcount+=1
                                    bi.append(int(time.time()-start))
                else:
                    
                    if(fo==True):
                        lastime=time.time()
                        fo=False
                    if(f_r==False):
                        start=time.time()
                        
                # displaying video in web
                ret, buffer = cv2.imencode('.jpg', img)
                img = buffer.tobytes()
                yield (b'--img\r\n'b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blinkcount')
def bcc():
    s={"blink":current_app.config["blink"]}
    return s

@app.route('/screenper')
def scc():
    s={"percentage":current_app.config["percentage"]}
    return s

@app.route('/blink')
def blink():
    return render_template('main.html',blink=current_app.config["blink"],percentage=current_app.config["percentage"])

@app.route('/blinkchart')
def blinkpng():
    f = blinkstat()
    o = io.BytesIO()
    FigureCanvas(f).print_png(o)
    return Response(o.getvalue(), mimetype='image/png')


# plotting blink vs time graph
def blinkstat():
    cur.execute('SELECT blink_count FROM blink_data')
    blinks = cur.fetchall()
    b=[]
    timee=[]
    c=1
    for i in blinks:
        b.append(i[0])
        timee.append(c)
        c+=1
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(timee,b,0.2)
    axis.set_title('Time')
    fig.supylabel('Blink count')
    return fig

@app.route('/screentime')
def screentimepng():
    fig = screentime()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

# plotting screentime vs time graph
def screentime():
    cur.execute('SELECT percentage FROM screentime')
    blinks = cur.fetchall()
    s=[]
    timee=[]
    c=1
    for i in blinks:
        s.append(i[0]%100)
        timee.append(c)
        c+=1
    print(s)
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot( timee,s)
    fig.supylabel('Percentage')
    return fig

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/video')
def video():
    return Response(generate_imgs(),mimetype='multipart/x-mixed-replace; boundary=img')

if __name__=="__main__":
    app.run(debug=True)