import commandler as handler
import netclient as client
#import threading

#RAW_PREFIXES = {'PING': client.pong, ':': _joinpart}

class Robo:
	"""
	Manages all the business of the process (in contrast to any front-facing UI (for which currently there are no plans (but you never know, y'know?)))
	"""
	def __init__(self, netpass, ):
		self.running = False
		self.client = client.InsecureMyRCClient(netpass)
		self.handler = handler.Handler()

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

	def send(self, message, isprivmsg=True):
		if self.running:
			self.client.send_message(message, isprivmsg)
		else:
			print "Robo not running. Can't send message."

	def recv(self):
		if self.running:
			data = self.client.recv()
			print 'Literal socket data:\n', repr(data), '\n'
			if 'ctrlc' in data and 'badges=broadcaster' in data[:data.index(' ')]:
				return -1
			self.handler.update_msg_queue(data)
		else:
			print "Robo not running. Can't receive message."
		return ""

	def process(self):
		# print 'robo processing'
		responses,isprivmsg = self.handler.process_msg()
		sendcount = 0
		for resp in responses:
			self.send(resp, isprivmsg)
			sendcount += 1
		if sendcount == 0:
			print 'No more messages to process'
		return sendcount

	def isrunning(self):
		return self.running

# r = Robo()
# r.handler = handler.Handler()
# r.handler.handle('toburobo: !hi')
#print threading.active_count()
