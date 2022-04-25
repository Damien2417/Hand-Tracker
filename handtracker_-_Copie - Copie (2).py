#!/usr/bin/python
# -*- coding: utf-8 -*-
from cvzone.HandTrackingModule import HandDetector
import cv2
import math
import pyautogui
import queue
from threading import Thread

q = queue.Queue()
q2 = queue.Queue()
q3 = queue.Queue()
flag=True

cap = cv2.VideoCapture(0)
class Recorder:
    def recordImage():
        while True:
            # Get image frame
            (success, img) = cap.read()
            q.put(img)
            #img = cv2.flip(img, 1)
            cv2.imshow('my webcam', q2.get())
            #q2.task_done()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                flag=False
                break
        q.join()
        q2.join()
        
class Showing:
    def showImage():
        while flag:
            if not q2.empty():
                cv2.imshow('my webcam', img)
                q2.task_done()
        q2.join()
        # After the loop release the cap object
        cap.release()
        # Destroy all the windows
        cv2.destroyAllWindows()

class HandTracker:
    def trackHands():
        detector = HandDetector(detectionCon=0.8, maxHands=2)
        while flag:
            img=q.get()
            hands = detector.findHands(img, draw=False)
            q2.put(img)
            if hands:
                q3.put(hands[0]['lmList'])
            q.task_done()
    
     
        
if __name__ == '__main__':

    
    threadRecorder = Thread(target=Recorder.recordImage)
    threadRecorder.start()
    
    threadTracker = Thread(target=HandTracker.trackHands)
    threadTracker.start()
    
    threadShowing = Thread(target=Showing.showImage)
    #threadShowing.start()
    
    #threadShowing.join()
    threadTracker.join()
    threadRecorder.join()
