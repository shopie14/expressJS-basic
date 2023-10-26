# server.py
import os
import datetime
from flask import Flask, request
from ftplib import FTP
import hashlib
import pika
import pymongo
import pytz
from app_worker import send_message_to_worker, upload_file_to_ftp, get_current_time
app = Flask(__name__)

# database connection
client = pymongo.MongoClient('mongodb://magangitg:bWFnYW5naXRn@database2.pptik.id:27017/?authMechanism=DEFAULT&authSource=magangitg')
db = client['magangitg']
collection = db['face_lskk']

FTP_HOST = 'ftp5.pptik.id'
FTP_PORT = 2121
FTP_USER = 'magangitg'
FTP_PASS = 'bWFnYW5naXRn'

RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'face_lskk'


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
        
def send_message_to_worker(filename):
     connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
     channel = connection.channel()
     channel.queue_declare(queue=RABBITMQ_QUEUE)
     channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=filename)
    
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    resi = hashlib.md5(file.filename.encode()).hexdigest() + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = resi + '.' + file.filename.rsplit('.', 1)[1]
    file_path = os.path.join('uploads/', filename)
    file.save(file_path)
    
    
    file_info = {
        'resi': resi, 
        'filename': filename,
        'status': 'processing', 
        'timestamp': get_current_time(),
    }
    
    collection.insert_one(file_info)

    upload_file_to_ftp(file_path, filename)
    print(f'File {filename} successfully uploaded to FTP')
    send_message_to_worker(filename)
    print(f'Message sent to worker to process {filename}')

    return 'File successfully uploaded and message sent to worker', 200

@app.route('/check/<resi>', methods=['POST'])
def check_status(resi):
    file_info = collection.find_one({'resi': resi})
    
    if file_info:
        if 'name' in file_info:
            status = 'success processing'
        else:
            status = 'processing'
        
        result = collection.find_one({'filename': file_info['filename']})
        
        if result:
            file_info.update(result)
            
    else:
        status = 'not found'

    response = {
        'resi': resi,
        'status': status,
    }

    return response, 200

if __name__ == '__main__':
    app.run(port=8080, debug=True)