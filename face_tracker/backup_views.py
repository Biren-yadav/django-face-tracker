from django.shortcuts import render

# Create your views here.

import cv2
import numpy as np
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators import gzip
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        ret, frame = self.video.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        return None

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def video_feed(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera()), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        return JsonResponse({'status': 'error'})

def index(request):
    return render(request, 'face_tracker/index.html')
