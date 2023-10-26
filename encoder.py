import cv2
import face_recognition
import os
import pickle
import json

def read_img(path):
    img = cv2.imread(path)
    (h, w) = img.shape[:2]
    width = 500
    ratio = width / float(w)
    height = int(h * ratio)
    return cv2.resize(img, (width, height))

def format_name(name):
    # Ubah setiap kata menjadi huruf kapital
    name = ' '.join([word.capitalize() for word in name.split()])
    
    # Pecah nama menjadi dua kata jika tidak mengandung spasi dan huruf kapital berurutan
    if name.isupper() and len(name) > 1:
        for i in range(1, len(name)):
            if name[i].isupper():
                name = name[:i] + ' ' + name[i:]
                break
    
    return name

def encode_reports_dataset_cleaning(reports_dataset_cleaning_folder, known_encodings):
    known_names = set(known_encodings.keys())
    successful_encodings = 0  # Inisialisasi jumlah file yang berhasil diencode
    failed_encodings = []  # Inisialisasi list file yang gagal diencode

    for root, dirs, files in os.walk(reports_dataset_cleaning_folder):
        for file in files:
            if file.endswith(".jpg"):
                name = os.path.splitext(file)[0]  # Remove file extension
                name = ''.join(filter(str.isalpha, name))  # Remove numbers
                name = format_name(name)  # Format nama
                
                if name not in known_names:
                    img = read_img(os.path.join(root, file))
                    face_encodings = face_recognition.face_encodings(img)

                    if len(face_encodings) > 0:
                        img_enc = face_encodings[0]
                        known_encodings[name] = img_enc
                        known_names.add(name)  # Add to the set
                        successful_encodings += 1  # Tambahkan 1 ke jumlah yang berhasil diencode
                    else:
                        failed_encodings.append(file)  # Tambahkan file yang gagal diencode ke dalam list

    return successful_encodings, failed_encodings

def save_encoder(encoder, filename):
    with open(filename, 'wb') as f:
        pickle.dump(encoder, f)

def main():
    encoder_filename = 'final_training.p'
    # encoder_filename = 'manual_encoder.p'
    # encoder_filename = 'mtcnn_encoder.p'
    # encoder_filename = 'mtcnn_with_parameter.p'
    # encoder_filename = 'harcascade_encoder.p'

    
    known_encodings = {}
    
    if os.path.exists(encoder_filename):
        with open(encoder_filename, 'rb') as f:
            known_encodings = pickle.load(f)
            
        print("Encoder file already exists. Loading existing data.")
    else:
        print("Encoder file does not exist. Creating new encoding data.")


    # reports_dataset_cleaning_folder = 'repots_dataset'
    reports_dataset_cleaning_folder = 'final_dataset/training'

    # reports_dataset_cleaning_folder = 'manual_cleaned'
    # reports_dataset_cleaning_folder = 'mtcnn_cleaned'
    # reports_dataset_cleaning_folder = 'mtcnn_cleaned_parameter'
    # reports_dataset_cleaning_folder = 'haar_cascade_cleaned_dataset'


    if os.path.exists(reports_dataset_cleaning_folder):
        successful_encodings, failed_encodings = encode_reports_dataset_cleaning(reports_dataset_cleaning_folder, known_encodings)
        save_encoder(known_encodings, encoder_filename)

        # Print known names sorted alphabetically
        known_names = set(known_encodings.keys())
        print("Number of known names:", len(known_names))
        sorted_names = sorted(known_names)

        print("Known Names:", sorted_names)

        # Print jumlah file yang berhasil diencode
        print("Total Successful Encodings:", successful_encodings)

        # Print file yang gagal diencode
        print("Files Failed to Encode:", failed_encodings)

        # Simpan file yang gagal diencode ke dalam JSON
        failed_encodings_json = json.dumps(failed_encodings)
        with open('final_training.json', 'w') as json_file:
            json_file.write(failed_encodings_json)

if __name__ == "__main__":
    main()
