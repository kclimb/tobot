import robo as robo
import sys
import time

SERV_HOST_NAME = 'irc.chat.twitch.tv'
privmsg_ex = "@badges=broadcaster/1,premium/1;color=#106F73;display-name=Toburr;emotes=;id=c17fbc52-e48c-4f6f-9e5d-be7ed47d7404;mod=0;room-id=77780959;subscriber=0;tmi-sent-ts=1534012954836;turbo=0;user-id=77780959;user-type= :toburr!toburr@toburr.tmi.twitch.tv PRIVMSG #toburr :The quick brown fox jumped over the lazy dogs.\r\n"

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
		while r.process() > 0:  # Process messages til none are left
			pass

if __name__ == "__main__":
    main()
