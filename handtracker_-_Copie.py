#!/usr/bin/python
# -*- coding: utf-8 -*-
from cvzone.HandTrackingModule import HandDetector
import cv2
import math
import pyautogui
import queue
from multiprocessing import Process
import multiprocessing as mp

class Camera:
    def __init__(self):      
        self.flag=True
        """self.baseImageQueue = queue.Queue()
        self.processedImageQueue = queue.Queue()
        self.finalQueue = queue.Queue()"""

        self.baseImageQueue = mp.Queue()
        self.processedImageQueue = mp.Queue()
        self.finalQueue = mp.Queue()
    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.processRecordAndShow = Process(target=self.recordImageAndShow)
        self.processRecordAndShow.start()
        self.processProcess = Process(target=self.treatImage)
        self.processProcess.start()
        self.processWriteBeforeShow = Process(target=self.writeOnImage)
        self.processWriteBeforeShow.start()
        return self
    
    def recordImageAndShow(self):
        while self.flag:          
            # Get image frame
            (success, img) = self.cap.read()
            #self.baseImageQueue.put(img)           
            #img = cv2.flip(img, 1)
            
            cv2.imshow('my webcam', img)       
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.flag=False
                break
        self.baseImageQueue.join()
        # After the loop release the cap object
        self.cap.release()
        # Destroy all the windows
        cv2.destroyAllWindows()
        self.processRecordAndShow.join()

    def treatImage(self):
        while self.flag:
            if not self.baseImageQueue.empty():
                self.processedImageQueue.put(self.baseImageQueue.get())
                self.baseImageQueue.task_done()
        self.processedImageQueue.join()
        self.processProcess.join()

    def writeOnImage(self):
        while self.flag:
            if not self.processedImageQueue.empty():
                self.finalQueue.put(self.processedImageQueue.get())
                self.processedImageQueue.task_done()
        self.finalQueue.join()
        self.processWriteBeforeShow.join()
        
          
if __name__ == '__main__':
    Camera().start()
    
    
    
