# CTF writeups 
To add your writeups to the repo, drop them in `/srv/http/ctf/writeups` then 
git add, commit, and push 'em. Writeups can then be edited in GitHub's web
editor, or by committing changes from the repo. 

Contact a club lead or ask in IRC for help on uploading your writeups if you're 
new to all this.


## Formatting 
Each writeup should be either a markdown or flat text file, preferably wrapped 
to 80 character width. 

The first line is the document title, preceded by a single '#' and a space.
Line 2 is your authorship (real name or handle) with two hashes and a space.
Line 3 is an optional subtitle, preceded by 3 hashes and a space.  ''Please keep
your subtitle under 140 chars.''

Example: 
    # tux.smashthestack.org level3 writeup 
    ## mike_pizza 
    ### Recovering credentials in over-the-wire RSA encryption [censored]


## Censorship 
For writeups of CTF challenges from competitions, no censorship is needed. 
Just be sure to hold off on posting them until the competition is over.

Challenges part of ongoing campaigns that can be done at any time (ie,
SmashTheStack, HackThisSite!, etc) must be censored to prevent others from
cheating. Feel free to include notes on your thought process and explanations of
necessary concepts, but exclude any finished code you used to complete the chal.
Snippets and pseudocode for explanation are allowed, but be discretionary. These
are writeups, not walkthroughs.

However, we certainly encourage you to write uncensored writeups/walkthroughs
for internal use. It's also far easier to write censored writeups first, then
cut them down to uncensored versions. Any files in `/srv/http/ctf/writeups`
suffixed with `.uncensored` will not be synced to the public.

