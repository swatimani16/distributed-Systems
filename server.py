#Swati Sriram Mani
#100168136
import threading
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import shutil
import os
from random import choice

clientNames=[]   #list of client names
l={}             #dictionary storing clientN:actualnames
file_list = []   #list of files comming from the client-side
delete_file_list = []   #list of files comming from the client-side for deletion
voteResponseCount = 0
requestorName = ''
fileunderdeletion = ''
timedOut = False
'''Referred from: "https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170"'''

def file_present_check():
    cl=['client1','client2','client3']
    print("Heyyyyy")
    for h in cl:
        print(" h value", h)
        path1 = "C:/Users/Swati/PycharmProjects/triallll/"+h
        path = "C:/Users/Swati/PycharmProjects/triallll/server_folder"
        f_names=[]
        f_names1=[]
        for root1, d_names1, f_names1 in os.walk(path1):
            f_names1= f_names1
            for root, d_names, f_names in os.walk(path):
                f_names= f_names
        for j in f_names1:
            if j in f_names:
                print("Okay")
            else:
                source = 'C:/Users/Swati/PycharmProjects/triallll/' + h + '/' + j
                # destination Path
                dest = shutil.copy(source, 'C:/Users/Swati/PycharmProjects/triallll/server_folder/')
                print("copied the file in the server folder since copy not present ")




def accept_incoming_connections():
    #Sets up handling for incoming clients
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Enter your Username and press Send!", "utf8"))   #sending the message to the client side through the socket
        addresses[client] = client_address                     #Storing the addresses of the clients asking to be connected
        Thread(target=handle_client, args=(client,)).start()   #Creating a new thread to handle the client connections inside the handle_client()



'''Referred from: "https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170"'''
def handle_client(client):  # Takes client socket as argument.
    global l
    file_present_check()
    global requestorName
    global fileunderdeletion
    global timedOut

    while True:
        try:
            msg = client.recv(BUFSIZ).decode("utf8")
            msg_fragments = msg.split("~~~")    #getting the message from the clientside and splitting it into fragments to divide it so as to perform different actions
            clientN = msg_fragments[0]          #containing the name of the client connecting to the server
            clientOperation = msg_fragments[1]  #containing the operation performed
            print("OPERATION",clientOperation)
            if clientOperation == "Modified":
                if clientN in l.values():     #checking if client is already connected to server or not
                    wel = 'Sorry %s already connected! If you want to connect, Re-enter another username.' % clientN
                    client.send(bytes(wel, "utf8"))
                    msg3 = "%s already Connected!" % clientN
                    msg_list.insert(0, msg3)
                else:
                    clientNames.append(clientN)
                    welcome = str(len(clientNames))+'~~~Modified~~~Welcome %s! If you ever want to quit, type quit to exit.' % clientN
                    client.send(bytes(welcome, "utf8"))
                    clients[clientN] = client
                    msg3 = "%s is connected now!" % clientN
                    msg_list.insert(0,msg3)
                    broadcast(msg3)
                    l["client"+str(len(clients))] = clientN

            if clientOperation == "Quit":  #if the operation is Quit, remove the connection,delete from the list of clients and broadcast the message saying that client has left the network
                l = {key:val for key,val in l.items() if val!=clientN} #checking the items in the dictionary l for the value not equal to the clientN
                #print("After quit l values: "+str(l))
                clients.pop(clientN)  #removing the clientN from the clients dictionary
                clientNames.remove(clientN) #removing the ClientN from the clientNames list
                msg3 = "%s left network!" % clientN
                #print("msg3", msg3)
                msg_list.insert(tkinter.END, msg3)
                broadcast(msg3)

            if clientOperation == "DeleteFileOperation" and msg_fragments[2] not in delete_file_list:  # if operation is modify,check if file is present in the list of files
                delete_file_list.append(msg_fragments[2])
                msg3 = l[clientN]+" Deleted "+msg_fragments[2]+" and vote request is being sent to other parties"
                uni_msg = clientN+"~~~FileDeleteRequest~~~"+msg_fragments[2]
                unicast(uni_msg,clientN) #send message to the client sayin a file has been detected
                print("AFTER")
                #print("msg3", msg3)
                msg_list.insert(tkinter.END, msg3)
                print("AFTER Deleting files from all clients")
            if clientOperation == "GetVote":
                # global requestorName
                global timedOut
                requestorName = clientN
                fileunderdeletion = msg_fragments[3]
                print("getVote: ",msg)
                print("clients: ", clients)
                timedOut = False
                timer = threading.Timer(3.1, checkTimeout)
                timer.start()

                for i in clients:
                    if i != clientN:
                        print("ClientUni: ", i)
                        vmsg = clientN+"~~~VoteFile~~~"+msg_fragments[3]
                        # unicast(vmsg,i)
                        clients[i].send(bytes(vmsg, "utf8"))

            if clientOperation == "VoteResponse":
                # global requestorName
                print("IN VoteResponse:")
                global voteResponseCount

                print("VoteResponse: ", msg)
                if msg_fragments[2]=="No" and timedOut==False:
                    timedOut = True
                    delete_file_list.remove(fileunderdeletion)
                    abortMsg = clientN+"~~~AbortDelete~~~"+fileunderdeletion
                    print("AbortDelete", abortMsg)
                    print("RequestorName:",requestorName)
                    clients[requestorName].send(bytes(abortMsg, "utf8"))
                    # unicast(abortMsg,requestorName)
                    recover_file(fileunderdeletion,requestorName)
                if msg_fragments[2]=="Yes" and timedOut==False:
                    voteResponseCount += 1
                    print("VoteCount",voteResponseCount)
                    if voteResponseCount == (len(clients)-1):
                        timedOut = True
                        print("Delete Majority recieved")
                        # abortMsg = clientN+"~~~AbortDelete~~~"+msg_fragments[2]
                        # unicast(abortMsg,requestorName)
                        deleted_files(fileunderdeletion,requestorName)
                        voteResponseCount = 0

        except Exception:
            break


def checkTimeout():
    global timedOut
    global fileunderdeletion
    global requestorName
    if not timedOut:
        timedOut = True
        delete_file_list.remove(fileunderdeletion)
        abortMsg = "ServerTimeOut~~~AbortDelete~~~" + fileunderdeletion
        print("AbortDelete", abortMsg)
        print("RequestorName:", requestorName)
        clients[requestorName].send(bytes(abortMsg, "utf8"))
        # unicast(abortMsg,requestorName)
        recover_file(fileunderdeletion, requestorName)

'''Referred from: "https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170"'''
def broadcast(msg):
    """Broadcasts a message to all the clients."""
    for sock in clients:
        print("sock",sock)
        clients[sock].send(bytes(msg, "utf8"))

def unicast(msg,clientname):  # prefix is for name identification.
    """Unicast a message to the clients."""
    print("Unicast:",msg)
    #print("int:"+str(int(str(clientname).replace("client",""))))
    s= clientNames[int(str(clientname).replace("client",""))-1]
    sock=clients[s]
    print("sockujhj:",sock,s)
    # print("UniMsg:"+msg)
    sock.send(bytes(msg, "utf8"))


'''Referenced: https://docs.python.org/2/library/shutil.html
https://www.geeksforgeeks.org/python-shutil-copytree-method/'''
def deleted_files(filename,clientname):  #moving the files
    global l
    print("Delete:",l)
    # source = 'C:/Users/Swati/PycharmProjects/ds_lab3/' + clientname + '/' + filename
    #checking the list by iterating through it
    clientname = list(l.keys())[list(l.values()).index(clientname)]
    for i in l:
        print("i inside", i)
        if (i != clientname and filename not in file_list):  #if clientname not in the l and the filename is not present in the file_names list(to remove the issue of duplication)
            print("i inside",i)
            # dest = shutil.copy(source, 'C:/Users/Swati/PycharmProjects/ds_lab3/' + i + '/')
            os.remove('C:/Users/Swati/PycharmProjects/ds_lab3/' + i + '/' + filename)
            print("HAPPENING",'C:/Users/Swati/PycharmProjects/ds_lab3/' + i + '/')
            msg7 = "File Deleted from other clients: "+filename
            unicast(msg7, i)
    #
    #  file_list.append(filename)


def recover_file(filename,clientname):
    global l
    print("Recover:",l)
    source = 'C:/Users/Swati/PycharmProjects/ds_lab3/server_folder/'+filename
    dest = list(l.keys())[list(l.values()).index(clientname)]
    print("Source:", source)
    print("Dest:",dest)
    d = shutil.copy(source, 'C:/Users/Swati/PycharmProjects/ds_lab3/' + dest + '/')
    print("Done Copy")
    msg="Recovered file "
    unicast(msg, clientname)
    #checking the list by iterating through it
    # for i in l:
    #     print("i inside", i)
    #     # if (i != clientname and filename not in file_list):  #if clientname not in the l and the filename is not present in the file_names list(to remove the issue of duplication)
    #     print("i inside",i)
    #     dest = shutil.copy(source, 'C:/Users/Swati/PycharmProjects/ds_lab3/' + i + '/'+filename)
    #     # os.remove('C:/Users/Swati/PycharmProjects/ds_lab3/' + i + '/')
    #     print("HAPPENING",'C:/Users/Swati/PycharmProjects/ds_lab3/' + i + '/')
    #     msg7 = "File recovered to client which had deleted the file: "+filename
    #     unicast(msg7, i)

def server_start():
    SERVER.listen(3)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)   #Creating the thread for the incoming clients
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()


'''Referred from: "https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170"'''
top1 = tkinter.Tk()
top1.title("Server")

messages_frame = tkinter.Frame(top1)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Welcome to the Server!!Waiting for Connection from Client!!")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

#To display the List of Clients
def list_clients():
    msg_list.insert(tkinter.END,clients.keys())

#to display the list of files in the folder of the server
def display_files():
    path='C:/Users/Swati/PycharmProjects/ds_lab3/server_folder/'
    files = os.listdir(path)
    for i in files:
        msg_list.insert(tkinter.END, i)
#buttons for viewing the files in server folder and the clients connected
list_b=tkinter.Button(top1, text="View Clients Connected!", command=list_clients)
list_b.pack()
list_f=tkinter.Button(top1, text="Files in Server Folder", command=display_files)
list_f.pack()


#allocating the addresses for the server to run on

clients = {}
addresses = {}


HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

Thread(target=server_start).start() #creation of the thread


tkinter.mainloop()  #Start of the GUI
