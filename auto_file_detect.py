#Swati Sriram Mani
#100168136

from socket import AF_INET, socket, SOCK_STREAM
import time
import os


# from movefiletry import move1
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from threading import Thread

isKill = False

#Referenced from http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html
class MyHandler(PatternMatchingEventHandler):
    # patterns = ["*.txt", "*.xml","*.pdf","*.py","*.jpg","*.xlsx"]
    print("Hello from auto_file_detect file!!")
    # ----Now comes the sockets part----
    HOST = 'localhost'
    PORT = 33000
    if not PORT:
        PORT = 33000
    else:
        PORT = int(PORT)

    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there

        print (event.src_path, event.event_type)  # print now only for debug


    #Checking if file is modified in any client directory, if yes then send the updated file to the server folder and do the next steps:
    def on_deleted(self, event):
        self.process(event)  #event object created saying that the a new file is created in the client folder being watched
        filename=(os.path.basename(event.src_path)) #extracting the name of the file
        clientname = os.path.basename(os.path.dirname(event.src_path)) #extracting the name of the folder
        msg = clientname+"~~~DeleteFileOperation~~~"+filename #sending this message to the server to perform the further actions
        print("new msgsgsg:",msg)
        path='C:/Users/Swati/PycharmProjects/ds_lab3/'+clientname+'/'
        print("hkwbfkw")
        #if os.path.isfile(path)==False: #checking if the file is present already in the folder
        #move1(self, filename, clientname) #calling function move1
        self.client_socket.send(bytes(msg, "utf8")) #sending the message to the server

#Referenced by http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html
#setting the observer on the client folder to detect the event that will take place
def auto_detect(clientfolder):
    args = os.getcwd() + "\\"+clientfolder
    observer = Observer()
    observer.schedule(MyHandler(), path=args if args else '.')
    observer.start()
    #kill the thread when the connection is stopped
    #https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
    global isKill
    try:
        while True:
            time.sleep(1)
            if isKill:
                observer.stop()
                break
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

#creating the threads for every client that is wanting to connect to the server
def new_thread(foldercount):
    print("foldercount",foldercount)
    new_t = Thread(target=auto_detect,args=(foldercount,))
    new_t.start()


def kill_thread():
    global isKill
    isKill = True