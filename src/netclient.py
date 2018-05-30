import socket

class IRCClient:
	pass

class MyRCClient(IRCClient):

	def connect(hostname, ipv):
		mysocket = socket.socket(ipv)


ghbnex = socket.gethostbyname_ex('irc.chat.twitch.tv')
print ghbnex
#print socket.getaddrinfo(ghbnex[0], 443, socket.AF_INET6)
opass = 'oauth:qmr96t6q9qqf64w0pje93pmv6bxq4p'
s = socket.create_connection(('irc.chat.twitch.tv', 6667))
print 'client connected'
num = s.send('PASS ' + opass + '\n')
print 'sent ' + str(num) + ' bytes'
s.sendall('NICK toburobo\n')
print 'credentials sent'
print 'PASS ' + opass
print s.getpeername()

message = ''
message = s.recv(1024)
if message:
	print message

print 'finished receiving welcome'
s.send('CAP REQ :twitch.tv/membership\n')
s.recv(1024)
s.send('CAP REQ :twitch.tv/tags\n')
s.recv(1024)
s.send('CAP REQ :twitch.tv/commands\n')
print 'sent membership request'
message = s.recv(1024)
print 'received membership request'
if message:
	print message
s.send('JOIN #toburr\n')
print 'sent join channel request'
message = s.recv(1024)
if message:
	print message
message = s.recv(1024)
print message

s.send('PRIVMSG hi!\n')
print 'sent hi'
message = s.recv(1024)
print message
message = s.recv(1024)
print message
