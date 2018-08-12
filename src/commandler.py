import commands as commands
import parsers as parsers

class Separator:
	"""
	A class for taking in a Twitch IRC message and separating it into
	key-value pairs that can be understood by the parser.
	"""

	RAW_PREFIXES = {'PING': _pong, ':': _joinpart}
	def __init__(self, p = RAW_PREFIXES, d = MSG_DELIMITER):
		self.prefixes = p
		self.delimeter = d

	def _joinpart(self, msg):
		"""
		Handles separation of JOIN and PART messages
		"""
		excla = msg.index('!')
		firstspace = msg.index(' ')
		name = msg[1:excla]
		rest = msg[firstspace + 1:]
		secspace = rest.index(' ')
		return {'name': name, 'cmd': rest[:secspace]}

	def _pong(self):
		"""
		Handles the, uh, "separation" of a received PING message (respond PONG)
		"""
		return {'cmd': 'PONG'}


class Handler:
	"""
	A handler that takes raw Twitch IRC input and does format-specific
	message processing in order to parse messages and generate appropriate
	responses.
	"""
	MSG_DELIMITER = '\r\n'

	def __init__(self, p = parsers.MapParser(), d = MSG_DELIMITER, v = True):
		self.parser = p
		self.delimeter = d
		self.verbose = v

		# Primed with an empty string because queue should never be empty.
		# See parse_socket_data for details.
		self.msg_q = ['']

	def _parse_next_msg(self, inputmsg):
		firstspace = inputmsg.index(" ")
		headers = inputmsg[:firstspace]
		rest = inputmsg[firstspace + 1:]
		secspace = rest.index(" ")
		cmd = rest[:secspace]
		return headers, cmd, rest[secspace + 1:]

	def eval(self, cmd, args):
		return cmd(*args)

	def handle(self):
		"""
		Removes next message from message queue and processes it.
		"""
		if len(self.msg_q) > 1:
			next_msg = self.msg_q.pop(0)
			headers, comd, message = self._parserawmsg(next_msg)
			cmds = self.parser.translate(message)
			for cmd in cmds:
				if self.verbose:
					print 'Handler says', cmd
					print self.eval(cmd[0], cmd[1])
		else:
			if self.verbose:
				print 'Nothing currently in message queue'
			return 0

	def update_msg_queue(self, sockstream):
		"""
		Given recent socket data, parses data into individual messages and
		updates the queue of messages to be handled
		"""
		msgs = sockstream.split(self.delimeter)
		if len(msgs) > 0:
			self.msg_q[-1] += msgs[0]
			for msg in msgs[1:]:
				self.msg_q.append(msg)

	 

# msg = ":toburr!toburr@toburr.tmi.twitch.tv JOIN #toburr"
# h = Handler()
# print h._parserawmsg(msg)
a = [4]
for guy in a[1:]:
	print 'ha'