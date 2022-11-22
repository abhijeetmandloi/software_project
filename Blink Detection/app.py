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

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/blink'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
with app.app_context():
    current_app.config["blink"] = 1
    current_app.config["percentage"] = 86
camera=cv2.VideoCapture(0)
db = SQLAlchemy(app)
conn = psycopg2.connect("postgresql://postgres:1234@localhost:5432/blink")
cur = conn.cursor()
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
start=time.time()
eaf=start
first_read = True
totalnft=0
lastime=0
totalft=0
fo=False
eo=False
blinkcount=0
i=1
class blink_data(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    USERNAME = db.Column(db.String(50), nullable=False)
    BLINK_COUNT = db.Column(db.Integer, nullable=False)
    TIMEDURATION = db.Column(db.Integer, nullable=False)
    TIME = db.Column(db.String(50), nullable=False)
    SESSIONDATE = db.Column(db.String(50), nullable=False)

    def __init__(self,ID, USERNAME, BLINK_COUNT,TIMEDURATION,TIME,SESSIONDATE):
        self.ID = ID
        self.USERNAME = USERNAME
        self.BLINK_COUNT = BLINK_COUNT
        self.TIMEDURATION = TIMEDURATION
        self.TIME = TIME
        self.SESSIONDATE = SESSIONDATE
        
class screentime(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    USERNAME = db.Column(db.String(50), nullable=False)
    PERCENTAGE = db.Column(db.Integer, nullable=False)
    TIMEDURATION = db.Column(db.Integer, nullable=False)
    TIME = db.Column(db.String(50), nullable=False)
    SESSIONDATE = db.Column(db.String(50), nullable=False)

    def __init__(self, ID,USERNAME, PERCENTAGE,TIMEDURATION,TIME,SESSIONDATE):
        self.ID = ID
        self.USERNAME = USERNAME
        self.PERCENTAGE = PERCENTAGE
        self.TIMEDURATION = TIMEDURATION
        self.TIME = TIME
        self.SESSIONDATE = SESSIONDATE
        
def generate_imgs():
    while True:
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
        start=time.time()
        eaf=start
        first_read = True
        totalnft=0
        lastime=0
        totalft=0
        bi=[]
        fo=False
        eo=False
        i=1
        blinkcount=0
        ret, img = camera.read()  # read the camera img
        if not ret:
            break
        else:
            while(ret):
                if(time.time()-start>=10):
                    print("data entry")
                    with app.app_context():
                        current_app.config["blink"]=blinkcount
                        current_app.config["percentage"]="{:.2f}".format((120-totalnft)/1.2)
                    cur.execute('SELECT id FROM blink_data')
                    p=1
                    id = cur.fetchall()
                    for i in id:
                        if(i[0]>p):
                            p=i[0]
                    c=p+1
                    q=set(bi)
                    blinkcount=len(q)
                    cur.execute('INSERT INTO blink_data (ID, USERNAME, BLINK_COUNT,TIMEDURATION,TIME,SESSIONDATE)'
                        'VALUES (%s,%s, %s, %s, %s,%s)',
                        (c,"atul",blinkcount,120,"21-11-2022:10:36","21-11-2022:10:36"))
                    
                    cur.execute('INSERT INTO screentime (ID, USERNAME, PERCENTAGE,TIMEDURATION,TIME,SESSIONDATE)'
                        'VALUES (%s,%s, %s, %s, %s,%s)',
                        (c,"atul",current_app.config["percentage"],120,"21-11-2022:10:36","21-11-2022:10:36"))
                    conn.commit()
                    start=time.time()
                    eaf=start
                    totalnft=0
                    lastime=time.time()
                    totalft=0
                    bi=[]
                    fo=True
                    eo=False
                    blinkcount=0
                ret, img = camera.read()
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray,5,1,1)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5,minSize=(200,200))
                if(len(faces)>0):
                    if(fo==False):
                        # print("+++++++++++++++++")
                        # print(lastime)
                        # print("+++++++++++++++++")
                        totalnft+=time.time()-lastime
                        # print(totalnft)
                        fo=True
                    for (x,y,w,h) in faces:
                        img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                        roi_face = gray[y:y+h,x:x+w]
                        roi_face_clr = img[y:y+h,x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_face,1.3,5,minSize=(50,50))
                        if(len(eyes)>=2):
                            
                            if(first_read):
                                first_read=False
                                totalnft=0
                                start=time.time()-totalft
                            if(eo==True):
                                eo=False
                                    
                            #     cv2.putText(img, "press s to begin", (100,100), cv2.FONT_HERSHEY_PLAIN, 3,(0,0,255),2)
                            # else:
                            # print("----------------------")
                        else:
                            if(first_read):
                                first_read=True
                                cv2.putText(img, "No eyes detected", (100,100), cv2.FONT_HERSHEY_PLAIN, 3,(0,0,255),2)
                            else:
                                if(eo==False):
                                    eo=True
                                    blinkcount+=1
                                    bi.append(int(time.time()-start))
                                    # print(time.time()-start)
                                # first_read=True
                else:
                    
                    if(fo==True):
                        # print("********")
                        lastime=time.time()
                        # print(lastime)
                        fo=False
                    if(first_read==False):
                        start=time.time()
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

def blinkstat():
    cur.execute('SELECT blink_count FROM blink_data')
    blinks = cur.fetchall()
    b=[]
    timee=[]
    c=2
    for i in blinks:
        b.append(i[0])
        timee.append(c)
        c+=1
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(timee,b,0.2)
    return fig

@app.route('/screentime')
def screentimepng():
    fig = screentime()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def screentime():
    cur.execute('SELECT percentage FROM screentime')
    blinks = cur.fetchall()
    s=[]
    timee=[]
    c=2
    for i in blinks:
        s.append(i[0]%100)
        timee.append(c)
        c+=1
    print(s)
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot( timee,s)
    return fig

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/video')
def video():
    return Response(generate_imgs(),mimetype='multipart/x-mixed-replace; boundary=img')

if __name__=="__main__":
    app.run(debug=True)