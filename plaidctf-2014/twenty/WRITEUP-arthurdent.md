#### Crypto 20

Provided text:

<div style="word-wrap:break-word;">
FVOXOXFVWDEPAGXMWXFPUKLEOFXHWEVEFUYGZEPFVEXWFVUFGEYFRYEDOJHWFFOYHXCWGMLXEYLAWFXFURWFVOXECFEZFVWBECPFPEEJUYGOYFEFVWXFPWWFXOJUMWUXFUFFVWAWUXFLECAAZUBWJWOYFVWYEPFVWUXFHWFJLOPWCKAOHVFJLZOPWOAAHEVUPGWPFVUYWJOYWJDWYFUFJUPOUVBUAAJWUAOUPKECYGJWOYFVWUXXDOFVYEACMWBVUZOYHLECPWZCBROYHDOFVFVWGCGWDVEHEFFVWRWLXFELECPXUZWUYGFVEXWFVUFBUYFGEMPOYHXCOFXBPLFELECPCYBAWXUJFEXWFFAWGOXKCFWXFVECHVFLECGFUBRAWFVOXDOFVUAOFFAWJEPWFUBFMCFFVWYUHUOYZCGHWKUBRWPXOGEYFRYEDIUBROXVWGUFWUPWSWPLFOJWOFVOYREZAORXUYHMCFXVOFJUYFVWLPWUBEPKEPUFOEYUYGOJUKWPXEYOZOBUFOEYEZZPWWGEJZEPUAALECZOAAGEBRWFXAORWFVUFXUBEYBWKFZEPWOHYFELUAADVOAWAUDLWPXJCGGLDUFWPUYGFPEXXFUAAECFEZMCXOYWXXOXIUOAZEPJWUYGLECPWXCOYHJWBOSOAALWNVOMOFFVOXOYFVWBECPFPEEJHEEYGEOFOGUPWLECBEYHPUFCAUFOEYXFVWZAUHOXXOYBWYWDBPLKFEJOHVFVUSWYXUMUBRGEEPXOCXWEAGBPLKFE
</div>

This has a high probability of being a Caesar Cipher due to the number of repeating letter-pairs, and general letter frequency. One letter pairing that appears a lot together is `FV`, so `FV` is assumed to be the most common english letter pairing `th`. `OX` appears twice near the beginning. Making `O=i`, `X=s`  the beginning "this is th". From this point we can make the assumption that `W` is `e`. This guess and check process is repeated until the cipher is solved.

The flag is revealed at the very end of the string.

`theflagissincenewcryptomighthavensabackdoorsiuseoldcrypto`

I used [this slightly goofy looking flash application](http://cryptoclub.org/tools/cracksub_topframe.php ) to view letter frequency and substitute letters efficiently.
