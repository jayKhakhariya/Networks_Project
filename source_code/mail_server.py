import sys
import json
import socket
import select
import threading
import time
from zeroconf import IPVersion, ServiceInfo, ServiceBrowser, Zeroconf
from queue import Queue

# constants
FORMAT = 'UTF-8'
PEER_PORT = 5052
MAX_QUEUE_SIZE = 500
MAX_CLIENTS_CONNECTED = 8

# remember to just decide the format 
# and add the peers to the list
peers = []
info_peers = []

# to keep track of all connected clients
clients = []
new_client_setup = False

server_socket = None
local_socket = None
host_name = sys.argv[1]

# bind local and server socket with tcp and udp respectively
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setblocking(False)
server_socket.bind((host_name, PEER_PORT))

local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_socket.setblocking(False)
local_socket.bind(('127.0.0.1', 16019))
local_socket.listen(socket.SOMAXCONN)

stop_thread = False
output_message_queue = Queue(maxsize = MAX_QUEUE_SIZE)
input_mails = []


class MyListener:
    def remove_service(self, zeroconf, type, name):
        print("Service ", name, "removed")

        for infoPeer in info_peers:
            if(infoPeer[0] == type and infoPeer[1] == name):
                addrTup = [socket.inet_ntoa(
                    infoPeer[2].addresses[0]), infoPeer[2].port]
                print(addrTup, " removed")
                peers.remove(addrTup)
                info_peers.remove(infoPeer)

    def add_service(self, zeroconf, type, name):
        # add the service if there is any service....
        # also add the tuple
        info = zeroconf.get_service_info(type, name)

        # this ip address is not the name
        ipaddr = socket.inet_ntoa(info.addresses[0])
    
        port = info.port

        # don't add yourself
        if(ipaddr != host_name):
            # what about port?
            print("\nService %s added, service info: %s\n" % (name, info))
            peers.append([ipaddr, port])
            info_peers.append([type, name, info])

    def update_service(self, zeroconf, type, name):
        print("Service ", name, "updated")


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_OUR_p2pmail._udp.local.", listener)

if __name__ == '__main__':
    ip_version = IPVersion.V4Only

    desc = {}
    info = ServiceInfo(
        "_OUR_p2pmail._udp.local.",
        "OUR Mail Server " + socket.gethostname() + "._p2pmail._udp.local.",
        addresses=[socket.inet_aton(host_name)],
        port=PEER_PORT,
        properties=desc,
        server=socket.gethostname() + ".local.",
    )
    zeroconf = Zeroconf(ip_version=ip_version)
    zeroconf.register_service(info)




# keep track of sockets to listen data from
inputs = [server_socket, local_socket]
outputs = []  # None

# find the peer in a list of peers with the addr tuple
def find_peer(addr):
    for peer in peers:
        if(peer[0] == addr[0] and peer[1] == addr[1]):
            return peer
    return None 

# find the user among active/inactive clients
def find_user(user):
    for client in clients:
        if client['username'] == user:
            return client

    return None

# add the username when a client joins the service
def add_username(source, user, current_num_clients):
    if current_num_clients < MAX_CLIENTS_CONNECTED:
        new_client = {'username': user, 'connection': source, 'inbox': []}
        clients.append(new_client)
        current_num_clients += 1    

# dequeue the mail once the mail's receiving server has been found
def dequeue_mail(mail_id):
    for mail in input_mails:
        if mail_id == mail['mail_id']:
            input_mails.remove(mail)
            return mail
    return None

# dequeue from the queue to put mails into mailboxes
def put_mails_into_inboxes():
    while True:
        global stop_thread

        if stop_thread:
            break 
        
        time.sleep(10)

        if not output_message_queue.empty():
            new_mail = output_message_queue.get()
            print('Dequeu - ing -', new_mail, ' from the queue')
            client = find_user(new_mail['to'])

            client['inbox'].append(new_mail)

        else:
            time.sleep(1)


def print_clients():
    for client in clients:
        print(client['username'])

# just fetch a particular user's emails
def fetch_mails(user):
    mails = '---------------'
    client = find_user(user)
    client_inbox = client['inbox']
    for mail in client_inbox:
        mails += '\nReceived From: ' + mail['from'] + '\n'
        mails += 'Subject: ' + mail['subject'] + '\n'
        mails += 'Body: ' + mail['body'] + '\n'
        mails += '---------------'
    
    return mails

# actual mail server implementation
def run_mail_server():
    try:
        current_num_clients = 0
        mail_id = 0
        
        # run the thread which constantly works on putting mails into mailboxes
        thread = threading.Thread(target = put_mails_into_inboxes, args=())
        thread.start()

        print("Listening on interface " + host_name + ', ' + str(PEER_PORT))
        while inputs:
            try:
                print("Waiting to receive some input")
                timeout = 50
                # multithread block using select
                readable, _, _ = select.select(inputs, outputs, inputs, timeout)
                
                # we have received something check all the sockets
                for source in readable:
                    if source is server_socket:
                        data, addr = source.recvfrom(1024)
                        
                        #only accept msgs with command attribute
                        try:
                            peer = find_peer(addr)
                            if peer:
                                data_received = json.loads(data.decode(FORMAT), strict=False)
                                
                                command = data_received['command']
                                user = data_received['to']
                                
                                match command:
                                    # in case a peer receives a mail
                                    case 'receive_mail':    

                                        from_user = data_received['from']
                                        to_user = data_received['to']
                                        subject = data_received['subject']
                                        body = data_received['body']

                                        mail = {'from': from_user, 'to': to_user, 'subject': subject, 'body': body}

                                        print('\n-------\nMail has been received: ')
                                        print('Adding ', mail, ' to the queue')     

                                        if not output_message_queue.full():
                                            output_message_queue.put_nowait(mail)
                                        else:
                                            print('Client will have to wait; Queue is full')
                                    # check whether the peer has the client and reply appropriately
                                    case 'is_user_connected':
                                        reply = ''
                                        if find_user(user):
                                            reply = 'Yes'
                                        else:
                                            reply = 'No'

                                        my_reply = {'to': user , 'command': 'query_response', 'reply': reply, 'mail_id': data_received['mail_id']}
                                        server_socket.sendto(str.encode(json.dumps(my_reply)), addr)                                            
                                    # received a query response for the query I sent when I received a mail
                                    case 'query_response':
                                        # dequeue the mails that wanted 
                                        reply = data_received['reply']
                                        id = data_received['mail_id']
                                        if reply == 'Yes':
                                            mail_to_send = dequeue_mail(id)
                                            if mail_to_send:
                                                mail_to_send['command'] = 'receive_mail'
                                                # if the reply was yes send the email to that mail server
                                                server_socket.sendto(str.encode(json.dumps(mail_to_send)), addr)                                            
                                            else:
                                                print('no mail to send')
                            else:
                                print('ignore; received something from unknown')
                        except Exception as e:
                            print(sys.exc_info()[2].tb_lineno)
                            print(e)

                    # heard from local client for the first time
                    elif source is local_socket:
                        conn, addr = source.accept()
                        # don't block the conn
                        conn.setblocking(0)

                        if current_num_clients < MAX_CLIENTS_CONNECTED:
                            inputs.append(conn)
                            print("Client ", addr, " has connected:")
                        else:
                            # send and exit message since client could not be connected
                            print('send client exit message')

                    else:
                        data_received = source.recv(1024)
                        if data_received:
                            decode_data = json.loads(data_received.decode(FORMAT))
                            
                            user = decode_data['username']
                            command = decode_data['command']

                            if user and command:
                                match command:

                                    # received a new connection, add the user
                                    case 'my_username':
                                        add_username(source, user, current_num_clients)

                                    case 'exit':
                                        print("client has quit")
                                        source.close()
                                        inputs.remove(source)

                                    # client wants to send the mail
                                    case 'send_mail':
                                        
                                        mail = decode_data['mail']
                                        mail_id += 1
                                        mail['mail_id'] = mail_id

                                        if mail:
                                            print(mail)
                                            to_user = find_user(mail['to'])
                                            # check if I have the mail recipient connected 
                                            if to_user:
                                                if not output_message_queue.full():
                                                    print('Mail has been received: ')
                                                    print('Adding ', mail, ' to the queue')
                                                    output_message_queue.put_nowait(mail)
                                                else:
                                                    print('Queue is full')
                                            else:
                                                # else put it in the queue
                                                input_mails.append(mail)
                                                
                                                # and then see which peer has that user connected
                                                for peer in peers:  
                                                    addrtuple = (peer[0], peer[1])
                                                    is_client_connected = {'to': mail['to'], 'command': 'is_user_connected', 'mail_id': mail_id}
                                                    server_socket.sendto(str.encode(json.dumps(is_client_connected)), addrtuple)
                                    # fetch the emails
                                    case 'pull_mails':     
                                        data_send = fetch_mails(user)
                                        source.send(str.encode(data_send))

                            else:
                                print('invalid request; ignore')    

                        else:
                            print("client has quit")
                            source.close()
                            inputs.remove(source)

            # cleanup all sockets after server crashes
            except KeyboardInterrupt:
                print("Server exiting ")
                # clean all the sockets
                for clientSocket in inputs:
                    if((clientSocket is not local_socket) and (clientSocket is not server_socket)):
                        clientSocket.close()

                server_socket.close()
                local_socket.close()
                sys.exit(0)  # exit the program
            except Exception as e:
                print(e)

    except Exception as e:
        print(e)
    # unregister the service
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()
        global stop_thread
        stop_thread = True
        # kill the thread
        thread.join()


run_mail_server()
