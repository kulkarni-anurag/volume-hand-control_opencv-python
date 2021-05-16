import numpy as np
import cv2
import time
import HandTrackingModule as htm
import math
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

detector = htm.handDetector(detectionConfidence = 0.7)

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
volPer = 0

while(True):
    #Capture frame by frame
    success, img = cap.read()

    img = detector.findHands(img, draw = False)
    lmList = detector.findPosition(img, draw = False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        cx, cy = (x1 + x2)//2, (y1 + y1)//2

        cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)

        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        #cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)
        #print(length)

        #Hand Range from 30 to 180
        #Volume Range from -95 to 0

        vol = np.interp(length, [30, 180], [minVol, maxVol])
        volBar = np.interp(length, [30, 180], [400, 150])
        volPer = np.interp(length, [30, 180], [0, 100])
        #print(int(length), vol)

        volume.SetMasterVolumeLevel(vol, None)

        #if length < 30:
           #cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

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