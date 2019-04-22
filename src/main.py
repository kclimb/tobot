import robo as robo
import sys

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
	r.send('hi from main')
	handle_result = ""
	while handle_result != "STOP":
		m = r.recv()
		handle_result = r.handle(m)

if __name__ == "__main__":
    main()
