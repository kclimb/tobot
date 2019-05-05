import commands as commands
import tokenizers as tokenizers

MAX_COMMANDS_PER_MESSAGE = 5
USE_COMMAND_HARDCAP = True
ALLOW_DUPLICATE_COMMANDS = True

class Parser:

	def __init__(self, t = tokenizers.WhitespaceTokenizer()):
		"""
		Initializes a parser.
		The parameter 't' must be an object whose type implements Tokenizer.
		"""
		self.tokenizer = t

	def translate(self, message):
		"""
		Given a string message, produces an iterable container of actions to perform.
		Intended to be defined by implementing subclasses
		"""
		return None

class MapParser(Parser):
	"""
	An implementing class of parser that uses a map to translate token keys to
	behavioral (function object) values
	"""

	def __init__(self, m = commands.DEFAULT_COMMANDS, a = commands.DEFAULT_ARGC, t = tokenizers.WhitespaceTokenizer()):
		Parser.__init__(self, t)
		self.map = m
		self.argc = a

	def _gettokens(self, message):
		"""
		Converts the string message to a token container via the tokenizer
		"""
		return self.tokenizer.tokenize(message)

	def _parsing_error(self, commands, errorcmd):
		"""
		Tells the bot to print an error message due to an error parsing
		a command.

		"commands" - the currently parsed command list
		"errorcmd" - a 2-tuple:
			errorcmd[0] = the command function to run
			errorcmd[1] = a list of parameters to errorcmd[0]
		"""
		print 'ERROR: not enough args passed to last command'
		print 'Removing command from command list'
		commands[-1] = errorcmd
		return commands

	def _makecommandlist(self, tokens):
		"""
		Given a nonempty sequence of tokens, constructs an appropriate sequence of
		behaviors with respect to the token sequence
		"""
		cmnds = []
		commandset = set([])
		token_num = 0
		while token_num < len(tokens):
			# Stop if the message is trying to send too many commands (spam prevention)
			if USE_COMMAND_HARDCAP and len(cmnds) >= MAX_COMMANDS_PER_MESSAGE:
				return cmnds
			try:
				lowertoken = tokens[token_num].lower()
				command = self.map[lowertoken]
				if ALLOW_DUPLICATE_COMMANDS or lowertoken not in commandset:	# Don't allow users to spam the same command
					cmnds.append((command, []))
					commandset.add(lowertoken)
					try:
						expected_args = self.argc[lowertoken]
					except KeyError:
						# If we don't have a defined number of params, assume 0
						expected_args = 0
					# If a command is set to "infinity" expected args, that just
					# means the rest of the tokens are one big argument
					if expected_args == float('inf'):
						token_num += 1
						if len(tokens) - token_num > 0:
							cmnds[-1][1].append(tokens[token_num+1:]) # Note this is adding a single argument which is the remaining token list
							token_num = len(tokens) # Make sure we end the function after this
						else:
							return self._parsing_error(cmnds, (commands.missing_token_error, ['one or more','0']))
					else: # Finite number of tokens expected
						stop_num = token_num + expected_args
						while token_num < stop_num:
							token_num += 1
							if token_num >= len(tokens):
								return self._parsing_error(cmnds, (commands.missing_token_error, [str(expected_args),str(expected_args-(stop_num-token_num)-1)]))

							cur_token = tokens[token_num]
							append_arg = cur_token
							# Treat a sequence of tokens where the first starts with a " and the last ends with a " as a single token
							if append_arg.startswith('"'):
								append_arg = append_arg[1:]
								while not append_arg.endswith('"'):
									token_num += 1
									stop_num += 1 # Since each of these tokens doesn't count against our total parameters,
												  # we need to push back the stop num
									if token_num >= len(tokens):
										print 'No endquote token found'
										return self._parsing_error(cmnds, (commands.missing_end_quote_error, []))
									append_arg = append_arg + " " + tokens[token_num]
								append_arg = append_arg.rstrip('"')
							cmnds[-1][1].append(append_arg)
			except KeyError:
				# In the event of a self.map KeyError, we either:
				#	1) Have a dynamically defined command (in which case we run
				#	   doTextCommand with the token as an arg), or
				#	2) We're simply ignoring an unknown token.
				if commands.isTextCommand(lowertoken):
					cmnds.append((commands.doTextCommand, [lowertoken]))

			token_num += 1

		return cmnds

	def translate(self, message):
		return self._makecommandlist(self._gettokens(message))
