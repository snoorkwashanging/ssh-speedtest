What this is
======
This script is for getting internet speedtest JSON data from an SSH server, parsing it, and printing the results.
For now, this will only work with passwords. I will figure out how to get keys to work later, but I don't care too much since it runs on a local network and not over the internet for my use.

Some requirements:
======
-A server with the Ookla [speedtest-cli package](https://www.speedtest.net/apps/cli)

-Paramiko(just run pip install in this folder)

-The host key for the server, as in you should've connected to the SSH server before

-More will be added here when I finish this stuff lol


How to Use:
======
***python speed.py hostname port username password***

So for my system it would be:

**python speed.py 192.168.0.1 22 root passwordthatisntactuallymypassword**

Things I need to do still:
======
TODO: get the result to HA and have it do what I want it to do(this will probably be done with it just reading the printed value)

TODO: add arg for whether the paramiko log should be turned on or not(bool)

TODO: set up that log so it will start with an if statement

TODO: figure out the SSH key stuff so you don't have to use a password

TODO: probably figure out a safer way to do passwords if a password is used

TODO: Add the thing where paramiko will add the host key

TODO: clean up this garbage more
