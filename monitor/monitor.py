import socket
import csv
import sys
import os
import json
from pprint import pprint
import base64
import fileinput
from time import sleep


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

isConnected1 = 0
isConnected2 = 0
isConnected3 = 0
isConnectedall = 0




param_1 = sys.argv[1]
param_2 = sys.argv[2] 

if param_1 == '-config':
    with open(param_2) as con_file:
        data = json.load(con_file)




print 'reading configuration information from json file'
print 'homrdir		', data["homedir"]
print 'shard1ip	', data["shard1ip"]
print 'shard1port	', data["shard1port"]
print 'shard2ip	', data["shard2ip"]
print 'shard2port	', data["shard2port"]
print 'shard3ip	', data["shard3ip"]
print 'shard3port	', data["shard3port"]

# data["homedir"] is cli_dir
# data["shard1ip"] is localhost
# data["shard1port"] is 10007

#server_address = [1 for i in range(3)]
server_address1 = (data["shard1ip"], int(data["shard1port"]))
server_address2 = (data["shard2ip"], int(data["shard2port"]))
server_address3 = (data["shard3ip"], int(data["shard3port"]))

socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socket2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socket3=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

while True:
	socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	socket2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	socket3=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	# Connect the sockets to the ports where the server is listening
	try:
		socket1.connect(server_address1)
		print 'connected to shard 1 at ip ' + data["shard1ip"] + 'and port ' + data["shard1port"]
		isConnected1 = 1
	except Exception, e:
		isConnected1 = 0
	try:
		socket2.connect(server_address2)
		print 'connected to shard 2 at ip ' + data["shard2ip"] + 'and port ' + data["shard2port"]
		isConnected2 = 1
	except Exception, e:
		isConnected2 = 0
	try:
		socket3.connect(server_address3)
		print 'connected to shard 3 at ip ' + data["shard3ip"] + 'and port ' + data["shard3port"]
		isConnected3 = 1
	except Exception, e:
		isConnected3 = 0
	
	if isConnected1 == 1 and isConnected2 == 1 and isConnected3 ==1:
		isConnectedall = 1
	
	
	msg_to_send = {'MessageType': 'BYTESTORED'}
	encoded_msg = json.dumps(msg_to_send)
	print encoded_msg
	#encoded_msg = base64.b64encode(encoded_msg)
	#sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#sock.connect(server_address)
	#sock.sendall(encoded_msg)
	
	print 'asking for currently used storage'
	while encoded_msg:
		if isConnected1 == 1:
			bytes = socket1.send(encoded_msg)
		if isConnected2 == 1:
			bytes = socket2.send(encoded_msg)
		if isConnected3 == 1:
			bytes = socket3.send(encoded_msg)
		encoded_msg = encoded_msg[bytes:]
	#sock.shutdown(socket.SHUT_WR)
	#sock.shutdown(socket.SHUT_WR)
	#print 'Waiting for Shard 1 to reply...'
	recv_data1 = ''
	recv_data2 = ''
	recv_data3 = ''
	if isConnected1 == 1:
		for buffer in recvmsg(socket1):
			recv_data1 = buffer
		json_obj1 = json.loads(recv_data1)
	if isConnected2 == 1:
		for buffer in recvmsg(socket2):
			recv_data2 = buffer
		json_obj2 = json.loads(recv_data2)
	if isConnected3 == 1:
		for buffer in recvmsg(socket3):
			recv_data3 = buffer
		json_obj3 = json.loads(recv_data3)
	#while True:
	#	read_data = sock.recv(1024)
	#	recv_data = recv_data + read_data
	#	print >>sys.stderr, 'received "%s"' % read_data
	#	if not read_data:
	#		break
	#sock.close()
	#decode = base64.b64decode(recv_data)
	
	if isConnectedall == 1:
		with open('monitor.csv','a') as file:
			file.write(json_obj1['BytesStored']+','+json_obj2['BytesStored']+','+json_obj3['BytesStored']+','+'\n')
		print 'reply was ' + json_obj1['BytesStored'] + 'bytes'
		print 'reply was ' + json_obj2['BytesStored'] + 'bytes'
		print 'reply was ' + json_obj3['BytesStored'] + 'bytes'

	elif isConnected1 == 1 and isConnected2 == 1:
		with open('monitor.csv','a') as file:
			file.write(json_obj1['BytesStored']+','+json_obj2['BytesStored']+','+'NA'+','+'\n')
		print 'reply was ' + json_obj1['BytesStored'] + 'bytes'
		print 'reply was ' + json_obj2['BytesStored'] + 'bytes'

	elif isConnected2 == 1 and isConnected3 == 1:
		with open('monitor.csv','a') as file:
			file.write('NA'+','+json_obj2['BytesStored']+','+json_obj3['BytesStored']+','+'\n')
		print 'reply was ' + json_obj2['BytesStored'] + 'bytes'
		print 'reply was ' + json_obj3['BytesStored'] + 'bytes'

	elif isConnected1 == 1 and isConnected3 == 1:
		with open('monitor.csv','a') as file:
			file.write(json_obj1['BytesStored']+','+'NA'+','+json_obj3['BytesStored']+','+'\n')
		print 'reply was ' + json_obj1['BytesStored'] + 'bytes'
		print 'reply was ' + json_obj3['BytesStored'] + 'bytes'
	
	
	
	


	if isConnected1 == 1:
		socket1.close()
	if isConnected2 == 1:
		socket2.close()
	if isConnected3 == 1:
		socket3.close()
	sleep(10)