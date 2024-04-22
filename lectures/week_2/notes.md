# Week 2: Web Exploitation

Nick Gregory - nmg355@nyu.edu


* Most web bugs stem from just a handful of issues
    * Not all identical bugs of course, but the core issue is typically one of just a few things
        * SQL injection (SQLi)
        * Cross-site scripting (XSS)
        * Cross-site request forgery (CSRF)
        * File inclusion
        * Command injection


* SQL - language to talk with databases
    * A human-readable language
    * Used _everywhere_ from hobby sites to Facebook
    * Different servers (MySQL, Oracle, Postgres, etc.) have slightly different dialects, but they're all the same for our purposes right now
    * 3 basic "tiers" for data
        1. database - usually defines the project the data is for
        2. table - a specific entity (e.g. users)
        3. columns - properties of the entity (e.g. name)
    * `SELECT id, name, password FROM users WHERE name LIKE 'nick%'`
        * Gets the ID, name, and password for each row in the `users` table where the user's name starts with "nick"
        * Capitalization of "SELECT", "FROM", "WHERE", etc. doesn't matter - just for readability
        * '%' is a wildcard, but you don't really need to know that right now
        * SELECTS can also just select constants
            * e.g. `SELECT 1,2` is completely valid
    * You can also have subqueries: `SELECT name FROM users WHERE id IN (SELECT id FROM banned)`
        * That specific example would be better coded with a `JOIN`, but SELECTs are more useful to us from an exploitation point of view
    * Arguments/parameters (like the 'nick%' above) can either be directly embedded in the query or parameterized
        * Parameterized queries are basically all you'll see in modern ORM-based code
        * Embedding directly in the query is still found today, but usually only in bad code
        * Often includes arguments directly from user input (e.g. search query)
    * If we have something like `SELECT * FROM users WHERE name = '$name'`, what could go wrong?
        * `$name="example's"`
        * `SELECT * FROM users WHERE name = 'example's`
    * The "s" is now outside of the string - syntax error
    * How could we make use of this?
        * Let's look at the following which may be used in a login page:
        * `SELECT * FROM users WHERE name = '$name' AND password = '$password'`
            * users is a table with 3 columns: id, name, password
        * How can we use this to log in as `$name = "admin"`?
        * `$password = "asdf' OR name = 'admin'";`
            * `SELECT * FROM users WHERE name = 'foo' AND password = 'asdf' OR name = 'admin'`
        * That's the basic idea of SQLi - "injecting" your own query into an existing SQL statement
    * How can we solve the problem?
        * Parameterization (preferred)
        * Escape the string!
            * Transform `'` into `\'` so that the SQL servers knows that the `'` is part of the string itself
            * `$name.replace("'", "\'")`?
            * Well... What if we had "\'" in the name...
                * The `\` gets escaped with the `\` that was supposed to escape the `'`
                * The result (`\\'`) makes the string itself contain a `\`, but the `'` is unescaped 
            * (For PHP): Enter `mysql_escape_string`
            * Problem solved, right?
            * Well languages (and therefore text encodings are hard)
                * `mysql_escape_string` can be bypassed if the DB uses an encoding other than UTF-8, ASCII, or ISO-8859
                * [Shift JIS](https://en.wikipedia.org/wiki/Shift_JIS) is amazing
            * ...
            * Enter `mysql_real_escape_string`
                * Takes into account DB encoding
                * Actually works when used (properly)
    * One other issue...
        * `SELECT * FROM users WHERE id = $id`
        * We don't even have escaping to bypass!
        * Obvious solution here is to parse $id as an int before passing it to SQL
            * But people miss this just like everything else
    * SQL also has a `UNION` operator which allows you to take the union of two queries
        * The only significant constraint is that the two SELECTs have to have the same number of columns
        * Example: `SELECT name FROM users UNION SELECT name from employees`
        * Never seen this used in the real world, but it's *amazing* for exploitation
        * Say the login page will tell you if the password is wrong
            * "Incorrect password for user $name!"
        * How can we combine this with the injection above?
        * `SELECT * FROM users WHERE name = '' UNION SELECT 1,2,3`
            * "Incorrect password for user 2!"
        * If the page returns data from the DB, we can use it to exfiltrate data out
        * `... UNION SELECT 1, DATABASE(), 3` will give us the name of the DB
        * How can we get the password for `admin`?
            * Just return the result of a subquery
            * `... UNION SELECT 1, (SELECT password FROM users WHERE name='admin'), 3`
            * "Incorrect password for user super_secret_password!"
    * Some random useful things to know:
        * `; -- ` will end the current query and start a comment
            * Makes the SQL server ignore everything after the "--"
            * So the last example could have also just been solved with `$name = "admin'; -- ";`
                * `SELECT * FROM users WHERE name = 'admin'; -- AND password = ...`
        * SQL has a _ton_ of built-in functions which can be useful for testing:
            * `SLEEP(n)`: sleeps the server for `n` seconds before returning the result
                * Super useful if you don't actually get any data back on the page directly from the query, but need to test if you have injection
                * We'll use this more extensively later
            * `VERSION()`: returns the version string of the SQL server
                * Useful for information gathering, but also just as a known good thing to return data




* HTTP - the core protocol
    * Human-readable format for getting content
    ```
    GET / HTTP/1.1
    Host: www.google.com


    ```
        * "GET" is the method
            * GET, POST are most common
        * "/" is the asset to get
        * "HTTP/1.1" is the version of the HTTP protocol (basically always 1.1)
        * "Host: www.google.com" tells the server which domain you're visiting
            * The same server can host multiple domains but have the same IP
        * Request is ended with two CRLF's
            * CRLF = carriage return, line feed: "\r\n"
    * Client and server both send headers
        * "Host" is a header in the above example
        * Headers are like request attributes
            * From the client, `Origin: ...` may tell the server what the "parent" URL is that requested this asset
            * From the server, `Server: ...` may tell the client what the name of the server software is
    * The client also maintains cookies which identify it to the server
        * They're what allows the server to track your login for example
        * As you may guess, a number of attacks are all about getting user cookies because cookies ~= authorization
    * GET requests are just the client sending headers requesting an object from the server
        * Can include parameters: `GET /square.php?num=3&foo=bar HTTP/1.1`
    * POST requests are the client sending headers and data to the server
        ```
        POST /upload.php HTTP/1.1
        Host: www.example.com
        Content-Type: text/plain
        Content-Length: 10


        asdfasdfas
        ```


* PHP - the worst, but most commonly used scripting language for web apps
    * /r/lolphp
    * "Note that the output will be different from the original mt19937ar.c, because PHP's implementation contains a bug. Thus, this test actually checks to make sure that PHP's behaviour is wrong, but consistently so." -ext/standard/tests/math/mt_rand_value.phpt, 2016
    * Let's just look at examples
    * `0 == "0"`
        * PHP will automatically try to type juggle variables in a `==`
        * The string `"0"` gets parsed into the int `0`
        * Resovled by using `===`
    * `"0e394759834" == "0e2346823420342"`
        * Again, type juggling the strings to ints (0e123 being 0^123)
        * Commonly seen in hash comparisons
        * Resolved with `===` again
    * `0 == "php"`
        * You see the pattern by now, but still deserving of a wat
    * `$a = "hello"; $$a = "foo"; echo $hello`
        * Never seen but WAT
        * And yes, this can be chained indefinitely
    * `unserialize($userinput)`
        * Not php specific, but commonly seen in CTFs because PHP is so common
        * `serialize`/`unserialize` take PHP objects and serialize them into a string (and vice-versa)
        * It does require some specific circumstances to be exploitable
        * Odds are very good that if you see either in a CTF challenge though, exploiting it is (at least part of) the solution
    * `include $_GET['path'] . ".php";`
        * Might be used to do templates
            * Have index.php have a static header and footer, and then just `include` the page the user wants
            * Sounds fine, right?
        * PHP has "filters" which are virtual URIs that can be opened and can manipulate files
            * `file_get_contents("php://filter/convert.base64-encode/resource=file.php");` will return the contents of `file.php` base64 encoded
                * Base64 is a super common encoding that you should be familiar enough to recognize when you see it
                * Allows you to encode arbitrary bytes into something that is ASCII printable
                * Uses `a-z`, `A-Z`, `0-9`, `+`, `/`, `=`
                * Ends with 0-2 `=`s
                * `SGVsbG8gV29ybGQh` is "Hello World!"
