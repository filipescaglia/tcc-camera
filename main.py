import sys
import requests

sys.path.append('./dependencies')

from detection import detection

def send_alert(camera_id, frame):
    try:
        
        url = 'http://192.168.15.10:8000/api/alert'

        headers = { 'content-type': "multipart/form-data",
                    'accept': "application/json" }

        data = { 'camera_id': camera_id, 'has_human': 1 }

        file = { 'image': ('image.jpeg', frame.tostring(), 'image/jpeg') }

        response = requests.post(url, data=data, files=file)

        print(response.text)
    except Exception as e:
        print(e)
        pass

def main():
    image = './image2.jpg'

    confidence, frame = detection(image)

    if confidence != None:
        send_alert(1, frame)


main()
