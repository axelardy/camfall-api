
import socket,cv2,struct
import imutils 
import time
import argparse
import getpass
import device



def run_connection(camera=True, host_ip=socket.gethostbyname(socket.gethostname()), port=5000):

	try:
		if camera == True:
			# print device list
			device_list = device.getDeviceList()
			index = 0
			for cam in device_list:
				print(str(index)+' : '+cam[0])
				index += 1
			# select camera
			camera_index = input('select camera :')
			vid = cv2.VideoCapture(int(camera_index))

		else:
			vid = cv2.VideoCapture('test.mp4')
		client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		client_socket.connect((host_ip,port))

		# client_socket.send('username'.encode())
		# client_socket.send('password'.encode())

		if client_socket:

			response = client_socket.recv(2048)

			login_id = input(response.decode())
			client_socket.send(login_id.encode())

			response = client_socket.recv(2048)
			password = getpass.getpass(response.decode())
			client_socket.send(str.encode(password))

			response = client_socket.recv(2048)
			response = response.decode()
			print(response)

			start_time = time.time()
			total_bytes_sent = 0
			last_print_time = start_time

			while (vid.isOpened()):
				try:
					img, frame = vid.read()
					frame = imutils.resize(frame,width=360)

					# more efficient solution
					result, buffer = cv2.imencode('.jpg', frame)
					buffer = buffer.tobytes()
					message = struct.pack("Q",len(buffer))+buffer


					client_socket.sendall(message)
					total_bytes_sent += len(message)

					cv2.imshow(f"TO: {host_ip}",frame)
					key = cv2.waitKey(1) & 0xFF
					if key == ord("q"):
						client_socket.close()

					current_time = time.time()
					if current_time - last_print_time >= 1:
						total_time_elapsed = current_time - start_time
						average_bytes_per_second = total_bytes_sent / total_time_elapsed
						print(f"\rAverage bytes sent per second: {average_bytes_per_second*8/1000000} mbps", end='')
						last_print_time = current_time
				except:
					print('VIDEO FINISHED!')
					break
	except Exception as e:
		print('EXCEPTION:',e)
	finally:
		vid.release()
		cv2.destroyAllWindows()
		client_socket.close()
		print("CLIENT DISCONNECTED")



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--camera', type=bool, default=True)
	parser.add_argument('--host_ip', type=str, default=socket.gethostbyname(socket.gethostname()))
	parser.add_argument('--port', type=int, default=5000)
	args = parser.parse_args()


	run_connection(camera=args.camera, host_ip=args.host_ip, port=args.port)