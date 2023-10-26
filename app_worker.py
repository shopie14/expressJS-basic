# worker.py
import os
import pika
import cv2
import dlib
import pymongo
from ftplib import FTP
import face_recognition
from run import load_encoder
import pytz
from datetime import datetime
import json
import uuid
import hashlib

FTP_HOST = 'ftp5.pptik.id'
FTP_PORT = 2121
FTP_USER = 'magangitg'
FTP_PASS = 'bWFnYW5naXRn'

RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'face_lskk'
encoder_filename = 'final_training.p'
encoder = load_encoder(encoder_filename)

# fungsi untuk membaca gambar
def read_img(path):
    img = cv2.imread(path)
    (h, w) = img.shape[:2]
    width = 500
    ratio = width / float(w)
    height = int(h * ratio)
    return cv2.resize(img, (width, height))

# fungsi untuk mendapatkan waktu saat ini
def get_current_time():
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    return now.strftime('%Y-%m-%d %H:%M:%S')

# fungsi untuk mengupload file ke FTP
def upload_file_to_ftp(file_path, filename):
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)
    ftp.cwd('./face_reports/report_lskk/')
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {filename}', file)

# fungsi untuk mendownload file dari FTP
def download_file_from_ftp(file_name):
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)
    ftp.cwd('./face_reports/report_lskk/')    

    local_file_path = os.path.join('downloads/', file_name)
    with open(local_file_path, 'wb') as file:
        ftp.retrbinary(f'RETR {file_name}', file.write)

    ftp.quit()


# fungsi untuk menyimpan hasil ke MongoDB
def save_result_to_mongodb(resi, file_name, result, status):
    client = pymongo.MongoClient('mongodb://magangitg:bWFnYW5naXRn@database2.pptik.id:27017/?authMechanism=DEFAULT&authSource=magangitg')
    db = client['magangitg']
    collection = db['face_lskk']

    post = {"resi": resi, "filename": file_name, "result": result, "status": status}
    post_id = collection.insert_one(post).inserted_id
    print('Successfully inserted document with post_id: {}'.format(post_id))
 
# fungsi untuk membandingkan wajah yang ada di database dengan wajah yang ada di gambar   
def compare_face(image_path, encoder):
    img = read_img(image_path)
    current_time = get_current_time()
    
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_locations = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(face_locations) == 0:
        return {"result": "No face detected.", "image_path": image_path, "detected_faces": []}
    
    detected_faces = []
    
    for (x, y, w, h) in face_locations:
        face_img = img[y:y+h, x:x+w]
        
        face_encodings = face_recognition.face_encodings(face_img)
        
        if not face_encodings:
            continue
        
        probabilitas = []
        
        for name, encoding in encoder.items():
            result = face_recognition.compare_faces([encoding], face_encodings[0])[0]
            distance = face_recognition.face_distance([encoding], face_encodings[0])[0]
            probability = 1 / (1 + distance)
            probabilitas.append((name, probability))
        
        probabilitas.sort(key=lambda x: x[1], reverse=True)
        
        identity = probabilitas[0][0] if probabilitas[0][1] > 0.7 else "Unknown"
        detected_faces.append({"name": identity, "probability": probabilitas[0][1], "timestamp": current_time})
        
        
        result ={
            "name": detected_faces[0]['name'],
            "probability": detected_faces[0]['probability'],
            'image_path': image_path,
            "timestamp": current_time,
        }
        
        return result
    
# fungsi untuk memproses gambar yang di download dari FTP
def process_image(file_name, encoder):
    download_file_from_ftp(file_name)
    print(f'Downloaded file: {file_name} from FTP to local')
    local_file_path = os.path.join('downloads/', file_name)
    
    # create unique filename
    resi = hashlib.md5(file_name.encode()).hexdigest() + '_' + datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = resi + '.' + file_name.rsplit('.', 1)[1]
    
    # unique_id = str(uuid.uuid4())
    # file_extension = file_name.rsplit('.', 1)[1]
    # file_name = f"{unique_id}.{file_extension}"
    status = 'processing'
    

    # Perform face detection
    # img = cv2.imread(local_file_path)

    # encode face
    encoder_filename = 'final_training.p'
    encoder = load_encoder(encoder_filename)
    
    # Inisialisasi detector
    result = compare_face(local_file_path, encoder)
    outpus_json = json.dumps(result, indent=4, default=str)
    
    status = "success processing" if result.get("name", "") != "unknown" else "failed processing"
    
    # Save the result to MongoDB
    save_result_to_mongodb(resi, file_name, result, status)
    print(f'File processed: {file_name}, result: {outpus_json}, status: {status}')


# fungsi untuk mengirim pesan ke worker  
def send_message_to_worker(filename):
     connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
     channel = connection.channel()
     channel.queue_declare(queue=RABBITMQ_QUEUE)
     channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=filename)
     

# fungsi untuk menerima pesan dari server
def callback(ch, method, properties, body):
    print('⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️')
    print(f"Received message from server: {(body.decode())}")
    file_name = body.decode()
    process_image(file_name, encoder)

if __name__ == '__main__':
    mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    mq_channel = mq_connection.channel()
    mq_channel.queue_declare(queue=RABBITMQ_QUEUE)

    mq_channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    mq_channel.start_consuming()