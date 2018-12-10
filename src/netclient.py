import select
import socket
import ssl
import time

class IRCClient:
	pass

TWITCH_SERVER = 'irc.chat.twitch.tv' # Default connection hostname. Bot currently only supports Twitch, no plans to change that
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
		
		# Initial connection
		if not self.socket or not self.channel:
			new_socket = self._make_and_login()
			# Disable connection if necessary
			self.is_connected = False
			self.socket = new_socket
		# Already connected, just changing channels
		else:
			if self.verbose:
				print 'Departing from channel ' + self.channel + '...'
			# Disable connection if necessary
			self.is_connected = False
			self.socket.sendall('PART #' + self.channel + '\n')
			m = self.socket.recv(1024)
			if self.verbose:
				print 'Successfully left #' + self.channel + '.'
				print 'Part response: ' + m
			self.channel = None

		self._join_channel(self.socket, chan)

		return True

	def gethostname(self):
		return self.host

	def getsocket(self):
		"""
		Returns this client's networking socket.
		"""
		return self.socket

	def pong(self):
		"""
		Tell Twitch we're alive.
		"""
		self.socket.sendall('PONG :tmi.twitch.tv\n'.encode('utf-8'))
		if self.verbose:
			print 'pong'

	def recv(self, bufsize=DEFAULT_RECV_BUFSIZE):
		if self.is_connected:
			if self.verbose:
				print 'Listening for message...'
			# Use select so that our client's recv blocks (or at least waits)
			# regardless of whether the socket does
			sock_ready = select.select([self.socket], [], [])
			while not sock_ready[0]:
				# We shouldn't get here, but if we do, try again
				sock_ready = select.select([self.socket], [], [])
			m = self.socket.recv(bufsize).decode()
			# ms = m.split('\r\n')
			# for guy in ms:
			# 	print '"' + guy + '"'
			# print 'ms len =', len(ms)
			if len(m) == 0:
				print 'Error: disconnected from irc server!'
				self.is_connected = False
				# TODO: properly handle the disconnection
			elif self.verbose:
				print 'Message received:'
				print m
			return m
		if self.verbose:
			print "Error: client currently not connected to channel. Can't receive messages"
		return None

	def refresh(self):
		"""
		Resets connection to current channel
		TODO: finish implementing me
		"""
		new_socket = self._make_and_login()

	def send_message(self, message):
		if self.is_connected:
			if self.verbose:
				print 'Sending message...'
			self.socket.sendall('PRIVMSG #' + self.channel + ' :' + message + '\n')
			m = self.socket.recv(1024).decode()
			if self.verbose:
				print 'Successfully sent message ' + message
				print 'Received response ' + m
			self.numwrites += 1
			return True
		if self.verbose:
			print 'Error: client currently not connected to channel. Message not sent'
		return False

	def sethostname(self, newname):
		if self.is_connected:
			# TODO: Raise "Bot is running" exception instead
			e = "Error: could not change hostname because client is already connected to a server."
			e += '\nPlease disconnect from the current server to change the hostname.'
			print e
		else:
			self.hostname = newname

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
		x = sock.recv(1024)
		if self.verbose:
			print 'login response received.'
			print x
			print 'requesting membership...'
		sock.sendall('CAP REQ :twitch.tv/membership\n')
		x = sock.recv(1024)
		if self.verbose:
			print 'received membership.'
			print x
			print 'requesting tags...'
		sock.sendall('CAP REQ :twitch.tv/tags\n')
		x = sock.recv(1024)
		if self.verbose:
			print 'received tags.'
			print x
			print 'requesting commands...'
		sock.sendall('CAP REQ :twitch.tv/commands\n')
		x = sock.recv(1024)
		if self.verbose:
			print 'received commands.'
			print x
			print 'Login successful.'

	def _make_and_login(self):
		"""
		Internal onvenience function that does both of the above two at once,
		and also throws in some whistling.
		"""
		new_socket = self._make_socket()
		if not new_socket:
			print 'ERROR creating socket'
			return
		if self.verbose:
			print 'Connected to ' + str(new_socket.getpeername())
		self._twitch_login(new_socket)
		return new_socket

	def _join_channel(self, sock, chan):
		"""
		Internal function that given a logged-in socket,
		joins a given channel.
		"""
		if self.verbose:
			print 'Joining channel ' + chan + '...'
		sock.sendall('JOIN #' + chan + '\n')
		for i in xrange(2):
			x = sock.recv(1024)
			if self.verbose:
				print x
		if self.verbose:
			print 'Successfully joined #' + chan + '.'
		self.channel = chan
		if sock is self.socket:
			self.is_connected = True

	def _part_channel(self, sock, chan):
		"""
		Internal function that given a logged-in socket currently in a channel,
		has the socket depart that channel.
		"""
		if self.verbose:
			print ''




f = open('mydata.txt')
oauth = f.read()
c = InsecureMyRCClient(oauth)
c.connect('toburr')
c.send_message('Hi :)')
#c.socket.sendall('NAMES #toburr\n')
while True:
	m = c.recv()
	if m.startswith('PING :tmi.twitch.tv'):
		c.pong()
	time.sleep(8)
