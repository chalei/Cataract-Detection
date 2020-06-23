#CREATED BY : DEDE ROHMAT H
#https://github.com/hahahihidede/Cataract-Detection
#buluidung69@gmail.com



import multiprocessing
import numpy as np
import cv2
import tensorflow.keras as tf
import pyttsx3
import math

def speak(speakQ, ):

    engine = pyttsx3.init()

    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume)  
   
    last_msg = ""
    
    while True:
        msg = speakQ.get()
       
        while not speakQ.empty():
            msg = speakQ.get()
       
        if msg != last_msg and msg != "Background":
            last_msg = msg
           
            engine.say(msg)
            engine.runAndWait()
        if msg == "Background":
            last_msg = ""



if __name__ == '__main__':

   
    labels_path = "mataa/labels.txt"

    labelsfile = open(labels_path, 'r')


    classes = []
    line = labelsfile.readline()
    while line:
        
        classes.append(line.split(' ', 1)[1].rstrip())
        line = labelsfile.readline()
    
    labelsfile.close()


    model_path = 'mataa/keras_model.h5'
    model = tf.models.load_model(model_path, compile=False)

 
    cap = cv2.VideoCapture(0)

    
    frameWidth = 1280
    frameHeight = 720

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frameWidth)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frameHeight)

    cap.set(cv2.CAP_PROP_GAIN, 0)

    speakQ = multiprocessing.Queue()


    p1 = multiprocessing.Process(target=speak, args=(speakQ, ), daemon="True")


    p1.start()

    while True:

        
        np.set_printoptions(suppress=True)

       
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

       
        check, frame = cap.read()
       
       
        margin = int(((frameWidth-frameHeight)/2))
        square_frame = frame[0:frameHeight, margin:margin + frameHeight]
       
        resized_img = cv2.resize(square_frame, (224, 224))
        
        model_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

        image_array = np.asarray(model_img)
        
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
       
        data[0] = normalized_image_array

 
        predictions = model.predict(data)

        
        conf_threshold = 90
        confidence = []
        conf_label = ""
        threshold_class = ""
       
        per_line = 2  
        bordered_frame = cv2.copyMakeBorder(
            square_frame,
            top=0,
            bottom=30 + 15*math.ceil(len(classes)/per_line),
            left=0,
            right=0,
            borderType=cv2.BORDER_CONSTANT,
            value=[0, 0, 0]
        )
   
        for i in range(0, len(classes)):
           
            confidence.append(int(predictions[0][i]*100))
           
            if (i != 0 and not i % per_line):
                cv2.putText(
                    img=bordered_frame,
                    text=conf_label,
                    org=(int(0), int(frameHeight+25+15*math.ceil(i/per_line))),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(255, 255, 255)
                )
                conf_label = ""

            conf_label += classes[i] + ": " + str(confidence[i]) + "%; "
       
            if (i == (len(classes)-1)):
                cv2.putText(
                    img=bordered_frame,
                    text=conf_label,
                    org=(int(0), int(frameHeight+25+15*math.ceil((i+1)/per_line))),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(255, 255, 255)
                )
                conf_label = ""
            
            if confidence[i] > conf_threshold:
                speakQ.put(classes[i])
                threshold_class = classes[i]
        
        cv2.putText(
            img=bordered_frame,
            text=threshold_class,
            org=(int(0), int(frameHeight+20)),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.75,
            color=(255, 255, 255)
        )

     
        cv2.imshow("Capturing", bordered_frame)
        cv2.waitKey(10)

        
    p1.terminate()
