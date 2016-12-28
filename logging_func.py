import logging
import urllib2
#1 debug- detailed info
#2 info- confirmation that things according to plan
#3 warning- something unexpected
#4 error- some function failed
#5 critical- something failed application must close

logging.basicConfig(filename='logfile.log',level=logging.DEBUG)

def main():
	try:
		logging.debug("we are in the main try loop")
		#mathFail=1/0
		if 1<2:
			logging.debug("entered into the first if statement")
			print "hello"
			
			try:
				urllib2.urlopen("http://www.google.com").read()
			except Exception, e:
				logging.error('urllib2 url visit failed, for the reason of %s' % str(e))
		else:
			logging.debug("entered into the first else statement")
			print "yo"
	except Exception, e:
		logging.critical(str(e))


main()
