import commandler as handler
#import threading

class Robo:
	"""
	Manages all the business of the process (in contrast to any front-facing UI)
	"""
	def __init__(self, servname = None):
		self.hostname = servname # TODO: Move to netclient
		self.running = False
		self.client = None
		self.handler = None

	def start(self):
		self.running = True

	def stop(self):
		self.running = False

	def isrunning(self):
		return self.running

	# TODO: Move to netclient
	def gethostname(self):
		return self.hostname

	# TODO: Move to netclient
	def sethostname(self, newname):
		if self.running:
			# TODO: Raise "Bot is running" exception instead
			e = "Error: could not change hostname because Toburobo is already connected to a server."
			e += '\nPlease disconnect from the current server to change the hostname.'
			print e
		else:
			self.hostname = newname

r = Robo()
r.handler = handler.Handler()
r.handler.handle('toburobo: !hi')
#print threading.active_count()