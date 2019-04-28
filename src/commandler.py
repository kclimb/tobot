#import commands as commands
import api_managers as api
import parsers as parsers
import re

commands = parsers.commands

class Handler:
	"""
	A handler that takes raw Twitch IRC input and does format-specific
	message processing in order to parse messages and generate appropriate
	responses.
	"""

	######################## Message Separation Routines ######################
	# Listed first so we can map message types to these routines later.

	def _parse_headers(self, headers):
		"""
		Used by several of the subsequent "_separate" routines to parse message
		headers.
		"""
		hdrs = headers[1:]
		keyval = hdrs.split(';')
		hdr_dict = {}
		for pair in keyval:
			key,_,val = pair.partition('=')
			hdr_dict[key] = val
		return hdr_dict

	def _separate_clear_user_chat(self, msg):
		return {'type': 'CLEARUSERCHAT'}

	def _separate_clearchat(self, msg):
		return {'type': 'CLEARCHAT'}

	def _separate_globaluserstate(self, msg):
		return {'type': 'GLOBALUSERSTATE'}

	def _separate_joinpart(self, msg):
		"""
		Handles separation of JOIN and PART messages
		"""
		excla = msg.index('!')
		firstspace = msg.index(' ')
		name = msg[1:excla]
		rest = msg[firstspace + 1:]
		secspace = rest.index(' ')
		if '\r\n' in rest:	# For some reason the delimeter isn't there sometimes in testing?
			endline = rest.index('\r\n')
		else:
			endline = len(rest)
		return {'channel': rest[secspace+2:endline], 'name': name, 'type': rest[:secspace]}

	def _separate_mode(self, msg):
		return {'msg': msg[10:], 'type': 'MODE'}

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
		Handles the separation of PRIVMSG messages (aka "chat" messages)
		"""
		# print 'separating privmsg...'
		firstspace = msg.index(' ')
		headers = msg[:firstspace]
		rest = msg[firstspace+1:]
		secondspace = rest.index(' ')
		#sender = rest[1:rest.index('!')] Unused since we can get this from headers
		rest2 = rest[secondspace+1:]
		thirdspace = rest2.index(' ')
		rest3 = rest2[thirdspace+1:]
		fourthspace = rest3.index(' ')
		channel = rest3[1:fourthspace]
		payload = rest3[fourthspace+2:].rstrip('\r\n')
		# print 'separated privmsg'
		return {'channel': channel, 'headers': self._parse_headers(headers), 'message': payload, 'type': 'PRIVMSG'}

	def _separate_roomstate(self, msg):
		return {'type': 'ROOMSTATE'}

	def _separate_usernotice(self, msg):
		return {'type': 'USERNOTICE'}

	def _separate_userstate(self, msg):
		return {'type': 'USERSTATE'}

	############################# Handler Routines ############################

	MSG_DELIMITER = '\r\n'

	def __init__(self, p = parsers.MapParser(), d = MSG_DELIMITER, v = True):
		self.parser = p
		self.delimeter = d
		self.verbose = v

		# Primed with an empty string because queue should never be empty.
		# See parse_socket_data for details.
		self.msg_q = ['']
		self.api_mgr = api.TwitchAPIManager()

	def _parse_raw_msg(self, inputmsg):
		"""
		Examines the input message to determine what type the message is, then
		delegates to the appropriate separation routine.
		"""
		# print 'parsing raw message\n',inputmsg
		if inputmsg.startswith('PING :tmi.twitch.tv'):
			# PING
			return self._separate_pong()
		elif inputmsg.startswith('@badge-info=') or inputmsg.startswith('@badges='):
			firstspace = inputmsg.index(" ")
			headers = inputmsg[:firstspace]
			rest = inputmsg[firstspace + 1:]
			secspace = rest.index(" ")
			rest2 = rest[secspace + 1:]
			if rest2.startswith("PRIVMSG #"):
				# print 'parse raw reached privmsg'
				return self._separate_privmsg(inputmsg)
			elif rest2.startswith("USERSTATE #"):
				return self._separate_userstate(inputmsg)
		elif inputmsg.startswith(':jtv MODE'):
			# MODE
			return self._separate_mode(inputmsg)
		elif inputmsg.startswith(':tmi.twitch.tv'):
			return {'type': 'HOSTTARGET'}
		elif inputmsg.startswith(':'):
			return self._separate_joinpart(inputmsg)
		elif inputmsg.startswith("@msg-id="):
			return self._separate_usernotice(inputmsg)
		elif inputmsg.startswith("@broadcaster-lang="):
			return self._separate_roomstate(inputmsg)
		elif inputmsg.startswith("@ban-reason="):
			return self._separate_clear_user_chat(inputmsg)
		elif inputmsg.startswith("@room-id="):
			return self._separate_clearchat(inputmsg)
		#return headers, cmd, rest[secspace + 1:]
		# print 'unknown command'
		return {'type': 'UNKNOWN'}

	def _get_extra_params(self, cmd, data):
		"""
		Given an expected command and metadata from the message issuing the
		command, return any expected arguments that don't originate from
		the message body itself.
		"""
		params = []
		cmd_func = cmd[0]
		if cmd_func in commands.NEEDS_METADATA:
			params.append(data)
		if cmd_func in commands.NEEDS_API:
			params.append(self.api_mgr)
		return params

	def _do_commands(self, command_list, data):
		"""
		Actually run the commands parsed from the message.
		Returns any responses this bot needs to send to chat.
		"""
		responses = []
		for cmd in command_list:
			# Get any params we need from message metadata or internal state
			try:
				extra_params = self._get_extra_params(cmd, data)
				print 'extra_params are', extra_params
			except KeyError:
				extra_params = []
			cmd[1].extend(extra_params)
			cmd_result = self.eval(cmd[0],cmd[1])
			if cmd_result != None and cmd_result != "":
				responses.append(cmd_result)
		print 'responses:', responses
		return responses

	def _generate_responses(self, data):
		"""
		Parses incoming messages, returns any responses bot needs to send.

		Returns a 2-tuple:
			Item 1) a list of responses to send
			Item 2) True if responses are chat messages,
					False otherwise (aka pongs)
			We use item 2 to sandbox chatter-sent messages to make sure
			they are never interpreted as anything other than private messages
			(i.e. don't allow any type of IRC injection but idk why someone
			would try that.)
		"""
		if 'type' not in data:
			return []
		else:
			msgtype = data['type']

		if msgtype == 'PING':
			return (['PONG :tmi.twitch.tv\n'.encode('utf-8')], False)
		elif msgtype == 'PRIVMSG':
			command_list = self.parser.translate(data['message'])

			return (self._do_commands(command_list, data),True)
		return ([],True)

	def eval(self, cmd, args):
		"""
		Run a single command.
		"""
		return cmd(*args)

	def process_msg(self):
		"""
		Removes next message from message queue and processes it.
		"""
		# print 'handler processing'
		if len(self.msg_q) > 1:
			# print 'queue nonempty'
			raw_msg = self.msg_q.pop(0)
			data = self._parse_raw_msg(raw_msg)
			return self._generate_responses(data)
		else:
			if self.verbose:
				print 'Nothing currently in message queue'
			return ([],True)

	def update_msg_queue(self, sockstream):
		"""
		Given recent socket data, parses data into individual messages and
		updates the queue of messages to be handled
		"""
		msgs = sockstream.split(self.delimeter)
		if len(msgs) > 0:
			# The first message gets appended onto the last queue item
			if msgs[0].startswith('\n') and self.msg_q[-1].endswith('\r'):
				# handle case where EOL delimeter was split between messages
				last_msg_len = len(self.msg_q[-1])
				self.msg_q[-1] = self.msg_1[-1][:last_msg_len-1]
				msgs[0] = msgs[0][1:]
			else:
				# 99.999% of cases
				self.msg_q[-1] += msgs[0]
			# Add all the other messages to the queue
			for msg in msgs[1:]:
				self.msg_q.append(msg)


# Message examples:
clearchat_ex = "@ban-reason=;room-id=77780959;target-user-id=236791797;tmi-sent-ts=1534813739972 :tmi.twitch.tv CLEARCHAT #toburr :decafsmurf\r\n" # single user clear
clearchat2_ex = "@room-id=77780959;tmi-sent-ts=1534835137593 :tmi.twitch.tv CLEARCHAT #toburr\r\n" # Whole chat clear
hosttarget_ex = ":tmi.twitch.tv HOSTTARGET #toburr :- 0\r\n"
join_ex = ":toburr!toburr@toburr.tmi.twitch.tv JOIN #toburr\r\n"
mode_ex = ":jtv MODE #toburr +o toburobo\r\n"
notice_ex = "@msg-id=host_target_went_offline :tmi.twitch.tv NOTICE #toburr :alittlelisa has gone offline. Exiting host mode.\r\n"
part_ex = ":toburr!toburr@toburr.tmi.twitch.tv PART #toburr\r\n"
ping_ex = "PING :tmi.twitch.tv\r\n"
privmsg_ex = "@badges=broadcaster/1,premium/1;color=#106F73;display-name=Toburr;emotes=;id=c17fbc52-e48c-4f6f-9e5d-be7ed47d7404;mod=0;room-id=77780959;subscriber=0;tmi-sent-ts=1534012954836;turbo=0;user-id=77780959;user-type= :toburr!toburr@toburr.tmi.twitch.tv PRIVMSG #toburr :5\r\n"
roomstate_ex = "@broadcaster-lang=;emote-only=0;followers-only=-1;r9k=0;rituals=0;room-id=77780959;slow=0;subs-only=0 :tmi.twitch.tv ROOMSTATE #toburr\r\n"
userstate_ex = "@badges=moderator/1;color=;display-name=toburobo;emote-sets=0;mod=1;subscriber=0;user-type=mod :tmi.twitch.tv USERSTATE #toburr\r\n"

#test = "@badge-info=;badges=moderator/1,premium/1;color=;display-name=toburobo;emotes=;flags=;id=de613730-b8b2-4048-b701-0fc4c3659b91;mod=1;room-id=77780959;subscriber=0;tmi-sent-ts=1556060247754;turbo=0;user-id=185295401;user-type=mod :toburobo!toburobo@toburobo.tmi.twitch.tv PRIVMSG #toburr :!settitle a b c d test\r\n"
#h = Handler()
#h.update_msg_queue(test)
#r = h.process_msg()
#for guy in r:
#	print guy
