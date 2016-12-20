import socket
import sys
import json
import os
from pprint import pprint
import base64
import fileinput

def getFileSize(filename):
        st = os.stat(filename)
        return st.st_size

def recvmsg(sock, recv_buffer=1024, delim='}'):
    buffer = ''
    data = True
    while data:
        data = sock.recv(recv_buffer)
        #print data
        buffer += data
        #print buffer

        if buffer.find(delim) != -1:
            #msg, buffer = buffer.split('\n', 1)
            yield buffer
            return
    


if len(sys.argv) < 3:
    print 'the program needs 2 arguments'
    exit()

param_1 = sys.argv[1]
param_2 = sys.argv[2] 

if param_1 == '-config':
    with open(param_2) as con_file:
        data = json.load(con_file)

label = 1

print 'reading configuration information from json file'
print 'homrdir      ', data["homedir"]
print 'shard1ip ', data["shard1ip"]
print 'shard1port   ', data["shard1port"]
print 'shard2ip ', data["shard2ip"]
print 'shard2port   ', data["shard2port"]

server_address1 = (data["shard1ip"], int(data["shard1port"]))
server_address2 = (data["shard2ip"], int(data["shard2port"]))

# data["homedir"] is sha1_dir
# data["listenport"] is 10007
# data["metadatafile"] is meta1.txt
# data["shard1ip"] is localhost
# data["shard1port"] is 10007

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock3 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host =''
# Connect the socket to the port where the server is listening
server_address = (host, int(data["listenport"]))
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(10)

while True:
    # Wait for a connection
    print 'waiting for a client to connect'
    connection, client_address = sock.accept()

    
    print 'connection from', client_address
    recv_data = ''
    for buffer in recvmsg(connection):
        recv_data = buffer
    json_obj = json.loads(recv_data)
    
    if json_obj['MessageType'] == 'BYTESTORED':
        print 'received status query from client'
        f = open(data["metadatafile"],'r+')
        line = f.readline()
        msg_to_send = {'MessageType': 'BYTESTORED', 'BytesStored': str(int(line))}
        encoded_msg = json.dumps(msg_to_send)
        #encoded_msg = base64.b64encode(encoded_msg)
        #connection.sendall(encoded_msg)
        while encoded_msg:
            bytes = connection.send(encoded_msg)
            encoded_msg = encoded_msg[bytes:]

        print 'reply was ' + str(int(line)) + ' bytes'
        #connection.shutdown(socket.SHUT_WR)
        #connection, client_address = sock.accept()

        try:
            recv_data = ''
            for buffer in recvmsg(connection):
                recv_data = buffer
            json_obj = json.loads(recv_data)
        except Exception, e:
            print str(e)
            continue


        print 'received upload request of ' + str(int((int(json_obj['BytesTo']) - int(json_obj['BytesFrom'])))) + ' bytes for ' + json_obj['Filename']

        if json_obj['MessageType'] == 'DATA':
            print 'received file'
            f = open(json_obj['Filename'],'w+')
            f.write(base64.b64decode(json_obj['Data']))
            f.close()
            print 'saved file'

            msg_to_send = {'MessageType': 'Message', 'Content': 'Done'}
            #print msg_to_send
            encoded_msg = json.dumps(msg_to_send)
            #print encoded_msg
            #encoded_msg = base64.b64encode(encoded_msg)
            #print encoded_msg
            #connection.sendall(encoded_msg)
            while encoded_msg:
                bytes = connection.send(encoded_msg)
                encoded_msg = encoded_msg[bytes:]
            #connection.shutdown(socket.SHUT_WR)

            with open(data["metadatafile"],'r') as file:
                file_contents = file.readlines()
            size = getFileSize(json_obj['Filename'])
            meta_size = int(file_contents[0])
            meta_size += size
            file_contents[0] = str(meta_size)+'\n'

            with open(data["metadatafile"],'w') as file:
                file.writelines( file_contents )

            with open(data["metadatafile"],'a') as file:
                file.write(json_obj['Filename']+'\n'+str(size)+'\n'+json_obj['BytesFrom']+'\n'+json_obj['BytesTo']+'\n')

            sock2.connect(server_address1)
            sock3.connect(server_address2)

            f = open(json_obj['Filename'],'r+')

            size = getFileSize(json_obj['Filename'])
            if size % 2 != 0:
                to_shard2 = size/2
                to_shard3 = size/2 + 1 #1 extra byte
            else:
                to_shard2 = size/2
                to_shard3 = size/2


            msg_to_send2 = {'MessageType': 'BACKUPDATA', 'Filename': str(json_obj['Filename']), 'BytesFrom': json_obj['BytesFrom'], 'BytesTo': str(int(json_obj['BytesFrom'])+to_shard2 - 1), 'Data': base64.b64encode(str(f.read(to_shard2)))}
            msg_to_send3 = {'MessageType': 'BACKUPDATA', 'Filename': str(json_obj['Filename']), 'BytesFrom': str(int(json_obj['BytesFrom'])+to_shard2), 'BytesTo': str(int(json_obj['BytesFrom'])+to_shard2 + to_shard3 - 1), 'Data': base64.b64encode(str(f.read(to_shard3)))}
            encoded_msg2 = json.dumps(msg_to_send2)
            encoded_msg3 = json.dumps(msg_to_send3)
            while encoded_msg2:
                bytes = sock2.send(encoded_msg2)
                encoded_msg2 = encoded_msg2[bytes:]
            print 'sent backup bytes to shard 2'

            while encoded_msg3:
                bytes = sock3.send(encoded_msg3)
                encoded_msg3 = encoded_msg3[bytes:]
            print 'sent backup bytes to shard 3'

            sock2.close()
            sock3.close()


    
    #elif json_obj['MessageType'] == 'BACKUPDATA1':
    #    f = open(str('backup1'+json_obj['Filename']),'w+')
    #    f.write(base64.b64decode(json_obj['Data']))
    #    f.close()
    #    with open(data["metadatafile"],'r') as file:
    #        file_contents = file.readlines()
    #    size = getFileSize(json_obj['Filename'])
    #    meta_size = int(file_contents[0])
    #    meta_size += size
    #    file_contents[0] = str(meta_size)+'\n';

    #    with open(data["metadatafile"],'w') as file:
    #        file.writelines( file_contents )

    #    with open(data["metadatafile"],'a') as file:
    #        file.write(json_obj['Filename']+'\n'+str(size)+'\n')
    

    elif json_obj['MessageType'] == 'BACKUPDATA':
        f = open(str('backup'+str(label)+json_obj['Filename']),'w+')
        f.write(base64.b64decode(json_obj['Data']))
        f.close()
        
        with open(data["metadatafile"],'r') as file:
            file_contents = file.readlines()
        size = getFileSize(str('backup'+str(label)+json_obj['Filename']))
        meta_size = int(file_contents[0])
        meta_size += size
        file_contents[0] = str(meta_size)+'\n'

        with open(data["metadatafile"],'w') as file:
            file.writelines( file_contents )

        with open(data["metadatafile"],'a') as file:
            file.write(str('backup'+str(label)+json_obj['Filename'])+'\n'+str(size)+'\n'+json_obj['BytesFrom']+'\n'+json_obj['BytesTo']+'\n')
        label = label+1;
        

    elif json_obj['MessageType'] == 'FILEINFO':
        print 'received download query from client'
        with open(data["metadatafile"],'r') as file:
            file_contents = file.readlines()

        i = 1
        isFileFound = 0
        while file_contents[i:]:
            if file_contents[i] == str(json_obj['Filename']+'\n'):
                isFileFound = 0
                break
            else:
                isFileFound = 1
            i+= 4

        if isFileFound == 1:
            print 'no file found'
        else:
            #if str(file_contents[i+4]) == str('backup2'+file_contents[i]):
            BytesF2 = str(int(file_contents[i+6]))
            BytesT2 = str(int(file_contents[i+7]))
            BytesF3 = str(int(file_contents[i+10]))
            BytesT3 = str(int(file_contents[i+11]))
            #else:
            #    BytesF2 = str(int(file_contents[i+10]))
            #    BytesT2 = str(int(file_contents[i+11]))
            #    BytesF3 = str(int(file_contents[i+6]))
            #    BytesT3 = str(int(file_contents[i+7]))
            if BytesF3 < BytesF2:
                temp1 = BytesF3
                temp2 = BytesT3
                BytesF3 = BytesF2
                BytesT3 = BytesT2
                BytesF2 = temp1
                BytesT2 = temp2

            msg_to_send = {'MessageType': 'FILEINFO', 'Filename': str(json_obj['Filename']), 'BytesFrom': str(int(file_contents[i+2])), 'BytesTo': str(int(file_contents[i+3])), 'BytesFrom2': BytesF2, 'BytesTo2': BytesT2, 'BytesFrom3': BytesF3, 'BytesTo3': BytesT3}
            encoded_msg = json.dumps(msg_to_send)
            #encoded_msg = base64.b64encode(encoded_msg)
            #connection.sendall(encoded_msg)
            print 'sending FILEINFO for ' + json_obj['Filename']
            while encoded_msg:
                bytes = connection.send(encoded_msg)
                encoded_msg = encoded_msg[bytes:]
            #connection.shutdown(socket.SHUT_WR)
            #connection, client_address = sock.accept()
            recv_data = ''
            for buffer in recvmsg(connection):
                recv_data = buffer
            #print recv_data
            #while True:
            #    read_data = connection.recv(1024)
            #    recv_read_data = recv_read_data + read_data
            #    print >>sys.stderr, 'received "%s"' % read_data
            #    if not read_data:
            #        break

        #decode = base64.b64decode(recv_read_data)
        json_obj = json.loads(recv_data)
        print 'recieved file download request for ' + json_obj['Filename']
        #print json_obj
        if json_obj['MessageType'] == 'REQUESTDATA':
            f = open(json_obj['Filename'],'r+')
            msg_to_send = {'MessageType': 'DATA', 'Filename': str(json_obj['Filename']), 'BytesFrom': json_obj['BytesFrom'], 'BytesTo': json_obj['BytesTo'], 'Data': base64.b64encode(str(f.read()))}
            encoded_msg = json.dumps(msg_to_send)
            #encoded_msg = base64.b64encode(encoded_msg)
            #connection.sendall(encoded_msg)
            while encoded_msg:
                bytes = connection.send(encoded_msg)
                encoded_msg = encoded_msg[bytes:]
                #connection.shutdown(socket.SHUT_WR)
            print 'file sent!!'
            recv_data = ''
            for buffer in recvmsg(connection):
                recv_data = buffer
            #print recv_data
            try:
                json_obj = json.loads(recv_data)
            except Exception, e:
                continue
            #print json_obj
            print json_obj['MessageType']
            if json_obj['MessageType'] == 'REQUESTDATA':
                with open(data["metadatafile"],'r') as file:
                    file_contents = file.readlines()
                    i = 1
                    isFileFound = 0
                    while file_contents[i:]:
                        if file_contents[i] == str(json_obj['Filename']+'\n'):
                            isFileFound = 0
                            break
                        else:
                            isFileFound = 1
                        i+= 4
                    #print json_obj['BytesFrom'])
                    #print json_obj['BytesTo']
                    #print json_obj['BytesFrom'])
                    #print json_obj['Filename']
                    if  int(json_obj['BytesFrom']) == int(file_contents[i+6]) and int(json_obj['BytesTo']) == int(file_contents[i+7]):
                        f = open(str(file_contents[i+4]).rstrip(),'r+')
                        msg_to_send = {'MessageType': 'DATA', 'Filename': str(json_obj['Filename']), 'BytesFrom': json_obj['BytesFrom'], 'BytesTo': json_obj['BytesTo'], 'Data': base64.b64encode(str(f.read()))}
                        encoded_msg = json.dumps(msg_to_send)
                        while encoded_msg:
                            bytes = connection.send(encoded_msg)
                            encoded_msg = encoded_msg[bytes:]
                        print 'backup file sent!!'
                    elif int(json_obj['BytesFrom']) == int(file_contents[i+10]) and int(json_obj['BytesTo']) == int(file_contents[i+11]):
                        f = open(str(file_contents[i+8]).rstrip(),'r+')
                        msg_to_send = {'MessageType': 'DATA', 'Filename': str(json_obj['Filename']), 'BytesFrom': json_obj['BytesFrom'], 'BytesTo': json_obj['BytesTo'], 'Data': base64.b64encode(str(f.read()))}
                        encoded_msg = json.dumps(msg_to_send)
                        while encoded_msg:
                            bytes = connection.send(encoded_msg)
                            encoded_msg = encoded_msg[bytes:]
                        print 'backup file sent!!'

    elif json_obj['MessageType'] == 'EraseAll':

        print 'received query to erase all data'
        with open(data["metadatafile"],'r') as file:
            file_contents = file.readlines()

        i = 1
        while file_contents[i:]:
            try:
                os.remove(file_contents[i].rstrip())
            except Exception, e:
                print str(e)
            i+= 4

        with open(data["metadatafile"],'w') as file:
                file.write('0\n')

        msg_to_send = {'MessageType': 'DoesntMatter', 'Message': 'deleted everything'}
        encoded_msg = json.dumps(msg_to_send)
        #encoded_msg = base64.b64encode(encoded_msg)
        #connection.sendall(encoded_msg)
        while encoded_msg:
            bytes = connection.send(encoded_msg)
            encoded_msg = encoded_msg[bytes:]

        print 'reply was ' + '\'deleted everything\''