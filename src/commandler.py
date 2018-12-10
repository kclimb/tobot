import commands as commands
import parsers as parsers
import re

class Handler:
	"""
	A handler that takes raw Twitch IRC input and does format-specific
	message processing in order to parse messages and generate appropriate
	responses.
	"""

	######################## Message Separation Routines ######################
	# Listed first so we can map message types to these routines later.

	def _separate_clearchat(self, msg):
		return {'type': 'CLEARCHAT'}

	def _separate_globaluserstate(self, msg):
		return {'type': 'GLOBALUSERSTATE'}

	def _separate_join(self, msg):
		"""
		Handles separation of JOIN messages
		"""
		excla = msg.index('!')
		firstspace = msg.index(' ')
		name = msg[1:excla]
		rest = msg[firstspace + 1:]
		secspace = rest.index(' ')
		return {'name': name, 'type': rest[:secspace]}

	def _separate_mode(self, msg):
		return {'type': 'MODE'}

	def _separate_names(self, msg):
		return {'type': 'NAMES'}

	def _separate_part(self, msg):
		return {'type': 'PART'}

	def _separate_pong(self, msg=''):
		"""
		Handles the, uh, "separation" of a received PING message (respond PONG)
		"""
		return {'type': 'PING'}

	def _separate_privmsg(self, msg):
		"""
		Handles the separation of PRIVMSG messages
		"""
		return {'type': 'PRIVMSG'}

	def _separate_roomstate(self, msg):
		return {'type': 'ROOMSTATE'}

	def _separate_usernotice(self, msg):
		return {'type': 'USERNOTICE'}

	def _separate_userstate(self, msg):
		return {'type': 'USERSTATE'}

	############################# Handler Routines ############################

	RAW_PREFIXES = {'PING': _pong, ':': _joinpart}
	MSG_DELIMITER = '\r\n'

	def __init__(self, p = parsers.MapParser(), d = MSG_DELIMITER, v = True):
		self.parser = p
		self.delimeter = d
		self.verbose = v

		# Primed with an empty string because queue should never be empty.
		# See parse_socket_data for details.
		self.msg_q = ['']

	def _parse_raw_msg(self, inputmsg):
		"""
		Examines the input message to determine what type the message is, then
		delegates to the appropriate separation routine.
		"""
		if inputmsg.startswith('PING :tmi.twitch.tv'):
			# PING
			return self._pong()
		elif inputmsg.startswith(':jtv MODE'):
			# MODE
			return '', 'MODE', inputmsg[10:]
		elif inputmsg.startswith('@badges='):
			if ".tmi.twitch.tv PRIVMSG #" in inputmsg:
				return self._privmsg(inputmsg)
			elif " :tmi.twitch.tv USERSTATE #" in inputmsg:
				return self._userstate(inputmsg)
		elif " :tmi.twitch.tv ROOMSTATE #" in inputmsg:
			return self._roomstate()
		elif " :tmi.twitch.tv USERNOTICE #" in inputmsg:
			return self._usernotice()
		firstspace = inputmsg.index(" ")
		headers = inputmsg[:firstspace]
		rest = inputmsg[firstspace + 1:]
		secspace = rest.index(" ")
		rest2 = rest[secspace + 1:]
		thirdspace = rest2.index(" ")
		#if inputmsg[0] = '@':
		return headers, cmd, rest[secspace + 1:]

	def eval(self, cmd, args):
		return cmd(*args)

	def process_msg(self):
		"""
		Removes next message from message queue and processes it.
		"""
		if len(self.msg_q) > 1:
			raw_msg = self.msg_q.pop(0)
			headers, comd, message = self._parse_raw_msg(raw_msg)
			print headers, '|', comd, '|', message
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
				# Give priority to PINGs as long as the PING was fully sent
				if msg == 'PING :tmi.twitch.tv' and msg != msgs[-1]:
					self.msg_q.insert(0, msg)
				else:
					self.msg_q.append(msg)
		#print 'queue size', len(self.msg_q) - 1

	 
# Message examples:
clearchat_ex = "@ban-reason=;room-id=77780959;target-user-id=236791797;tmi-sent-ts=1534813739972 :tmi.twitch.tv CLEARCHAT #toburr :decafsmurf\r\n"
clearchat2_ex = "@room-id=77780959;tmi-sent-ts=1534835137593 :tmi.twitch.tv CLEARCHAT #toburr\r\n"
hosttarget_ex = ":tmi.twitch.tv HOSTTARGET #toburr :- 0\r\n"
join_ex = ":toburr!toburr@toburr.tmi.twitch.tv JOIN #toburr\r\n"
mode_ex = ":jtv MODE #toburr +o toburobo\r\n"
notice_ex = "@msg-id=host_target_went_offline :tmi.twitch.tv NOTICE #toburr :alittlelisa has gone offline. Exiting host mode.\r\n"
part_ex = ":toburr!toburr@toburr.tmi.twitch.tv PART #toburr\r\n"
ping_ex = "PING :tmi.twitch.tv\r\n"
privmsg_ex = "@badges=broadcaster/1,premium/1;color=#106F73;display-name=Toburr;emotes=;id=c17fbc52-e48c-4f6f-9e5d-be7ed47d7404;mod=0;room-id=77780959;subscriber=0;tmi-sent-ts=1534012954836;turbo=0;user-id=77780959;user-type= :toburr!toburr@toburr.tmi.twitch.tv PRIVMSG #toburr :5\r\n"
roomstate_ex = "@broadcaster-lang=;emote-only=0;followers-only=-1;r9k=0;rituals=0;room-id=77780959;slow=0;subs-only=0 :tmi.twitch.tv ROOMSTATE #toburr\r\n"
userstate_ex = "@badges=moderator/1;color=;display-name=toburobo;emote-sets=0;mod=1;subscriber=0;user-type=mod :tmi.twitch.tv USERSTATE #toburr\r\n"

# a = re.compile('@badges=')
# if a.match(privmsg_ex):
# 	print ':)'
# else:
# 	print ':('
# if a.match('bleep @badges='):
# 	print ':)'
# else:
# 	print ':('
# Some tests
# h = Handler()
# h.update_msg_queue(join_ex + privmsg_ex)
# #print h._parse_next_msg(join_ex)
# h.process_msg()
# h.process_msg()