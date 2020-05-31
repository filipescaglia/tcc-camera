import sys, requests, time, datetime, os, cv2
from gpiozero import MotionSensor
from picamera import PiCamera
from detection import detection

sys.path.append('./dependencies')

HOST = "http://192.168.15.10:8000"
CAMERA_CODE = 123456
CAMERA_SECRET = 123456

# Run when camera turns on
def start_camera():
    try:
        url = HOST + "/camera"

        headers = { "content-type": "multipart/form-data",
                    "accept": "application/json" }

        camera = PiCamera()

        image = getFileName() # Gets a filename

        camera.capture(image) # Gets the image from camera

        # Não sei se vai funcinar na PiCamera (Provalvemente vai)
        imencoded = cv2.imencode(".jpeg", image)[1]
        file = { "image": (image, imencoded.tostring(), "image/jpeg") } 

        data = { "code": CAMERA_CODE, "secret": CAMERA_SECRET }

        response = requests.post(url, data=data, files=file)

        print(response)

    except Exception as e:
        print(e)
        pass

def send_alert(camera_id, image, frame):
    try:
        
        url = HOST + '/api/alert'

        headers = { 'content-type': "multipart/form-data",
                    'accept': "application/json" }

        data = { 'code': CAMERA_CODE, 'secret': CAMERA_SECRET, 'has_human': 1 }

        file = { 'image': (image, frame.tostring(), 'image/jpeg') }

        response = requests.post(url, data=data, files=file)

        print(response.text)
    except Exception as e:
        print(e)
        pass

# Function to create new Filename from date and time into 'images' folder
def getFileName():
    return 'images/' + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")

def resizeImage(image):
    resize = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    scale_percent = 38 # percent of original size
    width = int(resize.shape[1] * scale_percent / 100)
    height = int(resize.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(resize, dim, interpolation = cv2.INTER_AREA)
    cv2.imwrite(image, resized)

def genLog(type):
    f = open("logs/" + datetime.datetime.now().strftime("%Y-%m-%d.txt"), "a+")
    if type == 'pes':
        f.write("Pessoa detectada em " + datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S") + "\r\n")
    elif type == 'mov':
        f.write("Movimento sem pessoa detectado em " + datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S") + "\r\n")
    f.close()

def getHour():
    return datetime.datetime.now().strftime("%H.%M.%S")

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
        print("Movimento detectado - " + getHour()) # Prints 'Movimento detectado' on terminal
        camera.capture(image) # Gets the image from camera
        print("Imagem capturada - " + getHour())
        resizeImage(image)
        confidence, frame = detection(image)
        if confidence != None:
            print("Pessoa detectada - " + getHour()) # Debugging
            send_alert(1, image, frame)
            genLog('pes') # Generates a person detection log
        else:
            genLog('mov') # Generates a motion detection log without a person
        eraseImages(execCount)

main()
