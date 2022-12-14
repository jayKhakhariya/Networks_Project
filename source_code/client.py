import socket
import threading
import sys
import json

# connect to the server running on localhost and port mentioned in server
PORT = 16019
FORMAT = 'UTF-8'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# use this to send the message to the server
def send(msg):
    message = str(json.dumps(msg)).encode(FORMAT)
    client.send(message)

def send_mail(user_header):
    user = user_header['username']
    print('From: ', user)
    send_to_mail_address = input('To: ')
    subject = input('Subject: ')
    body = input('Message: ')

    user_header['command'] = 'send_mail'

    mail = {'from': user, 'to': send_to_mail_address, 'subject': subject, 'body': body}
    user_header['mail'] = mail
    send(user_header)

# send the request received from the client to the server
def send_requests(headers):
    
    connected = True
    # wait for user to enter the command and forward the request
    
    # print("Following are a list of commands you can use to send/receive mails")
    
    # print("send_mail - to send an email to someone: you will be asked to enter all the fields")
    # print("pull_mails")
    # print("exit")

    while connected:
        try:
            command = input('What would you like to do?: ')
            command = command.strip()

            user_header = headers

            if command.startswith('send_mail'):
                send_mail(user_header)
                # wait for yes/no from client to see if the user exists
                print('Mail successfully sent')

            elif command == 'exit':
                user_header['command'] = command  
                send(user_header)                
                connected = False
           
            elif command == 'pull_mails':
                user_header['command'] = command
                send(user_header)
                print(client.recv(2048).decode(FORMAT))
                    
        # exit on pressing Ctrl + C 
        except KeyboardInterrupt as ex:
            connected = False
            headers['command'] = 'exit'
            send(headers)
            print('I am exiting\n')
        # In case anything unexpected happens 
        except Exception as e:
            connected = False
            headers['command'] = 'exit'
            send(headers)
            print('Some error occurred, I am exiting.\n')

# connect the client to the server
def connect_server():
    try:
        headers = {}
        username = input('Enter your email: ')
        headers['username'] = username
        headers['command'] = 'my_username'
        client.connect(ADDR)
        # forwards the request

        send(headers)
        send_requests(headers)
        # make sure you pass in the username
    except Exception as ex:
        print(ex)
        print('Server is not running or has died unfortunately: \n')
        sys.exit(0)

connect_server()
    