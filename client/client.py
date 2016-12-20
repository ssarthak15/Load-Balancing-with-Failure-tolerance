import socket
import sys
import os
import json
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

if len(sys.argv) < 4:
	print 'the program needs 3 or 4 arguments'
	exit()

isDownloading = 0
isUploading = 0
isConnected1 = 0
isConnected2 = 0
isConnected3 = 0
isConnectedall = 0
upDownFile = ''

param_1 = sys.argv[1] 
param_2 = sys.argv[2] 
param_3 = sys.argv[3]
if len(sys.argv) == 5:
	param_4 = sys.argv[4]

if param_1 == '-config':
	with open(param_2) as con_file:
		data = json.load(con_file)

if param_3 == '-config':
	with open(param_4) as con_file:
		data = json.load(con_file)

if param_1 == '-upload' or param_3 == '-upload':
	if param_1 == '-upload':
		upDownFile = param_2
	else:
		upDownFile = param_4
	isUploading = 1

if param_1 == '-download' or param_3 == '-download':
	if param_1 == '-download':
		upDownFile = param_2
	else:
		upDownFile = param_4
	isDownloading = 1




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

sock1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock3=socket.socket(socket.AF_INET,socket.SOCK_STREAM)


# Connect the sockets to the ports where the server is listening
try:
	sock1.connect(server_address1)
	print 'connected to shard 1 at ip ' + data["shard1ip"] + 'and port ' + data["shard1port"]
	isConnected1 = 1
except Exception, e:
	isConnected1 = 0
try:
	sock2.connect(server_address2)
	print 'connected to shard 2 at ip ' + data["shard2ip"] + 'and port ' + data["shard2port"]
	isConnected2 = 1
except Exception, e:
	isConnected2 = 0
try:
	sock3.connect(server_address3)
	print 'connected to shard 3 at ip ' + data["shard3ip"] + 'and port ' + data["shard3port"]
	isConnected3 = 1
except Exception, e:
	isConnected3 = 0

if isConnected1 == 1 and isConnected2 == 1 and isConnected3 ==1:
	isConnectedall = 1

if isUploading == 1:
	msg_to_send = {'MessageType': 'BYTESTORED'}
	encoded_msg = json.dumps(msg_to_send)
	print encoded_msg
	#encoded_msg = base64.b64encode(encoded_msg)
	#sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#sock.connect(server_address)
	#sock.sendall(encoded_msg)

	print 'asking for currently used storage'
	while encoded_msg:
		bytes = sock1.send(encoded_msg)
		bytes = sock2.send(encoded_msg)
		bytes = sock3.send(encoded_msg)
		encoded_msg = encoded_msg[bytes:]
	#sock.shutdown(socket.SHUT_WR)
	#sock.shutdown(socket.SHUT_WR)
	#print 'Waiting for Shard 1 to reply...'
	recv_data1 = ''
	recv_data2 = ''
	recv_data3 = ''
	for buffer in recvmsg(sock1):
		recv_data1 = buffer
	for buffer in recvmsg(sock2):
		recv_data2 = buffer
	for buffer in recvmsg(sock3):
		recv_data3 = buffer
	#while True:
	#	read_data = sock.recv(1024)
	#	recv_data = recv_data + read_data
	#	print >>sys.stderr, 'received "%s"' % read_data
	#	if not read_data:
	#		break
	#sock.close()
	#decode = base64.b64decode(recv_data)
	json_obj1 = json.loads(recv_data1)
	json_obj2 = json.loads(recv_data2)
	json_obj3 = json.loads(recv_data3)
	print 'reply was ' + json_obj1['BytesStored'] + 'bytes'
	print 'reply was ' + json_obj2['BytesStored'] + 'bytes'
	print 'reply was ' + json_obj3['BytesStored'] + 'bytes'
    # here we will have to check BYTEStored when we split for final deliverable project
	f = open(upDownFile,'r+')
	#find size of my file
	size = getFileSize(upDownFile)

	#adding the bytes of all shards and upload size
	total = int(json_obj1['BytesStored']) + int(json_obj2['BytesStored']) + int(json_obj3['BytesStored']) + int(size)
	total = total/3

	to_shard1 = 2
	to_shard2 = 2
	to_shard3 = 2
	size = size - 6

	shard_bytes1 = int(json_obj1['BytesStored']);
	shard_bytes2 = int(json_obj2['BytesStored']) 
	shard_bytes3 = int(json_obj3['BytesStored'])

	while size > 0:
		if shard_bytes1 < shard_bytes2 and shard_bytes1 < shard_bytes3:
			to_shard1+=1
			shard_bytes1+=1
		elif shard_bytes2 < shard_bytes1 and shard_bytes2 < shard_bytes3:
			to_shard2+=1
			shard_bytes2+=1
		elif shard_bytes3 < shard_bytes2 and shard_bytes3 < shard_bytes1:
			to_shard3+=1
			shard_bytes3+=1
		elif shard_bytes1 == shard_bytes2 and shard_bytes1 < shard_bytes3:
			to_shard1+=1
			shard_bytes1+=1
		elif shard_bytes2 == shard_bytes3 and shard_bytes2 < shard_bytes1:
			to_shard2+=1
			shard_bytes2 +=1
		elif shard_bytes3 == shard_bytes1 and shard_bytes3 < shard_bytes2:
			to_shard3+=1
			shard_bytes3 +=1
		elif shard_bytes1 == shard_bytes2 and shard_bytes2 == shard_bytes3:
			to_shard3 +=1 
			shard_bytes3 +=1
		size-=1

	print to_shard1
	print to_shard2
	print to_shard3

	msg_to_send1 = {'MessageType': 'DATA', 'Filename': str(upDownFile), 'BytesFrom': '0', 'BytesTo': str(to_shard1 - 1), 'Data': base64.b64encode(str(f.read(to_shard1)))}
	msg_to_send2 = {'MessageType': 'DATA', 'Filename': str(upDownFile), 'BytesFrom': str(to_shard1), 'BytesTo': str(to_shard1 + to_shard2 - 1), 'Data': base64.b64encode(str(f.read(to_shard2)))}
	msg_to_send3 = {'MessageType': 'DATA', 'Filename': str(upDownFile), 'BytesFrom': str(to_shard1 + to_shard2), 'BytesTo': str(to_shard1 + to_shard2 + to_shard3 - 1), 'Data': base64.b64encode(str(f.read(to_shard3)))}
	encoded_msg1 = json.dumps(msg_to_send1)
	encoded_msg2 = json.dumps(msg_to_send2)
	encoded_msg3 = json.dumps(msg_to_send3)
	#encoded_msg= base64.b64encode(encoded_msg)
	#sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#sock.connect(server_address)
	#sock.sendall(encoded_msg)
	print 'uploading file'
	while encoded_msg1:
		bytes = sock1.send(encoded_msg1)
		encoded_msg1 = encoded_msg1[bytes:]
	while encoded_msg2:
		bytes = sock2.send(encoded_msg2)
		encoded_msg2 = encoded_msg2[bytes:]
	while encoded_msg3:
		bytes = sock3.send(encoded_msg3)
		encoded_msg3 = encoded_msg3[bytes:]
	#sock.shutdown(socket.SHUT_WR)
	#sock.shutdown(socket.SHUT_WR)
	#print 'Waiting for Shard 1 to reply...'
	# Receive the data in small chunks and retransmit it
	for buffer in recvmsg(sock1):
		recv_data1 = buffer
	for buffer in recvmsg(sock2):
		recv_data2 = buffer
	for buffer in recvmsg(sock3):
		recv_data3 = buffer
	#while True:
	#	read_data = sock.recv(1024)
	#	global recv_data
	#	recv_data = recv_data + read_data
	#	print >>sys.stderr, 'received "%s"' % read_data
	#	if not read_data:
	#		break
	#sock.close()
	#decode = base64.b64decode(recv_data)
	json_obj1 = json.loads(recv_data1)
	print json_obj1['Content']
	json_obj2 = json.loads(recv_data2)
	print json_obj2['Content']
	json_obj3 = json.loads(recv_data3)
	print json_obj3['Content']
elif isDownloading == 1:
	msg_to_send = {'MessageType': 'FILEINFO', 'Filename': str(upDownFile)}
	encoded_msg = json.dumps(msg_to_send)
	#encoded_msg= base64.b64encode(encoded_msg)
	#sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#sock.connect(server_address)
	#sock.sendall(encoded_msg)
	print 'asking if shard 1 has the file'
	while encoded_msg:
		if isConnected1 == 1:
			bytes = sock1.send(encoded_msg)
		if isConnected2 == 1:
			bytes = sock2.send(encoded_msg)
		if isConnected3 == 1:
			bytes = sock3.send(encoded_msg)
		encoded_msg = encoded_msg[bytes:]
	#sock.shutdown(socket.SHUT_WR)
	#print 'Waiting for Shard 1 to reply...'
	recv_data1 = ''
	recv_data2 = ''
	recv_data3 = ''
	# Receive the data in small chunks and retransmit it
	if isConnected1 == 1:
		for buffer in recvmsg(sock1):
			recv_data1 = buffer
		json_objf1 = json.loads(recv_data1)
		print 'File is present from ' + json_objf1['BytesFrom'] + ' to ' + json_objf1['BytesTo']

	if isConnected2 == 1:
		for buffer in recvmsg(sock2):
			recv_data2 = buffer
		json_objf2 = json.loads(recv_data2)
		print 'File is present from ' + json_objf2['BytesFrom'] + ' to ' + json_objf2['BytesTo']

	if isConnected3 == 1:
		for buffer in recvmsg(sock3):
			recv_data3 = buffer
		json_objf3 = json.loads(recv_data3)
		print 'File is present from ' + json_objf3['BytesFrom'] + ' to ' + json_objf3['BytesTo']

	#print recv_data
	#while True:
	#	read_data = sock.recv(1024)
	#	print read_data
	#	global recv_data
	#	recv_data = recv_data + read_data
	#	if not read_data:
	#		break
	#sock.close()
	#decode = base64.b64decode(recv_data)
	#json_obj = json.loads(recv_data)
	#encoded_msg= base64.b64encode(encoded_msg)
	#sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#sock.connect(server_address)
	#sock.sendall(encoded_msg)
	if isConnected1 == 1:
		msg_to_send1 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf1['BytesFrom'], 'BytesTo': json_objf1['BytesTo']}
		encoded_msg1 = json.dumps(msg_to_send1)
		while encoded_msg1:
			bytes = sock1.send(encoded_msg1)
			encoded_msg1 = encoded_msg1[bytes:]

	if isConnected2 == 1:
		msg_to_send2 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf2['BytesFrom'], 'BytesTo': json_objf2['BytesTo']}
		encoded_msg2 = json.dumps(msg_to_send2)
		while encoded_msg2:
			bytes = sock2.send(encoded_msg2)
			encoded_msg2 = encoded_msg2[bytes:]

	if isConnected3 == 1:
		msg_to_send3 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf3['BytesFrom'], 'BytesTo': json_objf3['BytesTo']}
		encoded_msg3 = json.dumps(msg_to_send3)
		while encoded_msg3:
			bytes = sock3.send(encoded_msg3)
			encoded_msg3 = encoded_msg3[bytes:]
	#sock.shutdown(socket.SHUT_WR)
	#print 'Waiting for Shard 1 to reply...'

	if isConnected1 == 1:
		print 'Downloading primary from shard 1'
		recv_data1 = ''
		for buffer in recvmsg(sock1):
			recv_data1 = buffer
		json_obj1 = json.loads(recv_data1)

	if isConnected2 == 1:
		print 'Downloading primary from shard 2'
		recv_data2 = ''
		for buffer in recvmsg(sock2):
			recv_data2 = buffer
		json_obj2 = json.loads(recv_data2)

	if isConnected3 == 1:
		print 'Downloading primary from shard 3'
		recv_data3 = ''
		for buffer in recvmsg(sock3):
			recv_data3 = buffer
		json_obj3 = json.loads(recv_data3)

	#while True:
	#	read_data = sock.recv(1024)
	#	recv_data = recv_data + read_data
	#	if not read_data:
	#		break
	#sock.close()
	#decode = base64.b64decode(recv_data)
	#print decode
	#json_obj = json.loads(recv_data)
	#print json_obj

	#print json_obj1
	#print json_obj2

	if isConnectedall == 1:
		if json_obj1['MessageType'] == 'DATA' and json_obj2['MessageType'] == 'DATA' and json_obj3['MessageType'] == 'DATA':
			f = open(json_obj1['Filename'],'w+')
			f.write(base64.b64decode(json_obj1['Data']))
			f.write(base64.b64decode(json_obj2['Data']))
			f.write(base64.b64decode(json_obj3['Data']))
			f.close()
			print 'downloaded the file ' + json_obj1['Filename']
	elif isConnected1 == 1 and isConnected2 == 1:
		msg_to_send1 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf1['BytesFrom3'], 'BytesTo': json_objf1['BytesTo3']}
		encoded_msg1 = json.dumps(msg_to_send1)
		print encoded_msg1
		while encoded_msg1:
			bytes = sock1.send(encoded_msg1)
			print bytes
			encoded_msg1 = encoded_msg1[bytes:]


		msg_to_send2 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf2['BytesFrom3'], 'BytesTo': json_objf2['BytesTo3']}
		encoded_msg2 = json.dumps(msg_to_send2)
		while encoded_msg2:
			bytes = sock2.send(encoded_msg2)
			encoded_msg2 = encoded_msg2[bytes:]

		print 'Downloading backup data from shard 1'
		recv_data1 = ''
		for buffer in recvmsg(sock1):
			recv_data1 = buffer

		#print recv_data1
		#print 'recvdataend'
		jsonbk_obj1 = json.loads(recv_data1)

		print 'Downloading backup from shard 2'
		recv_data2 = ''
		for buffer in recvmsg(sock2):
			recv_data2 = buffer
		#print recv_data2
		#print 'recvdataend'
		jsonbk_obj2 = json.loads(recv_data2)
		f = open(json_obj1['Filename'],'w+')
		f.write(base64.b64decode(json_obj1['Data']))
		f.write(base64.b64decode(json_obj2['Data']))
		f.write(base64.b64decode(jsonbk_obj1['Data']))
		f.write(base64.b64decode(jsonbk_obj2['Data']))
		
		f.close()

	elif isConnected2 == 1 and isConnected3 == 1:
		msg_to_send2 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf2['BytesFrom2'], 'BytesTo': json_objf2['BytesTo2']}
		msg_to_send3 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf3['BytesFrom3'], 'BytesTo': json_objf3['BytesTo3']}
		encoded_msg2 = json.dumps(msg_to_send2)
		encoded_msg3 = json.dumps(msg_to_send3)

		while encoded_msg2:
			bytes = sock2.send(encoded_msg2)
			encoded_msg2 = encoded_msg2[bytes:]

		while encoded_msg3:
			bytes = sock3.send(encoded_msg3)
			encoded_msg3 = encoded_msg3[bytes:]

		print 'Downloading backup from shard 2'
		recv_data2 = ''
		for buffer in recvmsg(sock2):
			recv_data2 = buffer
		jsonbk_obj2 = json.loads(recv_data2)
		print jsonbk_obj2
		print 'Downloading backup data from shard 3'
		recv_data3 = ''
		for buffer in recvmsg(sock3):
			recv_data3 = buffer
		jsonbk_obj3 = json.loads(recv_data3)
		print jsonbk_obj3
		f = open(json_obj3['Filename'],'w+')
		f.write(base64.b64decode(jsonbk_obj2['Data']))
		f.write(base64.b64decode(jsonbk_obj3['Data']))
		f.write(base64.b64decode(json_obj2['Data']))
		f.write(base64.b64decode(json_obj3['Data']))
		f.close()

	elif isConnected3 == 1 and isConnected1 == 1:
		print 'lalalala'
		msg_to_send3 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf3['BytesFrom2'], 'BytesTo': json_objf3['BytesTo2']}
		msg_to_send1 = {'MessageType': 'REQUESTDATA', 'Filename': str(upDownFile), 'BytesFrom': json_objf1['BytesFrom2'], 'BytesTo': json_objf1['BytesTo2']}		
		encoded_msg3 = json.dumps(msg_to_send3)
		encoded_msg1 = json.dumps(msg_to_send1)

		while encoded_msg3:
			bytes = sock3.send(encoded_msg3)
			encoded_msg3 = encoded_msg3[bytes:]

		while encoded_msg1:
			bytes = sock1.send(encoded_msg1)
			encoded_msg1 = encoded_msg1[bytes:]

		print 'Downloading backup data from shard 3'
		recv_data3 = ''
		for buffer in recvmsg(sock3):
			recv_data3 = buffer
		jsonbk_obj3 = json.loads(recv_data3)

		print 'Downloading backup from shard 1'
		recv_data1 = ''
		for buffer in recvmsg(sock1):
			recv_data1 = buffer
		jsonbk_obj1 = json.loads(recv_data1)


		f = open(json_obj1['Filename'],'w+')
		f.write(base64.b64decode(json_obj1['Data']))
		f.write(base64.b64decode(jsonbk_obj3['Data']))
		f.write(base64.b64decode(jsonbk_obj1['Data']))
		f.write(base64.b64decode(json_obj3['Data']))
		f.close()
elif param_3 == '-eraseall':
	msg_to_send = {'MessageType': 'EraseAll'}
	encoded_msg = json.dumps(msg_to_send)
	print encoded_msg
	print 'asking to erase entire storage'
	while encoded_msg:
		bytes = sock1.send(encoded_msg)
		bytes = sock2.send(encoded_msg)
		bytes = sock3.send(encoded_msg)
		encoded_msg = encoded_msg[bytes:]
	recv_data1 = ''
	recv_data2 = ''
	recv_data3 = ''
	for buffer in recvmsg(sock1):
		recv_data1 = buffer
	for buffer in recvmsg(sock2):
		recv_data2 = buffer
	for buffer in recvmsg(sock3):
		recv_data3 = buffer
	json_obj1 = json.loads(recv_data1)
	json_obj2 = json.loads(recv_data2)
	json_obj3 = json.loads(recv_data3)
	print 'reply was: ' + json_obj1['Message']
	print 'reply was: ' + json_obj2['Message']
	print 'reply was: ' + json_obj3['Message']