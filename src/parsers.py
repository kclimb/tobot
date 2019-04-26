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

	def __init__(self, m = commands.DEFAULT_COMMANDS, a = commands.DEFAULT_ARGC, ma = commands.MIN_ARGC, t = tokenizers.WhitespaceTokenizer()):
		Parser.__init__(self, t)
		self.map = m
		self.argc = a
		self.min_argc = ma

	def _gettokens(self, message):
		"""
		Converts the string message to a token container via the tokenizer
		"""
		return self.tokenizer.tokenize(message)

	def _tokens_still_expected_error(commands):
		print 'ERROR: not enough args passed to last command'
		print 'Removing command from command list'
		commands.pop(len(commands)-1)
		return commands

	def _makecommandlist(self, tokens):
		"""
		Given a nonempty sequence of tokens, constructs an appropriate sequence of
		behaviors with respect to the token sequence
		"""
		commands = []
		commandset = set([])
		token_num = 0
		while token_num < len(tokens):
			# Stop if the message is trying to send too many commands (spam prevention)
			if USE_COMMAND_HARDCAP and len(commands) >= MAX_COMMANDS_PER_MESSAGE:
				return commands
			try:
				lowertoken = tokens[token_num].lower()
				command = self.map[lowertoken]
				if ALLOW_DUPLICATE_COMMANDS or lowertoken not in commandset:	# Don't allow users to spam the same command
					commands.append((command, []))
					commandset.add(lowertoken)
					expected_args = self.argc[lowertoken]
					# If a command is set to "infinity" expected args, that just
					# means the rest of the tokens are one big argument
					if expected_args == float('inf'):
						token_num += 1
						if len(tokens) - token_num > 0:
							commands[-1][1].append(tokens[token_num+1:]) # Note this is adding a single argument which is the remaining token list
							token_num = len(tokens) # Make sure we end the function after this
						else:
							return self._tokens_still_expected_error(commands)
					else: # Finite number of tokens expected
						while token_num < token_num + expected_args:
							token_num += 1
							if token_num >= len(tokens):
								return self._tokens_still_expected_error(commands)

							cur_token = tokens[token_num]
							append_arg = cur_token
							# Treat a sequence of tokens where the first starts with a " and the last ends with a " as a single token
							if append_arg.startswith('"'):
								while not append_arg.endswith('"'):
									append_arg = append_arg + " "
							commands[-1][1].append(append_arg)
			except KeyError:
				# In the event of a self.map KeyError, we're simply ignoring an
				# unknown token. For a self.argc KeyError, a command with no
				# specified argc is assumed to have 0 paramters.
					pass
			token_num += 1
			# We're expecting a parameter to the currently parsed command

		if expected_args > 0:
			cur_cmd = commands[-1][0]
			if cur_cmd in self.min_argc and self.min_argc[cur_cmd] + expected_args >= self.argc[cur_cmd]:
				pass
			else:
				print 'ERROR: not enough args passed to last command'
				print 'Removing command from command list'
				commands.pop(len(commands)-1)
		return commands

	def translate(self, message):
		return self._makecommandlist(self._gettokens(message))
