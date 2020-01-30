#Swati Sriram Mani
#100168136
import shutil
filename=""

'''https://docs.python.org/2/library/shutil.html
https://www.geeksforgeeks.org/python-shutil-copytree-method/'''

def move1(self,filename,clientname):
    # Source path
    print("In moving function")
    source = 'C:/Users/Swati/PycharmProjects/ds_lab3/'+clientname+'/'+filename
    #destination Path
    dest = shutil.copy(source, 'C:/Users/Swati/PycharmProjects/ds_lab3/server_folder/')

    return filename
