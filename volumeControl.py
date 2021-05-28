import numpy as np
import cv2
import time
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#####################################
wCam, hCam = 640, 480
#####################################

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
cTime = 0

detector = htm.handDetector(detectionConfidence = 0.7, maxHands = 1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

volBar = 400
volPer = volume.GetMasterVolumeLevelScalar() * 100
print(volPer)
Area = 0

while(True):
    #Capture frame by frame
    success, img = cap.read()

    #Find Hand
    img = detector.findHands(img, draw = False)
    lmList, bbox = detector.findPosition(img, draw = True)
    if len(lmList) != 0:

        #Filter Based on size
        Area = (bbox[2] - bbox[0])*(bbox[3] - bbox[1])//100
        #print(Area)

        if 250 < Area < 1000:
            #Find Distance between Index and Thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)
            #print(length)

            #Convert Volume
            #Hand Range from 30 to 180
            #Volume Range from -95 to 0

            volBar = np.interp(length, [30, 180], [400, 150])
            volPer = np.interp(length, [30, 180], [0, 100])
            #print(int(length), vol) 

            #Reduce resolution to make it smoother

            smoothness = 10
            volPer = smoothness * round(volPer/smoothness)

            #Check fingers up

            fingers = detector.fingersUp()
            #print(fingers)

            #If pinky is down set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer/100, None)
            #Drawings
            #Frame rate

            #print(lmList[4], lmList[8])

    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0))
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, "FPS: " + str(int(fps)), (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cv2.putText(img, "Vol: " + str(int(volPer)) + "%", (20, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    #Display the resulting frame
    cv2.imshow('Image', img)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

#When everything done release the capture
cap.release()
cv2.destroyAllWindows()