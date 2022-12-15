import socket
import sys
import json
import random
import time

# connect to the server running on localhost 
# and port mentioned in server
PORT = 16019
FORMAT = 'UTF-8'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
SOME_TEST_MAILS = ['Do you like Soccer?', 'Hello, did you receive this email', 'What are your hobbies?', 'Please contact someone if you can\'t view this message', 'Hey, you want to watch Argentina vs France final?']
SOME_TEST_USERNAMES = ['animesh@gmail.com', 'jay@gmail.com', 'comp4300@gmail.com', 'earth@outlook.com', 'argentina-wins@gmail.com']
TO_TEST_USERNAMES = ['khakhariya@gmail.com', 'chauhan@gmail.com', 'TA@gmail.com']
MAX_MAIL_COUNT = 50

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# use this to send the message to the server
def send(msg):
    message = str(json.dumps(msg)).encode(FORMAT)
    client.send(message)

def send_mail(user_header):
    user = user_header['username']
    send_to_mail_address = TO_TEST_USERNAMES[random.randint(0, len(TO_TEST_USERNAMES) - 1)]
    subject = 'Do Not Reply Mail'
    body = SOME_TEST_MAILS[random.randint(0, len(SOME_TEST_MAILS) - 1)]

    user_header['command'] = 'send_mail'

    mail = {'from': user, 'to': send_to_mail_address, 'subject': subject, 'body': body}
    user_header['mail'] = mail
    send(user_header)

# send the request received from the client to the server
def send_requests():
    
    for username in SOME_TEST_USERNAMES:
        headers = {}
        headers['username'] = username
        headers['command'] = 'my_username'

        time.sleep(2)
        send(headers)

    mail_count = 0
    while mail_count < MAX_MAIL_COUNT:
        headers = {}
        random_number = random.randint(0, len(SOME_TEST_USERNAMES) - 1)
        print(random_number)
        headers['username'] = SOME_TEST_USERNAMES[random_number]

        print(headers)
        send_mail(headers)
        mail_count += 1

        time.sleep(2)

# connect the client to the server
def connect_server():
    try:
        client.connect(ADDR)
        send_requests()
        exit_headers = {}
        exit_headers['username'] = 'username'
        exit_headers['command'] = 'exit'

        send(exit_headers)
    except Exception as ex:
        print(ex)
        print(sys.exc_info()[2].tb_lineno)
        print('Server is not running or has died unfortunately: \n')
        sys.exit(0)

connect_server()
    