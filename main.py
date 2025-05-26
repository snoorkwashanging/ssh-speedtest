#thingy for getting a speedtest json from a local unifi controller, parsing it, and sending it to
#a home assistant instance
# this shit will only work with passwords for now, I will figure out keys later, but I don't care too much since it
#runs on a local network and not over the internet
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# How to use:
# python main.py hostname port username password
#
# So for my system it would be:
# python main.py 192.168.0.1 22 root passwordthatisntactuallymypassword
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#things I need to do still:
#TODO: add arg for whether the paramiko log should be turned on or not(bool)
#TODO: set up that log so it will start with an if statement
#TODO: figure out the ssh key stuff so you dont have to use a password
#TODO: probably figure out a safer way to do passwords if a password is used
#TODO: Add the thing where paramiko will just add the host key
#TODO: clean up this garbage more
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
import sys
import traceback
import paramiko.util
import socket
import json

#some global shit
hostname = sys.argv[1]
port = int(sys.argv[2])
username = sys.argv[3]
password = sys.argv[4]

#this is just for debugging
#paramiko.util.log_to_file("log.log")


def getData(hostname, port, username, password):
    #tbh a lot of the getData class was copy and pasted from a demo, shout out to the paramiko team
    #this is setting up socket stuff, I dont really understand it fully, but I am too lazy to go in depth and it works
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except Exception as e:
        print("*** Im crying, it failed(there was an exception): " + str(e))
        traceback.print_exc()
        sys.exit(1)

    #try connecting and doing the speedtest command
    try:
        #instantiates the transport
        trans = paramiko.Transport(sock)
        #starts the transport client, throws exception if it fails
        try:
            trans.start_client()
        except paramiko.SSHException:
            print("*** SSH negotiation failed.")
            sys.exit(1)

        #all of this is literally to just get the host keys
        try:
            keys = paramiko.util.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
        except IOError:
            try:
                keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/ssh/known_hosts")
                )
            except IOError:
                print("*** Unable to open host keys file")
                keys = {}

        key = trans.get_remote_server_key()
        if hostname not in keys:
            print("*** WARNING: Unknown host key!")
        elif key.get_name() not in keys[hostname]:
            print("*** WARNING: Unknown host key!")
        elif keys[hostname][key.get_name()] != key:
            print("*** WARNING: Host key has changed!!!")
            sys.exit(1)
        #else:
            #for personal use, ignore unless you wanna use it.
            #print("*** Host key OK.")


        #checks if it is logged in, if not it will log in. if the username or password is wrong, it will print the
        #authentication failed message and kill the script
        if not trans.is_authenticated():
            trans.auth_password(username, password)
        if not trans.is_authenticated():
            print("*** Authentication failed. :(")
            trans.close()
            sys.exit(1)

        # getting left for personal use
        # if trans.is_authenticated():
        #
        #     print("*** Authentication successful.")
        # else:
        #     print("*** Authentication failed.")

        #opens the session
        channel = trans.open_session()

        #I am leaving this print for personal use
        #print("executing command")

        try:
            channel.exec_command("speedtest -f json -P 0")
            #receives the output, it was set to 1024 bytes initially, but the json parser got upset because it would cut off
            #before the closing curly bracket
            json_output_bytes = channel.recv(2048)
            #decodes all the data and returns it.
            return json_output_bytes.decode('utf-8')
        #exceptions!!!
        except Exception as e:
            print("*** Failed to execute command: " + str(e))
            traceback.print_exc()
            channel.close()
            trans.close()
            sys.exit(1)

        #trans.close()

    #this is the exception for all of that code in the giant try block
    except Exception as e:
        print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        try:
            trans.close()
        except:
            pass
        sys.exit(1)

#parses the json data, I probably should just put this in the main() function, but eh. It helps me keep track of things
def parsejsondownload(json_data):
    #print(json_data)
    data = json.loads(json_data)
    return data['download']['bandwidth']

def main():
    downloadsp = int(parsejsondownload(getData(hostname, port, username, password)))
    #more personal debugging stuff, only thing that matters is downloadspeedinmbps, it is the actual result this whole
    #thing will return to HA
    #downloadSpeedInbytesps = str(downloadsp)
    downloadspeedinmbps = str(int(downloadsp/125000))


if __name__ == "__main__":
    main()