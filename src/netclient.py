import select
import socket
import ssl
import time

TWITCH_SERVER = 'irc.chat.twitch.tv' # Default connection hostname. Bot currently only supports Twitch, no plans to change that
BOT_NAME = 'tobot'
DEFAULT_CHANNEL = 'toburr'
DEFAULT_RECV_BUFSIZE = 4096

class IRCClient:
	def __init__(self, opass, hostname, r_size, v):
		self.host = hostname
		self.oauth = opass
		self.read_size = r_size
		self.socket = None
		self.channels = set([])
		self.numwrites = 0 # Used to track whether bot is approaching a spam-ban
		self.is_connected = False # Won't send messages if not connected. Maps channel->True/False
		self.verbose = v


class InsecureMyRCClient(IRCClient):
	"""
	Twitch IRC client which DOES NOT have TLS enabled (writing this for the
	sake of getting working code for alpha. Will deprecate by version 1.0)
	"""
	def __init__(self, opass, hostname=TWITCH_SERVER, port=6667, r_size=DEFAULT_RECV_BUFSIZE, v=True):
		"""
		Initialize connection info. Non OAuth parameters are provided to allow
		flexibility (to maybe connect to non-Twitch hosts). If you're
		connecting to Twitch, don't bother passing arguments.
		"""
		IRCClient.__init__(self, opass, hostname, r_size, v)
		self.port = 6667

	# Needs to know:
	#	- client name (always tobot)
	#	- client's oauth token (tobot's oauth token: not included in this code because secrets)
	#	- channel to be a part of (can be any twitch user channel; defaults to Toburr)
	def connect(self, chan=DEFAULT_CHANNEL):
		"""
		Connects this client to a specific user's chatroom
		"""
		if chan in self.channels:
			if self.verbose:
				print 'Already in the specified channel'
			return False
		# Set up socket if it's our first connection
		if not self.socket:
			new_socket = self._make_and_login()
			# Disable connection if necessary
			self.is_connected = False
			self.socket = new_socket

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

	def recv(self, bufsize=None):
		if bufsize == None:
			bufsize = self.read_size
		if self.is_connected:
			if self.verbose:
				print 'Listening for message...'
			# Use select so that our client's recv blocks (or at least waits)
			# regardless of whether the socket does
			sock_ready = select.select([self.socket], [], [])
			while not sock_ready[0]:
				# We shouldn't get here, but if we do, try again
				sock_ready = select.select([self.socket], [], [])
			m = self.socket.recv(bufsize).decode('utf-8')
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
				print repr(m), '\n'
			return m
		elif self.verbose:
			print "Error: client currently not connected to channel. Can't receive messages"
		return None

	def refresh(self, chan):
		"""
		Resets connection to current channel
		TODO: test me
		"""
		if not self.socket:
			self.socket = self._make_and_login()
		elif chan in self.channels:
			self._part_channel(self.socket, chan)
		self._join_channel(self.socket, chan)

	def send_message(self, message, isprivmsg=True, chan=DEFAULT_CHANNEL):
		if self.is_connected:
			if self.verbose:
				print 'Sending message...'
			if chan in self.channels:
				if isprivmsg:
					self.socket.sendall('PRIVMSG #' + chan + ' :' + message + '\n')
				else:
					self.socket.sendall(message)
				#m = self.socket.recv(self.read_size).decode()
				if self.verbose:
					print 'Successfully sent message ' + message
					#print 'Received response ' + m
				self.numwrites += 1
				return True
			elif self.verbose:
				print 'Error: client not currently connected to channel: ' + chan
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
		Throws error if sock doesn't exist or is disconnected.
		"""
		# First, connect to twitch server with our credentials
		sock.sendall('PASS oauth:' + self.oauth + '\nNICK tobot\n') # TODO: generalize bot name stuff
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
		if chan in self.channels:
			print 'Error: tobot is already in channel: ' + chan
			return
		if self.verbose:
			print 'Joining channel ' + chan + '...'
		sock.sendall('JOIN #' + chan + '\n')
		for i in xrange(2):
			x = sock.recv(1024)
			if self.verbose:
				print x
		if self.verbose:
			print 'Successfully joined #' + chan + '.'
		self.channels.add(chan)
		if sock is self.socket:
			self.is_connected = True

	def _part_channel(self, sock, chan):
		"""
		Internal function that given a logged-in socket currently in a channel,
		has the socket depart that channel.
		"""
		if chan not in self.channels:
			print 'Error: tobot already not in channel: ' + chan
			return
		if self.verbose:
			print 'Departing from channel ' + chan + '...'
		self.is_connected = False	# Disable connection if necessary
		sock.sendall('PART #' + chan + '\n')	# This is the Leave IRC command
		m = sock.recv(self.read_size)
		if m != None and self.verbose:
			print 'Successfully left #' + chan + '.'
			print 'Part response: ' + m
		self.channels.remove(chan)


#f = open('mydata.txt')
#oauth = f.read()
#c = InsecureMyRCClient(oauth)
#c.connect('toburr')
#c.send_message('Hi :)')
##c.socket.sendall('NAMES #toburr\n')
#while True:
#	m = c.recv()
#	if m.startswith('PING :tmi.twitch.tv'):
#		c.pong()
#	elif m.endswith('ctrlc\r\n'):
#		break
#	c._part_channel(c.socket,'toburr')
#	time.sleep(1)
#	c.recv()
#	time.sleep(1)
#	c._join_channel(c.socket,'toburr')
