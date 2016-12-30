import os
import time
import sys
try:
	while True:
		time.sleep(0.1)
		os.system('sudo /home/amit/change_permission.sh')
except KeyboardInterrupt:
	sys.exit(1)
	
