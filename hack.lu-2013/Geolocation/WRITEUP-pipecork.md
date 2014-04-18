# Geolocation writeup
    Hack.Lu CTF, 2013
    Writeup by pipecork

In this challenge, teams are given a unique URL. A single point is gained for every different country that the URL is visited from, 222 possible points in total. Teams can gain some minor points with a little clever ingenuity, or by having a lot of international friends.

Because this challenge would yield, at most, around the same number of points that another challenge would, it wouldn't be wise to spend much time on it. I wrote a quick script to utilize tor's global network to run in the background:

    while true; do
      pidof tor | xargs kill -HUP  # get a new tor identity
      torify wget -qO- https://ctf.fluxfingers.net/ref/oSaBba5IScd8V2a --no-check-certificate | grep "successfully"
    done

After accessing the URL from a tor exit node, we request a new tor identity (along with a new exit node) to hopefully land in a country we haven't gotten yet. We only output on every new country (by grepping for "successfully") so we can run this in the background while working on other challenges.

Another approach I used was nodes at http://planet-lab.org with a similar wget script. However, most of the nodes I tried were in countries we already acquired through tor, so its yield wasn't much.

Interestingly enough, Antarctica proved very difficult to acquire. I had access to a Gentoo box in a physics research station near the south pole. However, because the research station was American, the IP address registered was as well. I'm curious how other teams acquired that country.
