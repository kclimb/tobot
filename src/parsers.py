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

# A default map of supported commands, and the corresponding number of arguments for
# each command.
DEFAULT_COMMANDS = {'!hi': commands.sayhi}
DEFAULT_ARGC = {'!hi': 0}

class MapParser(Parser):
	"""
	An implementing class of parser that uses a map to translate token keys to
	behavioral (function object) values
	"""
	
	def __init__(self, m = DEFAULT_COMMANDS, a = DEFAULT_ARGC, t = tokenizers.WhitespaceTokenizer()):
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
		name = tokens[0]
		for token in tokens[1:]:

			# We're expecting a command signal
			if expected_args == 0:
				try:
					command = self.map[token]
					commands.append((command, [name]))
					expected_args += self.argc[token]
				except KeyError:
					# In the event of a self.map KeyError, we're simply ignoring an
					# unknown token. For a self.argc KeyError, a command with no
					# specified argc is assumed to have 0 paramters.
					pass

			# We're expecting a parameter to the currently parsed command
			else:
				commands[-1][1].append(token)
				expected_args -= 1
		return commands

	def translate(self, message):
		return self._makecommandlist(self._gettokens(message))
