# multiplication is hard writeup
    Plaid CTF, 2014
    Writeup by pipecork

I actually remember this joke from my first year of CS. If you put `38.55 * 1700` in a calculator you'll get 65535. But that isn't the flag.

Back in 2007 it was discovered that floating point multiplication operations in the latest version of Microsoft Excel that *should* result in 65535 actually resulted in 100000. A small bit of trivia for a quick answer! Joel Spolsky has a [great technical explanation](http://www.joelonsoftware.com/items/2007/09/26b.html) of the issue on his blog.

The flag is `100000`.

