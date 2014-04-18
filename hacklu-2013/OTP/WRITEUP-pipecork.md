# OTP writeup
    Hack.Lu CTF, 2013
    Writeup by pipecork

> Some robots are on the Oktoberfest and want to take some tasty oil in a tent. But they hadn't reserved a table and all tents are full. No one gets access. They found a back entrance and managed to spy the credentials while an employee enters. They captured the username "admin" and password "supersafepw". But the employee also entered a strange number (168335). As they were sure nobody's looking, they tried the captured data to get in the tent, but it didn't work. Help the robots to get their tasty tasty oil. https://ctf.fluxfingers.net:1318

Following the link gives us a plain login. Using the admin user:pass and the 6
number code doesn't give us access. Can't be that easy.

There's a register button. I register the username "max" with the password
"wat", and get a Google Authenticator QR code to scan. Google Authenticator TOTP
(Time-based One-time Password Algorithm) use a secret value and the time to give
a code that changes every 30 seconds for use in two-factor authentication.

I'm able to use my GA code and user:pass to login, but we want admin's
Authenticator code. Scanning the original QR code shows my secret value:

    otpauth://totp/OTP-Chal:max?secret=AAPLAL443GGQQFQTDERKVD6J4GKS57SM

After reading up a bit on how TOTPs are generated, I learn that Google prefers
the secret to be encoded in base32. It doesn't translate to anything meaningful
in ASCII. Decoding to base16 reveals:

    DD8E0C8950E22CAC2F8F14A5853220430B93C534

Running our base16 value through hash-identifier
(https://code.google.com/p/hash-identifier/) says that it's likely a SHA-1 hash
(additionally, the original base32 is identified as an MD5, but it's likely just
a coincidence). 

This is where I hit the road-block. There's no way I could know a timestamp for
its generation, and just feeding my user:pass into SHA-1 doesn't yield anything
fruitful. I didn't think they'd expect me to brute-force it; only after the
competition ended did I realize they DID. So, I did.

    hashcat --hash-type=100 --attack-mode=3 -o recovered.txt otp-b16.hash ?a?a?a?a?a?a?a?a?a

I broke out hashcat, my personal favorite hash cracking tool. The above command
says to use a brute-force SHA-1 attack on the base16 hash, with a mask of every
combination of ASCII of 9 characters (the original attack of 8 characters
yielded nothing). This took just over 30 minutes to reveal:

    DD8E0C8950E22CAC2F8F14A5853220430B93C534:prng11631

So my personal secret was derived from prng11631. Assuming the numeric value is
generated sequentially, I artificially generate the TOTP codes for 'prng1',
'prng01', 'prng001', 'prng0001', and 'prng00001'.

Using the TOTP code from prng0001 in conjunction with their login details gets
us in.

