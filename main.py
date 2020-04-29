import sys
import requests
from gpiozero import MotionSensor
from picamera import PiCamera
import time
import datetime

sys.path.append('./dependencies')

from detection import detection

def send_alert(camera_id, image, frame):
    try:
        
        url = 'http://192.168.15.21:8000/api/alert'

        headers = { 'content-type': "multipart/form-data",
                    'accept': "application/json" }

        data = { 'camera_id': camera_id, 'has_human': 1 }

        file = { 'image': (image, frame.tostring(), 'image/jpeg') }

        response = requests.post(url, data=data, files=file)

        print(response.text)
    except Exception as e:
        print(e)
        pass

# Function to create new Filename from date and time into 'images' folder
def getFileName():
    return 'images/' + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")

def main():
    pir = MotionSensor(26)
    camera = PiCamera()

    while True:    
        image = getFileName() # Gets a filename
        pir.wait_for_motion() # Waits for motion on the sensor
        print("Movimento detectado") # Prints 'Movimento detectado' on terminal
        #camera.start_preview() # Starts camera live preview
        camera.capture(image) # Gets the image from camera
        #camera.stop_preview() # Stops camera live preview
        confidence, frame = detection(image)
        if confidence != None:
            send_alert(1, image, frame)
        time.sleep(5) # Waits 5 seconds for another work cycle

main()
