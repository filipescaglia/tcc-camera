import sys, requests, time, datetime, os
from gpiozero import MotionSensor
from picamera import PiCamera
from detection import detection

sys.path.append('./dependencies')

def send_alert(camera_id, image, frame):
    try:
        
        url = 'http://192.168.15.10:8000/api/alert'

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

def genLog(type):
    f = open("logs/" + datetime.datetime.now().strftime("%Y-%m-%d.txt"), "a+")
    if type == 'pes':
        f.write("Pessoa detectada em " + datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S") + "\r\n")
    elif type == 'mov':
        f.write("Movimento sem pessoa detectado em " + datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S") + "\r\n")
    f.close()

def eraseImages(count):
    if count == 10:
        folder = './images/'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        count = 0

def main():
    pir = MotionSensor(26)
    camera = PiCamera()
    execCount = 0

    while True:    
        execCount += 1
        image = getFileName() # Gets a filename
        pir.wait_for_motion() # Waits for motion on the sensor
        print("Movimento detectado - " + datetime.datetime.now().strftime("%H.%M.%S")) # Prints 'Movimento detectado' on terminal
        #camera.start_preview() # Starts camera live preview
        camera.capture(image) # Gets the image from camera
        #camera.stop_preview() # Stops camera live preview
        confidence, frame = detection(image)
        if confidence != None:
            send_alert(1, image, frame)
            print("Pessoa detectada - " + datetime.datetime.now().strftime("%H.%M.%S")) # Debugging
            genLog('pes') # Generates a person detection log
        else:
            genLog('mov') # Generates a motion detection log without a person
        eraseImages(execCount)
        time.sleep(2) # Waits 2 seconds for another work cycle

main()
