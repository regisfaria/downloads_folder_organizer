"""
 This code tracks a given folder and will transfer any files to a destiny folder

 My goal here is to give a destination whenever a file is found in downloads folder
and transfer it to a related folder.

--- Exemple cases:
1. If I download a image, ending with ".jpg", ".jpeg", ".png" I will send it to the Pictures folder
   A video, to the videos folder
   and so on...

Must read/watch links:

 The below link will teach me how to use a unix application that runs python code whenever a new file is
found on a folder:
https://askubuntu.com/questions/781799/execution-permission-to-all-files-created-under-a-specific-directory-by-default/781909#781909

--------------------------------------------------------
Next steps:
[OK] Develop a way to move pictures 
[OK] Develop a way to move pdfs
[OK] Wait for files that can be being downloaded, before moving it
[ ] Find more about how can a code be called everytime we have a new file in the folder
[ ] Make a installation shell script
[ ] Make a windows build


"""
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

import json
import getpass
import os
import time
import shutil
import sys
import logging

# Directory setup
script_directory = os.path.dirname(os.path.abspath(__file__))
script_name = os.path.basename(__file__)

# Logs directory setup
logs_directory = os.path.join(script_directory, 'logs')
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)

# LOGGING
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_template = '%(asctime)s %(module)s %(levelname)s: %(message)s'
formatter = logging.Formatter(log_template)

# Logging - File Handler
log_file_size_in_mb = 10
count_of_backups = 5  # example.log example.log.1 example.log.2
log_file_size_in_bytes = log_file_size_in_mb * 1024 * 1024
log_filename = os.path.join(logs_directory, os.path.splitext(script_name)[0]) + '.log'
file_handler = handlers.RotatingFileHandler(log_filename, maxBytes=log_file_size_in_bytes,
                                            backupCount=count_of_backups)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Logging - STDOUT Handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


folder_prefix = "/home/" + sys.argv[1] + "/"
downloads_folder = folder_prefix + "Downloads"
def type_check(filename):
    # Folder settings
    pictures_folder = folder_prefix + "Pictures"
    documents_folder = folder_prefix + "Documents"
    videos_folder = folder_prefix + "Videos"
    
    # Get file extention
    extention = filename.split('.')[-1]
    
    # File extention settings
    # DEVNOTE: I will add more extentions when needed
    img_extentions = ['jpg', 'jpeg', 'png']
    docs_extentions = ['pdf']
    video_extentions = ['mp4', 'mkv', 'avi', 'AVI']

    # check if that kind of file will be moved
    if extention in img_extentions:
        new_destination = pictures_folder
    elif extention in docs_extentions:
        new_destination = documents_folder
    elif extention in video_extentions:
        new_destination = videos_folder
    # If the file is not on the ext list, I won't move it
    else:
        new_destination = False

    return new_destination

def is_downloading(filepath):
    while True:
        actual_size = os.stat(filepath)[6]
        time.sleep(2.5)
        modified_size = os.stat(filepath)[6]
        if actual_size == modified_size:
            return
    
##############################################################################################

class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        for filename in os.listdir(downloads_folder):
            new_destination = type_check(filename)
            # Add move date to the file name
            try:
                if sys.argv[2] == "-format":
                    new_name = "[" + str(datetime.now()).split()[0] + "]" + filename
            except:
                new_name = filename
            
            try:
                # if we will move the file AND the file don't exists on the destiny folder
                if new_destination and not os.path.isfile(new_destination + "/" + new_name):            
                    logging.debug('Moving file "{}" to {} directory'.format(filename, new_destination.split('/')[-1]))
                    # Set paths
                    src = downloads_folder + "/" + filename
                    new_destination += "/" + new_name
                    
                    # Check if the file is downloading
                    is_downloading(src)

                    shutil.move(src, new_destination)
                    time.sleep(1)
                    # Sometimes we have a junk file on the old folder, so we will delete it, if it's there
                    try:
                        os.remove(src)
                    except:
                        continue
            except Exception as e:
                logger.debug("A problem was found: {}".format(e))
                logger.debug('Error found when moving file "{}"'.format(filename))
                logger.debug("Please contact: regisprogramming@gmail.com for bug report")


##############################################################################################

'''
07/04/2020 TO DO: look into how __init__ works [ ]

below is the code starter... I should look on how to make a __init__.py or even a __init__ function
'''
event_handler = Handler()
observer = Observer()
observer.schedule(event_handler, downloads_folder, recursive=True)
observer.start()

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    observer.stop()

observer.join()