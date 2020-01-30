#Swati Sriram Mani
#100168136

"""Script for Tkinter GUI """
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import socket
import auto_file_detect
import os
from random import choice
import time

client_folder_name = "client"

'''Referred from: "https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170"'''
def receive():

    """Handles receiving of messages."""
    global client_folder_name #storing the names of the client folders into this list
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf-8")
            #print("msg",msg)
            msg_fragments = str(msg).split("~~~")
            if(len(msg_fragments) == 3):
                if msg_fragments[1] == 'Modified':
                    msg_list.insert(tkinter.END, msg_fragments[2])
                    #print("This is first")
                    #print(msg)
                    client_folder_name = client_folder_name+str(msg_fragments[0])
                    auto_file_detect.new_thread('client'+msg_fragments[0])
                if msg_fragments[1] == 'FileDetected':
                    mymsg = "File modified in folder "+msg_fragments[0]+" named "+msg_fragments[2]
                    msg_list.insert(tkinter.END,mymsg)
                if msg_fragments[1] == 'FileDeleteRequest':
                    mymsg = "File Delete request in folder "+msg_fragments[0]+" named "+msg_fragments[2]
                    msg_list.insert(tkinter.END,mymsg)
                    global client_name
                    voteMsg = client_name+"~~~GetVote"+"~~~Sending vote msg to other clients for deleting~~~"+msg_fragments[2]
                    client_socket.send(bytes(voteMsg, "utf8"))  # sending the message to the server
                if msg_fragments[1] == 'VoteFile':
                    print("Before Sleep")
                    time.sleep(3)

                    myVote = choice(['Yes'])
                    myVoteMsg = client_name+"~~~VoteResponse~~~"+myVote
                    print("After Sleep vote:",myVote)
                    client_socket.send(bytes(myVoteMsg, "utf8"))  # sending the message to the server
                if msg_fragments[1] == 'AbortDelete':
                    print("Abort Delete",msg)
                    mymsg = "File Delete Operation for "+msg_fragments[2]+" was voted reject by client "+msg_fragments[0]
                    msg_list.insert(tkinter.END, mymsg)

            else:
                msg_list.insert(tkinter.END, msg)
            #print("from autodetect",filename)
        except OSError:  # Possibly client has left the chat.
            break
            # opening and writing into file received from Server

#this function isbeing invoked when the button is pressed after the client name has been entered
def send1(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get() #getting the name from the entry field on the GUI
    my_msg.set("")  # Clears input field.
    top.title(msg)
    global client_name
    client_name = msg
    msg = client_name+"~~~"+"Modified"
    client_socket.send(bytes(msg, "utf8")) #sending the message to the server


def exit1():
    """Handles sending of messages."""
    # msg = my_msg.get()
    # my_msg.set("")  # Clears input field.
    global client_name
    # client_name = msg
    msg = client_name + "~~~" + "Quit"
    client_socket.send(bytes(msg, "utf8")) #sending the message to server
    auto_file_detect.kill_thread()  #killing the thread of the client that has left the network
    client_socket.close() #closing the socket of the disconnected client
    top.destroy() #close the GUI of tkinter

'''Referred from: "https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170"'''
def on_closing():
    '''This function is to be called when the window is closed.'''
    # my_msg.set("{quit}")
    # send1()
    client_socket.send(bytes(client_name + "~~~Quit", "utf8"))
    client_socket.close()
    top.destroy()

top = tkinter.Tk()
def display_files(clientname):
    path='C:/Users/Swati/PycharmProjects/ds_lab3/'+clientname+'/'
    files = os.listdir(path)
    for i in files:
        msg_list.insert(tkinter.END,i)

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()
client_name = ""
entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send1)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send1)
send_button.pack()
view_files=tkinter.Button(top,text="View files in folder", command=lambda :display_files(client_folder_name))
view_files.pack()
exit_button = tkinter.Button(top, text="Exit", command=exit1)
exit_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
HOST = 'localhost'
PORT = 33000
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket.socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution