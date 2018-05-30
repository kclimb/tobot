import commands as commands
import parsers as parsers

class Handler:

	def __init__(self, p = parsers.MapParser()):
		self.parser = p

	def eval(self, cmd, args):
		return cmd(*args)

	def handle(self, message):
		cmds = self.parser.translate(message)
		for cmd in cmds:
			print 'Handler says', cmd
			print self.eval(cmd[0], cmd[1])