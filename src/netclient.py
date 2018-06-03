import socket
import ssl

class IRCClient:
	pass

TWITCH_SERVER = 'irc.chat.twitch.tv'
BOT_NAME = 'toburobo'
DEFAULT_CHANNEL = 'toburr'
DEFAULT_RECV_BUFSIZE = 4096

class InsecureMyRCClient(IRCClient):
	"""
	Twitch IRC client which DOES NOT have TLS enabled (writing this for the
	sake of getting working code for alpha. Will deprecate by version 1.0)
	"""
	def __init__(self, opass, hostname=TWITCH_SERVER, port=6667, v=True):
		"""
		Initialize connection info. Non OAuth parameters are provided to allow
		flexibility (to maybe connect to non-Twitch hosts). If you're
		connecting to Twitch, don't bother passing arguments.
		"""
		self.host = hostname
		self.port = 6667
		self.oauth = opass
		self.verbose = v
		self.socket = None
		self.channel = None
		self.numwrites = 0 # Used to track whether bot is approaching a spam-ban
		self.is_connected = False # Won't send messages if not connected

	# Needs to know:
	#	- client name (always toburobo, currently)
	#	- client's oauth token (toburobo's oauth token: not included in this code because secrets)
	#	- channel to be a part of (can be any twitch user channel; defaults to Toburr)
	def connect(self, chan=DEFAULT_CHANNEL):
		"""
		Connects this client to a specific user's chatroom
		"""
		# Disable connection if necessary
		self.is_connected = False

		# Initial connection
		if not self.socket or not self.channel:
			new_socket = self._make_socket()
			if not new_socket:
				print 'ERROR'
				return
			if self.verbose:
				print 'Connected to ' + str(new_socket.getpeername())
			self._twitch_login(new_socket)
			self.socket = new_socket
		else:
			if self.verbose:
				print 'Departing from channel ' + self.channel + '...'
			self.socket.send('PART #' + self.channel)
			self.socket.recv(1024)
			if self.verbose:
				print 'Successfully left #' + self.channel + '.'
			self.channel = None


		if self.verbose:
			print 'Joining channel ' + chan + '...'
		self.socket.send('JOIN #' + chan + '\n')
		for i in xrange(2):
			self.socket.recv(1024)
		if self.verbose:
			print 'Successfully joined #' + chan + '.'
		self.channel = chan

		self.is_connected = True

	def send(self, message):
		if self.is_connected:
			if self.verbose:
				print 'Sending message...'
			self.socket.sendall('PRIVMSG #' + self.channel + ' :' + message + '\n')
			self.socket.recv(1024)
			if self.verbose:
				print 'Successfully sent message'
			return True
		if self.verbose:
			print 'Error: client currently not connected to channel. Message not sent'
		return False

	def recv(self, bufsize=DEFAULT_RECV_BUFSIZE):
		if self.is_connected:
			if self.verbose:
				print 'Listening for message...'
			m = self.socket.recv(bufsize)
			if self.verbose:
				print 'Message received'
			return m
		if self.verbose:
			print "Error: client currently not connected to channel. Can't receive messages"
		return None

	def pong(self):
		"""
		Tell Twitch we're alive.
		"""
		self.socket.sendall('PONG :tmi.twitch.tv')
		if self.verbose():
			print 'pong'

	def _make_socket(self):
		"""
		Internal socket factory. Makes and initializes a new client socket
		and sets up host connection
		"""
		return socket.create_connection((self.host, self.port))

	def _twitch_login(self, sock):
		"""
		Internal login helper. Sends PASS and NICK, and receives welcome.
		Then fetches capabilities from server.
		Throws error if self.socket doesn't exist or is disconnected.
		"""
		sock.sendall('PASS oauth:' + self.oauth + '\nNICK toburobo\n')
		if self.verbose:
			print 'receiving login response...'
		sock.recv(1024)
		if self.verbose:
			print 'login response received.'
			print 'requesting membership...'
		sock.sendall('CAP REQ :twitch.tv/membership\n')
		sock.recv(1024)
		if self.verbose:
			print 'received membership.'
			print 'requesting tags...'
		sock.send('CAP REQ :twitch.tv/tags\n')
		sock.recv(1024)
		if self.verbose:
			print 'received tags.'
			print 'requesting commands...'
		sock.send('CAP REQ :twitch.tv/commands\n')
		sock.recv(1024)
		if self.verbose:
			print 'received commands.'



f = open('mydata.txt')
oauth = f.read()
c = InsecureMyRCClient(oauth)
c.connect('toburr')
c.send('Hi :)')
while True:
	m = c.recv()
	print m
	if m.startswith('PING :tmi.twitch.tv'):
		c.pong()
