
import socket, cv2, struct
import pyshine as ps 
from ultralytics import YOLO
import numpy as np

from server_script.login_script.db_engine import *
from server_script.send_notification import send_notification
from server_script.detect import FallDetector

import time

from flask import send_file
from io import BytesIO

import threading

from flask import Flask, render_template, Response,redirect,url_for, request,make_response
from flask_login import LoginManager

from queue import Queue




app = Flask(__name__)

model = YOLO("../models/best.pt")

# create a socket object for video ingest server
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 5000
socket_address = (host_ip,port)
server_socket.bind(socket_address)
server_socket.listen()
print("Listening (Video Ingest Server) at",socket_address)

# create a socket object for sending frames to flask

queues = {}
client_sockets = {}
cam_user = {}

fall = False

@app.route('/')
def index():
	global queues
	return render_template('index.html')

# check login status
# return True if user is logged in
def check_login_status():
	username = request.cookies.get('username')
	if not username or not user_exist(username):
		return False,username
	return True,username



@app.route('/main')
def Main():
	global cam_user
	status,username =check_login_status()
	if  status == False:
		return redirect('/login')
	if username in cam_user:
		cameras = cam_user[username]
	else:
		cameras = []
	if check_contact(username) == False:
		alert = 'Please add your email on profile page to receive notification'
		return render_template('main.html',alert = alert)
	return render_template('main.html',cameras=cameras,username=username)

@app.route('/logout',methods=['POST'])
def logout():
	resp = make_response(redirect(url_for('auth.login')))
	resp.set_cookie('username', '', expires=0)
	return resp

def generate_frames(addr):
	global frames, frames_lock
	global queues
	while True:

		frame_data = queues[addr].get()
		if frame_data is not None:
			yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

@app.route('/video_feed/<addr>')
def video_feed(addr):
	status, username = check_login_status()
	print('STATUS : ',status)
	print('USERNAME : ',username)
	addr = int(addr)
	if  status == False:
		return redirect('/main')
	if addr not in queues.keys():
		return 'CAMERA NOT FOUND'
	if cam_user[username].count(addr) == 0:
		return 'ACCESS DENIED'
	return Response(generate_frames(addr), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/profile')
def profile():
	status,username = check_login_status()
	if status == False:
		return redirect('/login')
	return render_template('profile.html',username=username)

#shutdown camera with this address
@app.route('/shutdown',methods=['POST'])
def shutdown():
    addr = int(request.form.get('cam_id'))
    status, username = check_login_status()
    if status == False:
        return redirect('/login')
    if cam_user[username].count(addr) == 0:
        return 'ACCESS DENIED'
    if addr in client_sockets:
        client_sockets[addr].close()
        del client_sockets[addr]
    return redirect(url_for('Main'))

def flask_server():
	from.auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)
	from .contact_route import contact as contact_blueprint
	app.register_blueprint(contact_blueprint)
	app.secret_key = 'augghhhhh'
	
	app.run(threaded=True,host='0.0.0.0')

def show_client(addr,client_socket):
	global frames
	try:
		print('CLIENT {} CONNECTED!'.format(addr[1]))
		if client_socket: # if a client socket exists
			client_socket.send(str.encode('ENTER USERNAME : ')) # Request Username
			name = client_socket.recv(2048)
			client_socket.send(str.encode('ENTER PASSWORD : ')) # Request Password
			password = client_socket.recv(2048)
			password = password.decode()
			username = name.decode()			

			password = hash_password(password) #hash password withs sha256


			# check username and password
			if not user_exist(username):
				client_socket.send(str.encode('Username doesn\'t exist, please sign up first!'))
				print('Connection denied : ',name)
				client_socket.close()
				return
			else:
				if login_db(username,password):
					# Response Code for Connected Client 
					client_socket.send(str.encode('Connection Successful'+'\nid: ' + str(addr[1]))) 
					print('Connected : ',username + '\nid: ' + str(addr[1]))
					if username not in cam_user:
						cam_user[username] = []
					cam_user[username].append(addr[1])
					client_sockets[addr[1]] = client_socket
				else:
					client_socket.send(str.encode('Login Failed')) # Response code for login failed
					print('Connection denied : ',name)
					client_socket.close()
					return
			
			print(cam_user)
			# start receiving video from client
			data = b""
			payload_size = struct.calcsize("Q")

			global fall
			global queues


			queues[addr[1]] = Queue()
			# start fall detection
			# if email is available
			fall_detector = FallDetector(addr[1],check_contact(username),username)
			if check_contact(username) != False:
				fall_detector.start()

			# start receiving video from client
			while True:
				# receive data until message size is reached
				data,msg_size = receive_data(data,client_socket,payload_size)

				# extract raw_frame from data
				frame_data = data[:msg_size]
				data  = data[msg_size:]
				
				# decode data into frame
				frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), -1) # more efficient
				# inference
				frame,fall = inference_and_draw(frame,addr)	

				queues[addr[1]].put(cv2.imencode('.jpeg', frame)[1].tobytes())


				# fall detection
				fall_detector.update_fall_state(fall)

				# show frame
 
				key = cv2.waitKey(1) & 0xFF
				if key  == ord('q'):
					break
			client_socket.close()

	except Exception as e:
		print(f"CLIENT {addr[1]} DISCONNECTED")
		queues[addr[1]].put(None)
		del queues[addr[1]]

		if addr[1] in cam_user[username]:
			cam_user[username].remove(addr[1])
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
	# frame =  ps.putBText(frame,text,10,10,vspace=10,hspace=1,font_scale=0.7,
	# 		 			background_RGB=(255,0,0),text_RGB=(255,250,250))
	
	if fall_box.size > 0:
		fall_detected = True
	else:
		fall_detected = False

	return frame,fall_detected
