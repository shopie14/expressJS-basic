import cv2
import face_recognition
import numpy as np
import os
import json
import pickle
import re
import uuid 

def read_img(path):
    img = cv2.imread(path)
    (h, w) = img.shape[:2]
    width = 500
    ratio = width / float(w)
    height = int(h * ratio)
    return cv2.resize(img, (width, height))

def load_encoder(filename):
    # Load the face encoding data from a pickle file
    with open(filename, 'rb') as f:
        return pickle.load(f)

def process_test_images(test_folder, encoder, output_path):
    results_data = []

    # Load Haar Cascade Classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Iterate through each file in the test folder, sorted by numeric value in filename
    for file in sorted(os.listdir(test_folder), key=lambda x: int(re.search(r'\d+', x).group())):  
        output_file = os.path.join(output_path, file)
        
        # Skip files that have already been processed
        if os.path.exists(output_file):
            print("Skipping", file, "- Already processed.")
            continue
        
        print("Processing", file)
        img = read_img(os.path.join(test_folder, file))
        
        # Convert the image to grayscale for Haar Cascade detection
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces using Haar Cascade Classifier
        face_locations = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        detected_faces = []
        
        # If no faces are detected, mark as Unknown
        if len(face_locations) == 0:
            print("No face detected in", file)
            detected_faces.append({"name": "Unknown", "probability": 0.0})
            if detected_faces[0]["name"] == "Unknown":
                cv2.imwrite(output_file, img)
            results_data.append({
                "file": file,
                "detected_faces": detected_faces
            })
            continue
        
        for (x, y, w, h) in face_locations:
            face_img = img[y:y+h, x:x+w]
            
            face_encodings = face_recognition.face_encodings(face_img)
            
            if not face_encodings:
                continue  # Skip unrecognized face
            
            probabilitas = []
            
            for name, encoding in encoder.items():
                result = face_recognition.compare_faces([encoding], face_encodings[0])[0]
                distance = face_recognition.face_distance([encoding], face_encodings[0])[0]
                probability = 1 / (1 + distance)
                probabilitas.append((name, probability))
            
            probabilitas.sort(key=lambda x: x[1], reverse=True)
            
            if float(probabilitas[0][1]) > 0.7:  # Set a threshold for face recognition
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                text = f"{probabilitas[0][0]} - {probabilitas[0][1]:.2f}"
            else:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
                text = f"Unknown - {probabilitas[0][1]:.2f}"
                probabilitas[0] = ("Unknown", probabilitas[0][1])  # Update the label to "Unknown"
            
            cv2.putText(img, text, (x+2, y+h+20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
            
            detected_faces.append({"name": probabilitas[0][0], "probability": probabilitas[0][1]})
            
        cv2.imwrite(output_file, img)
        
        results_data.append({
            "file": file,
            "detected_faces": detected_faces
        })
        print(json.dumps(results_data[-1], indent=4))  # Print the current processed image result
    
    # Write the results to a JSON file in the 'predict' folder
    json_filename = os.path.join(output_path, "results.json")
    with open(json_filename, "w") as json_file:
        json.dump(results_data, json_file, indent=4)
    
    print("Processing completed.")

def process_single_image(image_path, encoder):
    img = read_img(image_path)
    
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
        detected_faces.append({"x": x, "y": y, "w": w, "h": h, "identity": identity, "probability": probabilitas[0][1]})
    
    return {
        "result": "Processing completed.", 
        "image_path": image_path, 
        "detected_faces": detected_faces, 
        "processed_image": img
    }

def main():
    test_folder = 'dataset/test'       
    output_path = 'dataset/predict'     
    encoder_filename = 'encoder.p'     
    
    encoder = load_encoder(encoder_filename)
    process_test_images(test_folder, encoder, output_path)

if __name__ == "__main__":
    main()