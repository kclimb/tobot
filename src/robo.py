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
		succ = self.client.connect()
		if succ:
			self.running = True
		else:
			print 'ERROR when starting robo :('

	def stop(self):
		self.running = False

	def send(self, message):
		self.client.send(message)

	def recv(self):
		return self.client.recv()

	def isrunning(self):
		return self.running

# r = Robo()
# r.handler = handler.Handler()
# r.handler.handle('toburobo: !hi')
#print threading.active_count()