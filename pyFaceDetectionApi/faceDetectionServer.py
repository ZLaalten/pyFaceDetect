from crypt import methods
import json
from operator import methodcaller
from pydoc import classname
from turtle import distance
from flask import Flask, request, jsonify
from PIL import Image
import face_recognition
import pickle
import os

image_path = './images/'

app = Flask(__name__)

@app.route("/img_list", methods=["GET"])
def list_images():
    images = os.listdir(image_path)
    return jsonify({'msg' : 'success', 'images' : images})

@app.route("/img_encodes_list", methods = ["GET"])
def list_image_encodes():
    classNames = []
    with open('classNames.pkl', 'rb') as f1:
        classNames = pickle.load(f1)
    return jsonify({'msg' : 'success', 'image_encodes' : classNames})

@app.route("/img_store", methods=["POST"])
def store_image():
    file = request.files['image']
    # Read the image via file.stream
    img = Image.open(file.stream)
    img.save(image_path + file.filename)
    return jsonify({'msg': 'success', 'size': [img.width, img.height]})

@app.route("/img_encode", methods=["POST"])
def encode_image():
    fname = request.form.get("fname")
    try:
        image = face_recognition.load_image_file(image_path + fname)
        imageEncode = face_recognition.face_encodings(image)[0]
        imageEncodes.append(imageEncode)
        classNames.append(fname)
        updateEncodesToFile()
        response = jsonify({'msg' : 'success', 'encoded_file' : fname})
    except Exception as e:
        response = jsonify({'msg' : 'failed', 'reason' : str(e)})
    return response

@app.route("/img_process", methods=["POST"])
def process_image():
    file = request.files['image']
    img = Image.open(file.stream)
    img.save(image_path + file.filename)
    try:
        image = face_recognition.load_image_file(image_path  + file.filename)
        imageEncode = face_recognition.face_encodings(image)[0]
        classNames.append(file.filename)
        imageEncodes.append(imageEncode)
        updateEncodesToFile()
        response = jsonify({'msg': 'success', 'size': [img.width, img.height], 'status':'encoded'})
    except Exception as e:
        os.remove(image_path + file.filename)
        response = jsonify({'msg': 'failed', 'reason' : str(e)})
    return response

@app.route("/img_update", methods=["POST"])
def update_image():
    image_updated = False
    file = request.files['image']
    fname = file.filename
    for index,className in enumerate(classNames):
            if(className == fname):
                img = Image.open(file.stream)
                img.save(image_path + file.filename)
                del classNames[index]
                del imageEncodes[index]
                classNames.append(fname)
                image = face_recognition.load_image_file(image_path  + fname)
                imageEncode = face_recognition.face_encodings(image)[0]
                imageEncodes.append(imageEncode)
                updateEncodesToFile()
                image_updated = True
    if(image_updated):
        response = jsonify({'msg': 'success', 'size': [img.width, img.height]})
    else:
        response = jsonify({'msg': 'failed'})
    return response

@app.route("/img_delete", methods=["POST"])
def delete_image():
    deletion_successful = False
    try:
        fname = request.form.get("fname")
        if(fname==None):
            response = jsonify({'msg' : 'failed', 'reason' : 'fname must pe passed'})
        else:
            try:
                for index,className in enumerate(classNames):
                    if(className == fname):
                        del classNames[index]
                        del imageEncodes[index]
                        updateEncodesToFile()
                        os.remove(image_path + fname)
                        deletion_successful = True
                if(not(deletion_successful)):
                    response = jsonify({'msg' : 'failed', 'action' : fname + ' could not be deleted'})
                else:
                    response = jsonify({'msg' : 'success', 'action' : fname + ' deleted'})
            except Exception as e:
                response = jsonify({'msg': 'failed', 'reason' : str(e)})
    except Exception as e:
        response = jsonify({'msg' : 'failed', 'reason' : str(e)})
    return response

@app.route("/img_delete_all", methods=["POST"])
def delete_all_images():
    global classNames, imageEncodes
    deletion_successful = False
    key = request.form.get("key")
    if(key==None):
            response = jsonify({'msg' : 'failed', 'reason' : 'key must pe passed'})
    elif(key!="Fret@091"):
        response = jsonify({'msg' : 'failed', 'reason' : 'incorrect key'})
    else:
        try:
            classNames = []
            imageEncodes = []
            updateEncodesToFile()
            images = os.listdir(image_path)
            for fname in images:
                os.remove(image_path + fname)
            deletion_successful = True
            if(not(deletion_successful)):
                response = jsonify({'msg' : 'failed', 'action' : 'Files could not be deleted'})
            else:
                response = jsonify({'msg' : 'success', 'action' : 'All files successfully deleted'})
        except Exception as e:
            response = jsonify({'msg' : 'failed', 'reason' : str(e)})
    return response

@app.route("/img_detect", methods = ["POST"])
def detect_image():
    distance_found = 1.0
    file = request.files['image']
    unknownImage = face_recognition.load_image_file(file)
    try:
        unknownImageEncode = face_recognition.face_encodings(unknownImage)[0]
        detected_image = 'Nan.jpg'
        for index, imageEncode in enumerate(imageEncodes):
            if(face_recognition.compare_faces([unknownImageEncode], imageEncode)[0]== True ):
                distance = face_recognition.face_distance([unknownImageEncode], imageEncode)
                if(distance < distance_found):
                    distance_found = distance
                    detected_image = classNames[index]   
        response =  jsonify({'msg' : 'success', 'detected_class' : detected_image.split('.')[0], 'distance' : str(distance_found)})
    except Exception as e:
        response = jsonify({'msg' : 'failed', 'reason' : 'No face found in image'})
    return response
    
classNames = []
imageEncodes = []

def updateEncodesFromFile():
    global imageEncodes, classNames
    try:
        with open('classNames.pkl', 'rb') as f1:
            classNames = pickle.load(f1)
    except:
        classNames = []
    try:    
        with open('imageEncodes.pkl', 'rb') as f2:
            imageEncodes = pickle.load(f2)
    except:
        imageEncodes = []

def updateEncodesToFile():
    global imageEncodes, classNames
    with open('imageEncodes.pkl', 'wb') as f1:
        pickle.dump(imageEncodes, f1)
    with open('classNames.pkl', 'wb') as f2:
        pickle.dump(classNames, f2)    


if __name__ == "__main__":
    updateEncodesFromFile()
    app.run(host='0.0.0.0')