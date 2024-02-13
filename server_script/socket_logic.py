
import socket, cv2, struct
import pyshine as ps 
import cv2
from ultralytics import YOLO
import numpy as np
import hashlib

from server_script.login_script.db_engine import *

model = YOLO("../models/best.pt")

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 5000
socket_address = (host_ip,port)
server_socket.bind(socket_address)
server_socket.listen()
print("Listening at",socket_address)

HashTable = {}


def show_client(addr,client_socket):
	try:
		print('CLIENT {} CONNECTED!'.format(addr))
		if client_socket: # if a client socket exists
			client_socket.send(str.encode('ENTER USERNAME : ')) # Request Username
			name = client_socket.recv(2048)
			client_socket.send(str.encode('ENTER PASSWORD : ')) # Request Password
			password = client_socket.recv(2048)
			password = password.decode()
			username = name.decode()			

			password = hashlib.sha256(str.encode(password)).hexdigest() #hash password withs sha256

			# if name not in HashTable:
			# 	HashTable[name] = password
			# 	client_socket.send(str.encode('REGISTERED SUCCESSFULLY!'))
			# 	print('Registered : ',name)
			# 	print("{:<8} {:<20}".format('USER','PASSWORD'))
			# 	for k, v in HashTable.items():
			# 		label, num = k,v
			# 		print("{:<8} {:<20}".format(label, num))
			# 		print("-------------------------------------------")
			# else:
			# 	if(HashTable[name] == password):
			# 		client_socket.send(str.encode('Connection Successful')) # Response Code for Connected Client 
			# 		print('Connected : ',name)
			# 	else:
			# 		client_socket.send(str.encode('Login Failed')) # Response code for login failed
			# 		print('Connection denied : ',name)
			# 		client_socket.close()
			# 		return


			# check username and password
			if not user_exist(username):
				register(username,password)
			else:
				if login(username,password):
					client_socket.send(str.encode('Connection Successful')) # Response Code for Connected Client 
					print('Connected : ',username)
				else:
					client_socket.send(str.encode('Login Failed')) # Response code for login failed
					print('Connection denied : ',name)
					client_socket.close()
					return
				
			data = b""
			payload_size = struct.calcsize("Q")
			while True:
				# receive data until message size is reached
				data,msg_size = receive_data(data,client_socket,payload_size)

				# extract raw_frame from data
				frame_data = data[:msg_size]
				data  = data[msg_size:]
				
				# decode data into frame
				frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), -1) # more efficient
				# inference
				frame = inference_and_draw(frame,addr)				
				
				# show frame
				cv2.imshow(f"FROM {addr}",frame)
				key = cv2.waitKey(1) & 0xFF
				if key  == ord('q'):
					break
			client_socket.close()

	except Exception as e:
		print(f"CLINET {addr} DISCONNECTED")
		pass


# receiver
def receive_data(data,client_socket,payload_size):
	while len(data) < payload_size:
		packet = client_socket.recv(4*1024) # 4K
		if not packet: break
		data+=packet
	packed_msg_size = data[:payload_size]
	data = data[payload_size:]
	msg_size = struct.unpack("Q",packed_msg_size)[0]

	while len(data) < msg_size:
		data += client_socket.recv(4*1024)
	return data,msg_size

# inference and draw
def inference_and_draw(frame,addr):
	text  =  f"CLIENT: {addr}"
	result = model(frame, conf=0.85, verbose=False)
	fall_box = result[0].boxes.cpu().numpy().xyxy
	if fall_box.size > 0:
		fall_box = fall_box[0]
		frame = cv2.rectangle(frame, 
			   (int(fall_box[0]),
				int(fall_box[1])),
				(int(fall_box[2]),
				 int(fall_box[3])),
				 (0, 0, 255), 2)
	frame =  ps.putBText(frame,text,10,10,vspace=10,hspace=1,font_scale=0.7,
			 			background_RGB=(255,0,0),text_RGB=(255,250,250))
	return frame
	
