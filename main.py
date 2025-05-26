#thingy for getting a speedtest json from a local unifi controller, parsing it, and sending it to
#a home assistant instance
# this shit will only work with passwords for now, I will figure out keys later, but I don't care too much since it
#runs on a local network and not over the internet
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

paramiko.util.log_to_file("log.log")
##tbh a lot of this was copy and pasted from a demo

def getData(hostname, port, username, password):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except Exception as e:
        print("*** Im crying, it failed: " + str(e))
        traceback.print_exc()
        sys.exit(1)

    try:
        trans = paramiko.Transport(sock)
        try:
            trans.start_client()
        except paramiko.SSHException:
            print("*** SSH negotiation failed.")
            sys.exit(1)

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
        else:
            print("*** Host key OK.")


        if not trans.is_authenticated():
            trans.auth_password(username, password)
        if not trans.is_authenticated():
            print("*** Authentication failed. :(")
            trans.close()
            sys.exit(1)

        if trans.is_authenticated():
            print("*** Authentication successful.")
        else:
            print("*** Authentication failed.")

        channel = trans.open_session()
        channel.set_combine_stderr(True)
        print("poggers")
        print("executing command")

        try:
            channel.exec_command("speedtest-cli --json")
            #receive the output
            json_output_bytes = channel.recv(1024)
            print(type(json_output_bytes))
            json_output = json_output_bytes.decode('utf-8')
            print(type(json_output))
            print("JSON Output: " + json_output)
            print("IT WORKED!!!!")

        except Exception as e:
            print("*** Failed to execute command: " + str(e))
            traceback.print_exc()
            channel.close()
            trans.close()
            sys.exit(1)

        channel.close()
        trans.close()

    except Exception as e:
        print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        try:
            trans.close()
        except:
            pass
        sys.exit(1)
