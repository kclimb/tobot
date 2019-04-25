import commands as commands
import tokenizers as tokenizers

MAX_COMMANDS_PER_MESSAGE = 5
USE_COMMAND_HARDCAP = True

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

	def _makecommandlist(self, tokens):
		"""
		Given a nonempty sequence of tokens, constructs an appropriate sequence of
		behaviors with respect to the token sequence
		"""
		commands = []
		commandset = set([])
		expected_args = 0
		for token in tokens:
			# We're expecting a command signal
			if expected_args == 0:
				# Stop if the message is trying to send too many commands (spam prevention)
				if USE_COMMAND_HARDCAP and len(commands) >= MAX_COMMANDS_PER_MESSAGE:
					return commands
				try:
					lowertoken = token.lower()
					command = self.map[lowertoken]
					if lowertoken not in commandset:	# Don't allow users to spam the same command
						commands.append((command, []))
						commandset.add(lowertoken)
						expected_args += self.argc[lowertoken]
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
