# COMP 4300 Mail Server P2P Project:

## Project idea
The main idea of the project is to implement a mail server which can send/receive their users' emails.

In a more real-based setting, mail servers will not be on the same network and there will be some complexity as to how these mail servers communicate using SMTP protocol. In this project, we have implemented our own protocol to communicate between any 2 mail servers.

We are using zeroconf library to implement a P2P network where
mail servers when joined will announce themselves to the network and mail servers already in the network will be notified about the new mail server being added to the network.

As people exchange thousands to potentially millions of mails per second, there's a possibility that the mails going to these powerful servers might not be able to process these emails if they are coming in the server in huge numbers. In order to solve this problem, an output queue is implemented on all mail servers which keeps track of mails that they have received and needs to be forwarded to the appropriate user.


## Testing environment
 - The implementation of zeroconf used in this project only works with Linux operating systems. 
 - The code has been tested on University of Manitoba's aviary machines which is a set of computers available to use for the students in the Department of CS to run their assignments. Aviary is just a name to denote that it's linux machines.
    - There are about 25-30 different aviary bird machines all connected with each other and sort of forms a Local Area Network. 
    - Specs of the machines it was tested on: **Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-56-generic x86_64)**

## How to run the code?
 - Note: This is a terminal-based application
 - Before you run the code, make sure you have the following things installed, and have all the files (and necessary zeroconf code) in the source_code folder with the same file hierarchy.

- Make sure you have Python 3.10.8 installed

- Running a mail_server on a machine:
     - **python mail_server <IP_ADDRESS>** (where IP_ADDRESS denotes the) 
     - you can log into any of the aviary machines and run ifconfig to see the ip address of the machine.
     - In order to form a P2P network, you need to run the above command from different machines.
     - Once a P2P network has been formed, you can connect multiple clients with a node or mail server and can send emails using following commands to send/pull mails from the mail server.
       - send_mail command to send an email to someone
	    - pull_mails command to fetch the mails you received from someone
       - exit to terminate the connection


## Tools/Libraries used:
  - **Zeroconf**:
   
     - We are using zeroconf to sort of form a P2P network of mail servers. When the mail_server runs, it announces itself to the network, and any other services that already exist will notify the new mail server that just joined the network. And, hence this way with more mail servers is added onto the network, a P2P network will be formed between these mail servers.
     
     
  - **Environment setup**:
      -	This application has been tested on aviary machines available at University of Manitoba and can be logged into in following manner.
  	        - You just need to ssh **[umnetid]@[machine_name].cs.umanitoba.ca** where umnetid is your U of M’s umnetid
                 - Some of the machine names you can use sparrow, owl, oriole, pelican
      - If you don’t have access, you’ll have to contact someone in the IT department to grant you access to these machines
      - You need to have Python 3.10.8 installed, and make sure to have all the files (including zeroconf/ifaddr code) before testing the mail_server. 

## Testing:
  - The main testing of our code is to check whether the peers are able to communicate and handle multiple requests at once, i.e., sending and delivering huge number of emails. For this, we tested our queuing implementation to check if the server can collect and distribute the emails accordingly using the following ‘client bots’:        
     - ‘client-testbot’: This bot will create some sender clients (clients who will send the email) and will make 500 attempts to send emails to random people The server then will put all the incoming mails into a queue first before sending to the user. The queuing and dequeuing can be seen on the server side when this file runs.
     - ‘client-receive’: This bot will create some receiver clients (clients who will receive the emails) and each receiver client will receive the intended number of emails without any data loss.
     - ‘client-receive’ bot needs to be run before client-test-bot runs since the former creates a set of clients on the network to which the clients in the latter will send the emails to.
     
     
 - Each test bot will be connected to a different peer (mail server). Mail servers will communicate with each other according to the implemented communication protocol and will send/receive emails accordingly.
