import cv2
import numpy as np
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators import gzip
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Global variable to track trigger state
trigger_pulled = False
bullet_position = None

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        global trigger_pulled, bullet_position
        
        ret, frame = self.video.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                # Calculate forehead point (between eyebrows)
                forehead_x = x + w // 2
                forehead_y = y + h // 4
                
                # Draw sniper scope (concentric circles)
                scope_radius = 100
                cv2.circle(frame, (forehead_x, forehead_y), scope_radius, (0, 0, 255), 2)
                cv2.circle(frame, (forehead_x, forehead_y), scope_radius//2, (0, 0, 255), 2)
                
                # Draw crosshair
                cross_size = 30
                cv2.line(frame, (forehead_x-cross_size, forehead_y), 
                        (forehead_x+cross_size, forehead_y), (0, 0, 255), 2)
                cv2.line(frame, (forehead_x, forehead_y-cross_size), 
                        (forehead_x, forehead_y+cross_size), (0, 0, 255), 2)
                
                # Draw bullet effect when triggered
                if trigger_pulled:
                    cv2.circle(frame, (forehead_x, forehead_y), 15, (0, 255, 255), -1)  # Bullet impact
                    bullet_position = (forehead_x, forehead_y)
                    trigger_pulled = False
            
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

@csrf_exempt
def trigger(request):
    global trigger_pulled
    if request.method == 'POST':
        trigger_pulled = True
        return JsonResponse({'status': 'fired'})
    return JsonResponse({'status': 'error'})

def index(request):
    return render(request, 'face_tracker/index.html', {'bullet_position': bullet_position})
