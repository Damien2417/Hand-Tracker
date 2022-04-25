#!/usr/bin/python
# -*- coding: utf-8 -*-
from cvzone.HandTrackingModule import HandDetector
import cv2
import math
import pyautogui

class Tracking:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(detectionCon=0.8, maxHands=1)
        self.frameToCalibre = 30
        self.distanceToCalibre=50
        self.calibStart = False
        self.calibFrame = 0
        self.calibPoint = []
        self.calibPointTemp = [[0, 0]]
        self.longueurIRL=62.5
        self.hauteurIRL=46.6
        self.diagonalIRL = math.sqrt(pow(self.longueurIRL, 2) + pow(self.hauteurIRL, 2))
        self.diagonal1920 = 2202.90717008
        self.diagonalFictive=0
        self.ratioIRL = self.diagonal1920 / self.diagonalIRL
        self.ratioFictif = 0
        self.ratioTotal = 0
        self.calibAngleEnd=False
        self.f=[0,0]
        self.frameCount=0
        self.lengthIndexMajeur2=0
        self.oldx=0
        self.oldy=0

    def calibration(self,img,posFingers,lengthIndexMajeur):
        # starting calibration
        font = cv2.FONT_HERSHEY_SIMPLEX
  
        if len(self.calibPoint) < 2:
            if lengthIndexMajeur > self.distanceToCalibre:
                cv2.putText(
                    img,
                    str(self.frameToCalibre - self.calibFrame),
                    (0, 100),
                    font,
                    1,
                    (0xFF, 0xFF, 0xFF),
                    2,
                    )
                (oldx, oldy) = self.calibPointTemp[0]
                self.calibPointTemp[len(self.calibPointTemp) - 1] = posFingers

                diff1 = oldx - self.calibPointTemp[0][0]
                if diff1 < 0:
                    diff1 *= -1
                diff2 = oldy - self.calibPointTemp[0][1]
                if diff2 < 0:
                    diff2 *= -1
                if ((diff1 < 5) & (diff2 < 5)):
                    self.calibFrame += 1
                else:
                    self.calibFrame = 0
                if self.calibFrame >= self.frameToCalibre:
                    self.calibPoint.append(self.calibPointTemp[0])
                    self.calibFrame = 0
                   
            else:
                self.calibFrame = 0
        if ((len(self.calibPoint) == 2) & (not self.calibAngleEnd)):
            self.diagonalFictive = math.sqrt(pow(self.calibPoint[0][1] - self.calibPoint[1][1], 2)+ pow(self.calibPoint[0][0] - self.calibPoint[1][0],2))
            self.ratioFictif=self.diagonalFictive / self.diagonalIRL
            self.ratioTotal=1/self.ratioFictif*self.ratioIRL
            self.f[0]=self.calibPoint[0][0]*self.ratioTotal
            self.f[1]=self.calibPoint[0][1]*self.ratioTotal
            self.calibAngleEnd=True
            self.calibStart=False                                      
        elif len(self.calibPoint) > 0:
            cv2.putText(
                img,
                str(len(self.calibPoint)) + ' points calibred',
                (0, 50),
                font,
                1,
                (0xFF, 0xFF, 0xFF),
                2,
                )
        else:
            cv2.putText(
                img,
                'Calibration...',
                (0, 50),
                font,
                1,
                (0xFF, 0xFF, 0xFF),
                2,
                )

    def setCoords(self,img,posFingers,lengthIndexMajeur):
        if lengthIndexMajeur > self.distanceToCalibre:
            """if len(hands)>1:
                if (lengthIndexMajeur2>50):
                    pyautogui.click()
                    print("click")"""
            
            x = (posFingers[0] * self.ratioTotal)-self.f[0]
            y = (posFingers[1] * self.ratioTotal)-self.f[1]
            
            #print('x:' + str(x) + ' y:' + str(y))
            pyautogui.moveTo(x, y,_pause=False)
            diff1=self.oldx-x
            if(diff1<0):
                diff1*=-1
            diff2=self.oldy-y
            if(diff2<0):
                diff2*=-1
            if(float(diff1)<20 and float(diff2)<20):
                if(self.frameCount>=10):
                    pyautogui.click()
                    self.frameCount=0
                else:
                    self.frameCount+=1
            self.oldx=x
            self.oldy=y
    
    def trackHand(self,img):
        hands = self.detector.findHands(img, draw=False)  # with draw
        # hands = detector.findHands(img, draw=False)  # without draw
        
        if hands:
            # Hand 1
            hand1 = hands[0]
            lmList1 = hand1['lmList']  # List of 21 Landmark points
            bbox1 = hand1['bbox']  # Bounding box info x,y,w,h
            centerPoint1 = hand1['center']  # center of the hand cx,cy
            handType1 = hand1['type']  # Handtype Left or Right
            lengthIndexMajeur, info, img = self.detector.findDistance(lmList1[8], lmList1[12], img)
            if len(hands) == 2:
                # Hand 2
                hand2 = hands[1]
                lmList2 = hand2['lmList']  # List of 21 Landmark points
                bbox2 = hand2['bbox']  # Bounding box info x,y,w,h
                centerPoint2 = hand2['center']  # center of the hand cx,cy
                handType2 = hand2['type']  # Hand Type "Left" or "Right"
                lengthIndexMajeur2, info2, img2 = self.detector.findDistance(lmList2[8], lmList2[12], img)
            return hands[0]['lmList'][8],lengthIndexMajeur;
        return None,None
    
    
    def baseLoop(self):
        while True:
            # Get image frame
            (success, img) = self.cap.read()
            
            img = cv2.flip(img, 1)
            
            main,lengthIndexMajeur=self.trackHand(img)
            if ((main is not None) & (lengthIndexMajeur is not None)):
                if self.calibStart:
                    self.calibration(img,main,lengthIndexMajeur)
                # Display
                if(self.calibAngleEnd):
                    self.setCoords(img,main,lengthIndexMajeur)
                                      
            if cv2.waitKey(1) & 0xFF == ord('c'):
                self.calibStart = True
                self.calibPoint = []
                self.calibPointTemp = [[0, 0]]
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            cv2.imshow('Image', img)
            #cv2.waitKey(1)
        self.cap.release()
        cv2.destroyAllWindows()
   
if __name__ == '__main__':
    start = Tracking()
    start.baseLoop()
