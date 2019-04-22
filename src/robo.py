import commandler as handler
import netclient as client
#import threading

class Robo:
	"""
	Manages all the business of the process (in contrast to any front-facing UI (for which currently there are no plans (but you never know, y'know?)))
	"""
	def __init__(self, netpass):
		self.running = False
		self.client = client.InsecureMyRCClient(netpass)
		self.handler = None

	def start(self):
		if not self.running:
			succ = self.client.connect() # Default method connects to toburr
			if succ:
				self.running = True
			else:
				print 'ERROR when starting robo :('
				self.running = False
		else:
			print "already running, can't start"

	def stop(self):
		self.running = False

	def send(self, message):
		if self.running:
			self.client.send(message)
		else:
			print "Robo not running. Can't send message."

	def recv(self):
		if self.running:
			return self.client.recv()
		else:
			print "Robo not running. Can't receive message."
		return ""

	def handle(self, message):
		if m.startswith('PING :tmi.twitch.tv'):
			self.client.pong()
			return "pong"
		elif m.endswith('ctrlc\r\n'):
			return "STOP"
		return ""

	def isrunning(self):
		return self.running

# r = Robo()
# r.handler = handler.Handler()
# r.handler.handle('toburobo: !hi')
#print threading.active_count()
