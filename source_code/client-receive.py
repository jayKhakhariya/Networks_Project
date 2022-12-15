import socket
import threading
import sys
import json
import random
import time

# connect to the server running on localhost and port mentioned in server
PORT = 16019
FORMAT = 'UTF-8'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
SOME_TEST_MAILS = ['Do you like Soccer?', 'Hello, did you receive this email', 'What are your hobbies?', 'Please contact someone if you can\'t view this message', 'Hey, you want to watch Argentina vs France final?']
SOME_TEST_USERNAMES = ['khakhariya@gmail.com', 'chauhan@gmail.com', 'TA@gmail.com']
MAX_MAIL_COUNT = 500

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# use this to send the message to the server
def send(msg):
    message = str(json.dumps(msg)).encode(FORMAT)
    client.send(message)

# def send_mail(user_header):
#     user = user_header['username']
#     send_to_mail_address = TO_TEST_USERNAMES[random.randint(0, len(TO_TEST_USERNAMES))]
#     subject = 'Do Not Reply Mail'
#     body = SOME_TEST_MAILS[random.randint(0, len(SOME_TEST_MAILS))]

#     user_header['command'] = 'send_mail'

#     mail = {'from': user, 'to': send_to_mail_address, 'subject': subject, 'body': body}
#     user_header['mail'] = mail
#     send(user_header)

# send the request received from the client to the server
def send_requests():
    
    for username in SOME_TEST_USERNAMES:
        headers = {}
        headers['username'] = username
        headers['command'] = 'my_username'

        time.sleep(2)
        send(headers)



# connect the client to the server
def connect_server():
    try:
        client.connect(ADDR)
        send_requests()
        exit_headers = {}
        exit_headers['username'] = 'username'
        exit_headers['command'] = 'exit'

        time.sleep(2)
        send(exit_headers)
    except Exception as ex:
        print('Server is not running or has died unfortunately: \n')
        sys.exit(0)

connect_server()
    