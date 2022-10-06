import face_recognition
import os
import pickle

path = './images/'
imagepaths = []
classNames = []
imageEncodes = []
myList = os.listdir(path)
images_count = len(myList)

for index, cl in enumerate(myList):
    print("Encoding " + cl + " (" + str(index + 1) + " of " + str(images_count) + ")")
    imagepath = path + cl
    imagepaths.append(imagepaths)
    classNames.append(os.path.splitext(cl)[0])
    image = face_recognition.load_image_file(imagepath)
    imageEncode = face_recognition.face_encodings(image)[0]
    imageEncodes.append(imageEncode)

with open('imageEncodes.pkl', 'wb') as f1:
    pickle.dump(imageEncodes, f1)

with open('classNames.pkl', 'wb') as f2:
    pickle.dump(classNames, f2)
