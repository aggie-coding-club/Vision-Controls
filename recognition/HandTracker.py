# Using python version 3.7.9 for media-pipe
import cv2
import mediapipe as mp
import numpy as np
import time

# Getting openCV ready
cap = cv2.VideoCapture(0)

# Dimensions of the camera output window
wCam = int(cap.get(3))
hCam = int(cap.get(4))

# For testing, write output to video
#out = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (wCam,hCam))

# Sets up list to use for averaging the gesture
frames_to_average = 5 # number of frames to average
prevGestures = [] # gestures calculated in previous frames

# Getting media-pipe ready
mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=.7)
mpDraw = mp.solutions.drawing_utils

# Vars used to calculate avg fps
prevTime = 0
currTime = 0
fpsList = []

def dotProduct(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]

def normalize(v):
    mag = np.sqrt(v[0] ** 2 + v[1] ** 2)
    v[0] = v[0] / mag
    v[1] = v[1] / mag
    return v

def gesture(f):
    """
    Uses the open fingers list to recognize gestures
    :param f: list of open fingers (+ num) and closed fingers (- num)
    :return: string representing the gesture that is detected
    """
    #print("Thumb is at:", f[0])
    if f[1] > 0 > f[2] and f[4] > 0 > f[3]:
        return "Rock & Roll"
    elif f[0] > 0 and (f[1] < 0 and f[2] < 0 and f[3] < 0 and f[4] < 0):
        return "Thumbs Up"
    elif f[0] < 0 and f[1] > 0 and f[2] < 0 and (f[3] < 0 and f[4] < 0):
        return "1 finger"
    elif f[0] < 0 and f[1] > 0 and f[2] > 0 and (f[3] < 0 and f[4] < 0):
        return "Peace"
    elif f[0] > 0 and f[1] > 0 and f[2] > 0 and f[3] > 0 and f[4] > 0:
        return "Open Hand"
    elif f[0] < 0 and f[1] < 0 and f[2] < 0 and f[3] < 0 and f[4] < 0:
        return "Fist"
    elif f[0] < 0 and f[1] > 0 and f[2] > 0 and f[3] > 0 and f[4] > 0: 
        return "4 fingers"
    elif f[0] < 0 and f[1] > 0 and f[2] > 0 and f[3] > 0 and f[4] < 0:
        return "3 fingers"
    else:
        return "No Gesture"

def calcFPS(pt, ct, framelist):
    fps = 1 / (ct - pt)
    if len(framelist) < 30:
        framelist.append(fps)
    else:
        framelist.append(fps)
        framelist.pop(0)
    return framelist

def findLandMarks(img):
    """
    Draws the landmarks on the hand (not being used currently)
    :param img: frame with the hand in it
    :return:
    """
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hands = mpHands.Hands()
    pHands = hands.process(imgRGB)

    if pHands.multi_hand_landmarks:
        for handlms in pHands.multi_hand_landmarks:
            # mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)
            mpDraw.draw_landmarks(img, handlms)

def straightFingers(hand, img):
    """
    Calculates which fingers are open and which fingers are closed
    :param hand: media-pipe object of the hand
    :param img: frame with the hand in it
    :return: list of open (+ num) and closed (- num) fingers
    """
    fingerTipIDs = [4, 8, 12, 16, 20]  # list of the id's for the finger tip landmarks
    openFingers = []
    lms = hand.landmark  # 2d list of all 21 landmarks with there respective x, an y coordinates
    for id in fingerTipIDs:
        if id == 4: # This is for the thumb calculation, because it works differently than the other fingers
            x2, y2 = lms[id].x, lms[id].y  # x, and y of the finger tip
            x1, y1 = lms[id-2].x, lms[id-2].y  # x, and y of the joint 2 points below the finger tip
            x0, y0 = lms[0].x, lms[0].y  # x, and y of the wrist
            fv = [x2-x1, y2-y1]  # joint to finger tip vector
            fv = normalize(fv)
            pv = [x1-x0, y1-y0]  # wrist to joint vector
            pv = normalize(pv)

            thumb = dotProduct(fv, pv)
            # Thumb that is greater than 0, but less than .65 is typically
            # folded across the hand, which should be calculated as "down"
            if thumb > .65:
                openFingers.append(thumb)  # Calculates if the finger is open or closed
            else:
                openFingers.append(-1)

            # Code below draws the two vectors from above
            cx, cy = int(lms[id].x * wCam), int(lms[id].y * hCam)
            cx2, cy2 = int(lms[id-2].x * wCam), int(lms[id-2].y * hCam)
            cx0, cy0 = int(lms[0].x * wCam), int(lms[0].y * hCam)
            cv2.line(img, (cx0, cy0), (cx2, cy2), (255, 0, 0), 2)
            if dotProduct(fv, pv) >= .65:
                cv2.line(img, (cx, cy), (cx2, cy2), (0, 255, 0), 2)
            else:
                cv2.line(img, (cx, cy), (cx2, cy2), (0, 0, 255), 2)

        else: # for any other finger (not thumb)
            x2, y2 = lms[id].x, lms[id].y  # x, and y of the finger tip
            x1, y1 = lms[id-2].x, lms[id-2].y  # x, and y of the joint 2 points below the finger tip
            x0, y0 = lms[0].x, lms[0].y  # x, and y of the wrist
            fv = [x2-x1, y2-y1]  # joint to finger tip vector
            fv = normalize(fv)
            pv = [x1-x0, y1-y0]  # wrist to joint vector
            pv = normalize(pv)
            openFingers.append(dotProduct(fv, pv))  # Calculates if the finger is open or closed

            # Code below draws the two vectors from above
            cx, cy = int(lms[id].x * wCam), int(lms[id].y * hCam)
            cx2, cy2 = int(lms[id-2].x * wCam), int(lms[id-2].y * hCam)
            cx0, cy0 = int(lms[0].x * wCam), int(lms[0].y * hCam)
            cv2.line(img, (cx0, cy0), (cx2, cy2), (255, 0, 0), 2)
            if dotProduct(fv, pv) >= 0:
                cv2.line(img, (cx, cy), (cx2, cy2), (0, 255, 0), 2)
            else:
                cv2.line(img, (cx, cy), (cx2, cy2), (0, 0, 255), 2)
            # cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
    return openFingers

def getHand(handedness):
    '''
    Mediapipe assumes that the camera is mirrored
    :param handedness: media-pipe object of handedness
    :return: string that is 'Left' or 'Right'
    '''
    hand = handedness.classification[0].label

    if(hand == 'Left'):
        return 'Right'
    else:
        return 'Left'

def logFile(file, leftGestures, rightGestures):
    # left = ", ".join(f'"{x}"' for x in leftGestures)
    # right = ", ".join(f'"{x}"' for x in rightGestures)
    # file.write(f'{{ "time":{time.time()}, "left":[{left}], "right":[{right}]}}\n')
    left = 'null'
    if leftGestures:
        left = f'"{leftGestures[0]}"'
    right = 'null'
    if rightGestures:
        right = f'"{rightGestures[0]}"'
    file.write(f'{{"left":{left}, "right":{right}}}\n')

outFile = open('log.txt', 'w') 
# Used this command for HandEvents.py for testing
# cat log.txt | jq -s "map(.right)" -cM > log.json

frame_count = 0
while True:
    """
    Main code loop
    """
    # Gets the image from openCV and gets the hand data from media-pipe
    success, img = cap.read()

    # If there are no more frames, break loop
    if img is None:
        print("Video ended. Closing.")
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    leftPrevGestures = []
    rightPrevGestures = []
    # if there are hands in frame, calculate which fingers are open and draw the landmarks for each hand
    if results.multi_hand_landmarks:
        for handLms, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            fingers = straightFingers(handLms, img)
            hand = getHand(handedness)
            if hand == "Left":
                leftPrevGestures.append(gesture(fingers))
            else:
                rightPrevGestures.append(gesture(fingers))
            frame_count += 1
            #mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            mpDraw.draw_landmarks(img, handLms)
        
        logFile(outFile, leftPrevGestures, rightPrevGestures)
        # averages 'frames_to_average' amount of frames before deciding on the gesture
        if frame_count > (frames_to_average - 1):
            if (len(rightPrevGestures) != 0 and all(x == rightPrevGestures[0] for x in rightPrevGestures)):
                print('Right: ', rightPrevGestures[0])
            if (len(leftPrevGestures) != 0 and all(x == leftPrevGestures[0] for x in leftPrevGestures)):
                print('Left: ', leftPrevGestures[0])
            prevGestures = []
            frame_count = 0

    # Used for fps calculation
    currTime = time.time()
    fpsList = calcFPS(prevTime, currTime, fpsList)
    prevTime = currTime

    # Displays the fps
    cv2.putText(img, str(int(np.average(fpsList))), (10, 70),
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

    cv2.imshow("Video with Hand Detection", img)

    # Used for testing, writing video to output
    #out.write(img)

    cv2.waitKey(1)