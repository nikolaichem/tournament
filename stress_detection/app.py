import cv2
import dlib
import numpy as np
import pandas as pd
import imutils
from imutils import face_utils
from scipy.spatial import distance




def eyebrow_dist(left_eb, right_eb):
    dist = distance.euclidean(left_eb, right_eb)
    eyebrow_points.append(dist)
    return dist


def lip_dist(top_point, bott_point):
    dist = distance.euclidean(top_point, bott_point)
    mouth_points.append(dist)
    return dist
    

def min_max_stress_scaler(dist_eb, points_eyebrow, dist_mouth, points_mouth):
    norm_eb_dist = abs(dist_eb) 
    log_eb_dist = np.log10(norm_eb_dist)
    norm_mouth_dist = abs(dist_mouth) 
    log_mouth_dist = np.log10(norm_mouth_dist)
    pre_stress_value = (log_eb_dist + log_mouth_dist) / 2
    stress_value = np.exp(-(pre_stress_value))
    if stress_value > 0.5:
        stress_label = "Stressed"
    else:
        stress_label = "Not stressed"
    return stress_label, stress_value

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
cap = cv2.VideoCapture(0)


while True:
    # capture the image from the webcam
    ret, image = cap.read()
  
    # convert the image color to grayscale
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  
    # detect the face 
    rects = detector(gray_img, 1)

    # detect landmarks for face
    (l_begin, l_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eyebrow"]
    (r_begin, r_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eyebrow"]
    (lips_lower, lips_upper) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

    for rect in rects:
        shape = predictor(gray_img, rect)
        # convert to np array
        shape_np = np.zeros((68, 2), dtype="int")
        for i in range(68):
            shape_np[i] = (shape.part(i).x, shape.part(i).y)
        shape = shape_np.copy()

        # detect the parts of face
        left_eb = shape[l_begin:l_end]
        right_eb = shape[r_begin:l_begin]
        mouth = shape[lips_lower:lips_upper]
        
        # make hull transform of landmarks
        left_eb_hull = cv2.convexHull(left_eb)
        right_eb_hull = cv2.convexHull(right_eb)
        mouth_hull = cv2.convexHull(mouth)
       

        # display the convexed landmarks
        cv2.drawContours(image, [left_eb_hull], -1, (0, 255, 0), 1)
        cv2.drawContours(image, [right_eb_hull], -1, (0, 255, 0), 1)
        cv2.drawContours(image, [mouth_hull], -1, (0, 255, 0), 1)
        
        # for i, (x, y) in enumerate(shape):
        #     cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
        mouth_points = []
        eyebrow_points = []
        lip_distance = lip_dist(mouth_hull[-1], mouth_hull[0])
        eb_distance = eyebrow_dist(left_eb_hull[-1].flatten(), right_eb_hull[-1].flatten())

        # calculate stress-level
        label_stress, value_stress = min_max_stress_scaler(eb_distance, eyebrow_points, lip_distance, mouth_points)

        if pd.isna(value_stress * 100) == True:
            continue

        # picture text parameters
        text_one = f"Stress value: {str(value_stress * 100)}"
        origin_one = (10, 40)
        text_two = f"Stress level: {label_stress}"
        origin_two = (10, 60)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, text_one, origin_one, font, 0.5, (0, 0, 255), 2)
        cv2.putText(image, text_two, origin_two, font, 0.5, (0, 0, 255), 2)
        
    # # display the image zz
    cv2.imshow("Stress Level Detection", image)
    

    # press Esc to terminate the session
    if cv2.waitKey(10) == 27:
        break


cv2.destroyAllWindows()
cap.release()
        