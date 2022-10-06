from gzip import FNAME
import time
from unittest import case
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import pickle
import face_recognition
from debounce import debounce

image_path = "./images/"

t0 = time.time()
t1 = time.time()

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

def updateListToPkl():
    with open('imageEncodes.pkl', 'wb') as f1:
        pickle.dump(imageEncodes, f1)
    with open('classNames.pkl', 'wb') as f2:
        pickle.dump(classNames, f2)

print(imageEncodes)
print(classNames)

if __name__ == "__main__":
    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

def on_created(event):
    global t0 
    t0 = time.time()
    fname = event.src_path.split('/')[-1]
    print("Creating " + fname)
    classNames.append(fname)
    image = face_recognition.load_image_file(image_path + fname)
    imageEncode = face_recognition.face_encodings(image)[0]
    imageEncodes.append(imageEncode)
    updateListToPkl()

 
def on_deleted(event):
    global t0
    t0 = time.time()
    fname = event.src_path.split('/')[-1]
    print("Deleting " + fname)
    for index,className in enumerate(classNames):
        if(className == fname):
            del classNames[index]
            del imageEncodes[index]
            updateListToPkl()

@debounce(1) 
def on_modified(event):
    t1 = time.time()
    if(t1-t0 > 2):
        fname = event.src_path.split('/')[-1]
        print("Modifying " + fname)
        for index,className in enumerate(classNames):
            if(className == fname):
                del classNames[index]
                del imageEncodes[index]
                classNames.append(fname)
                image = face_recognition.load_image_file(image_path  + fname)
                imageEncode = face_recognition.face_encodings(image)[0]
                imageEncodes.append(imageEncode)
                updateListToPkl()
                

# def on_moved(event):
#     pass

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
# my_event_handler.on_moved = on_moved

path = image_path
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)
my_observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()