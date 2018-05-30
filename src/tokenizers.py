class Tokenizer:
	"""
	An interface for converting strings into collections of string tokens to be parsed.
	"""

	def tokenize(self, message):
		"""
		Given a string message, produces a list of tokens representing the message somehow.
		Intended to be defined by implementing subclasses.
		"""
		return None

class WhitespaceTokenizer(Tokenizer):
	"""
	A simple tokenizer that tokenizes by whitespace
	"""

	def tokenize(self, message):
		tokens = message.split()
		return tokens

