import robo as robo
import sys
import time

SERV_HOST_NAME = 'irc.chat.twitch.tv'

def main():
	args = sys.argv
	print args
	if len(args) <= 1:
		f = open('mydata.txt')
		opass = f.read()
	else:
		opass = args[1]
	r = robo.Robo(opass)
	r.start()
	r.send('hi :)')
	while True:
		if r.recv() == -1:      # Wait for incoming data
			break
		if not r.client.is_connected: # If we disconnect while reading data, try rebooting
			print "Client was disconnected. Attempting to reboot..."
			r.stop()
			r.start()
			continue
		r.process()  # Process messages til none are left

if __name__ == "__main__":
    main()
