import commands as commands
import tokenizers as tokenizers

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

	def _makecommandlist(self, tokens):
		"""
		Given a nonempty sequence of tokens, constructs an appropriate sequence of
		behaviors with respect to the token sequence
		"""
		commands = []
		expected_args = 0
		for token in tokens:
			# We're expecting a command signal
			if expected_args == 0:
				try:
					command = self.map[token.lower()]
					commands.append((command, []))
					expected_args += self.argc[token.lower()]
				except KeyError:
					# In the event of a self.map KeyError, we're simply ignoring an
					# unknown token. For a self.argc KeyError, a command with no
					# specified argc is assumed to have 0 paramters.
					pass

			# We're expecting a parameter to the currently parsed command
			else:
				commands[-1][1].append(token)
				expected_args -= 1
		if expected_args > 0:
			print 'ERROR: not enough args passed to last command'
			print 'Removing command from command list'
			commands.pop(len(commands)-1)
		return commands

	def translate(self, message):
		cmdlist = self._makecommandlist(self._gettokens(message))
		responses = []
		for cmd in cmdlist:
			cmd_result = cmd[0](*(cmd[1]))
			if cmd_result != None and cmd_result != "":
				responses.append(cmd_result)
		return responses
