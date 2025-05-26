#Author:snoorkwashanging
#shoutout to the paramiko devs, some of this code did come from a demo, and of course I mostly use paramiko to do stuff
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Some requirements:
#some server with the Ookla speedtest-cli package (https://www.speedtest.net/apps/cli)
#paramiko(just run pip install in this folder)
#the host key for the server, as in you should've connected to the ssh server before
#more will be added here, when I finish this stuff lol
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# How to use:
# python speed.py hostname port username password
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#things I need to do still:
#TODO: get the result to HA and have it do what I want it to do
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


#this is just for debugging
#paramiko.util.log_to_file("log.log")

def get_data(hostname, port, username, password):
    #tbh a lot of the get_data class was copy and pasted from a demo, shout out to the paramiko team
    #this is setting up socket stuff, I dont really understand it fully, but I am too lazy to go in depth and it works
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except Exception as e:
        print("*** Im crying, it failed(there was an exception): " + str(e))
        traceback.print_exc()
        sys.exit(1)

    #instantiates the transport
    transport = paramiko.Transport(sock)

    #try connecting and doing the speedtest command
    try:
        #starts the transport client, throws exception if it fails
        try:
            transport.start_client()
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

        key = transport.get_remote_server_key()
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
        if not transport.is_authenticated():
            transport.auth_password(username, password)
        if not transport.is_authenticated():
            print("*** Authentication failed. :(")
            transport.close()
            sys.exit(1)

        # getting left for personal use
        # if transport.is_authenticated():
        #
        #     print("*** Authentication successful.")
        # else:
        #     print("*** Authentication failed.")

        #opens the session
        channel = transport.open_session()

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
            transport.close()
            sys.exit(1)

        #transport.close()

    #this is the exception for all of that code in the giant try block
    except Exception as e:
        print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        try:
            transport.close()
        except:
            pass
        sys.exit(1)

#parses the json data, I probably should just put this in the main() function, but eh. It helps me keep track of things
def parse_json_data(json_data):
    #print(json_data)
    data = json.loads(json_data)
    return data['download']['bandwidth']

def main():
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    download_speed = int(parse_json_data(get_data(hostname, port, username, password)))
    #more personal debugging stuff, only thing that matters is download_speed_mbps, it is the actual result this whole
    #thing will return to HA
    #downloadSpeedInbytesps = str(download_speed)
    download_speed_mbps = str(int(download_speed/125000))
    print(download_speed_mbps)


if __name__ == "__main__":
    main()