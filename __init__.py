import sys
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import *
import paramiko
import argparse
import getpass
import posixpath
import pysftp
from config import Config

logFormat='%(levelname)s: %(message)s'
logging.basicConfig(format=logFormat)
logger=logging.getLogger('syncup')
logger.setLevel(logging.INFO)

class syncWatchdog(PatternMatchingEventHandler):
	#watchdog event handler to trigger actions on remote servers based on events fired due to local filesystem change
	
	#constructor
	def __init__(self,remote_control,**kw):
		super(syncWatchdog,self).__init__(**kw)
		self._remote_control=remote_control

	#on file create event handler
	def on_created(self,event):
		#check if the event is of a directory creation, if yes ignore it as directory will automatically created bt transfer_file()
		if isinstance(event,DirCreatedEvent):
			logger.debug('Ignoring DirCreatedEvent for %s', event.src_path)
		else:
			self._remote_control.transfer_file(event.src_path)
			

	#on file delete event handler
	def on_deleted(self,event):
		self._remote_control.delete_resource(event.src_path)
		
	
	#on file modified event handler
	def on_modified(self,event):
		#check of the event is directory modified event then ignore it
		if isinstance(event, DirModifiedEvent):
			logger.debug('Ignoring DirModifiedEvent for %s' % event.src_path)
		else:
			self._remote_control.transfer_file(event.src_path)
			
	#on file moved event handler
	def on_moved(self,event):
		self._remote_control.move_resource(event.src_path, event.dest_path)
		

#remote control class defines methods to deal with data
class RemoteControl:
	"""
	performs filesystem manipulations on a remote server, using data from the local machine's filesystem as necessary"""
	def __init__(self,sftp_connection,local_base, remote_base):
		self._connection=sftp_connection.connection
		self._ssh_prefix=sftp_connection.ssh_prefix
		self._local_base=local_base
		self._remote_base=remote_base
		self._local_base_length=len(local_base)

	#given a full canonical path on the local filesystem, returns an equivalent full canonical path on the remote filesystem
	def get_remote_path(self,local_path):
		#strip the local base path from the local full canonical path to get the relative path
		remote_relative=local_path[self._local_base_length:]
		return self._remote_base+remote_relative

	#function to transfer new files to remote
	def transfer_file(self,src_path):
		dest_path=self.get_remote_path(src_path)
		logger.info('Copying\n\t%s\nto\n\t%s: %s' % (src_path,self._ssh_prefix,dest_path))
		try:
			#make sure the intermediate destination path to this file actually exists on the remote machine
			self._connection.execute('mkdir -p "'+ os.path.split(dest_path)[0] + '"')
			# above command make all parent directories to the current path if they dont exist, otherwise make only the current directory
			print "printing the source path ", src_path
			print "printing the destn path ", dest_path
			#put command transfers the file to remote site
			self._connection.put(src_path,dest_path)
			
		except Exception as e:
			logger.error('Caught exception while copying')
			logger.exception(e)

	#function to delete files from remote
	def delete_resource(self,src_path):
		dest_path=self.get_remote_path(src_path)
		logger.info('Deleting %s:%s' %(self._ssh_prefix,dest_path))
		try:
			self._connection.execute('rm -rf "' + dest_path + '"')
		except Exception as e:
			logger.error('Caught exception while deleting:')
			logger.exception(e)
	
	#function to move resources
	def move_resource(self,src_path,dest_path):
		logger.info('Moving\n\t%s:%s\nto\n\t%s:%s'%(self._ssh_prefix, self.get_remote_path(src_path), self._ssh_prefix, self.get_remote_path(dest_path)))
		try:
			#make sure the intermediate destination path to this file actually exists on the remote machine
			self._connection.execute('mkdir -p "' + os.path.split(dest_path)[0] + '"')
			self._connection.execute('mv "' + src_path + '" "' + dest_path + '"')
		except Exception as e:
			logger.error('Caught exception while moving:')
			logger.exception(e)


#class to encapsulate the sftp connection
class SFTPConnection:
	"""maintain an ssh connection to remote server via pysftp"""
	
	def __init__(self, host, port=None, private_key_file=None, private_key_password=None, username=None, password=None):
		self._ssh_prefix=None
		self._connection=None
		
		#if username is not set demand for it
		if username=='':
			#getting the username of the account with which script is being executed
			username=getpass.getuser()
			logger.debug('no username configured; assuming username %s' % username)
		else:
			logger.debug('Using configured username %s' % username)
	
		self._ssh_prefix='%s@%s' % (username,host)
	
		#attempt key authentication if no password was specified; prompt for a password if fails
		if password=='':
			try:
				logger.debug('No password specified, attempting to use key authentication')
				self._connection=pysftp.Connection(host,port=port, username=username, private_key=private_key_file, private_key_pass=private_key_password)
			except Exception as e:
				logger.debug('key authentication failed. \nCause: %s\nFalling back to password authentication...' % e)
				password=getpass.getpass('Password for %s: ' % self._ssh_prefix)
		else:
			logger.debug('Using configured password')
	
		#if we dont have a connection yet, attempt password authentication
		
		if self._connection is None:
			try:
				self._connection=pysftp.Connection(host,port=port,username=username,password=password)
			except Exception as e:
				logger.error('Could not successfully connect to %s\nCause: %s' % (self._ssh_prefix, e))
				sys.exit(1)
		
		logger.debug('successfully connected to %s' % self._ssh_prefix)
	

	@property
	def ssh_prefix(self):
		"""string containing the username and host information for the remote server"""
		return self._ssh_prefix

	@property
	def connection(self):
		"""a pysftp connection object representing the active connection to the remote server"""
		return self._connection



#main function

def _main():
	parser=argparse.ArgumentParser(description='Reflect local filesystem changes on a remote system in real time, automatically.')
	parser.add_argument('-c','--config-file', default='syncup.cfg.dist',help='location of syncup configuration file')
	args=parser.parse_args()
	
	try:
		config_file=file(args.config_file)
	except Exception as e:
		logger.error('Couldnt read syncup configuration file!\n Either place the syncup.cfg file in the same folder as this script or specify the full path.\n Run \'%s -h\' for usage information.\nCause: %s' % (os.path.basename(__file__), e))
		sys.exit()


	try:
		cfg=Config(config_file)
	except Exception as e:
		logger.error('syncup configuration file is invalid!\nCause: %s' % e)
		sys.exit(1)
	
	#read configuration 
	local_root_path=os.path.abspath(os.path.expanduser(cfg.local_root_path))
	#if the configured path is not a directory we cant sync it
	if not os.path.isdir(local_root_path):
		logger.error('invalid local_root_path confgured: %s is not valid path on the local machine' % cfg.local_root_path)
		sys.exit(1)
	
	else:
		logger.debug('using local root path: '+ local_root_path)

	#create persistant SSH connection to remote server
	sftp_connection=SFTPConnection(cfg.remote_host,cfg.remote_port,cfg.private_key_file, cfg.private_key_password,cfg.remote_username,cfg.remote_password)
	
	logger.debug('Using local root path: '+ local_root_path)
	
	no_valid_mappings=True #if this is still true when the loop below completes, no valid mappings are configured

	observer=Observer()

	for mapping in cfg.path_mappings:
		#create an absolute local path from the local root path and this mapping's local relative path
		local_base=os.path.join(local_root_path,mapping.local)
		if not os.path.isdir(local_base):
			logger.warn('invalid path mapping configured: %s is not a valid path on the local machine' % local_base)
			continue
		#if we have got this far, we have at least one valid mapping
		no_valid_mappings=False

		#create an absolute remote path from the remote root path and this mapping's remote relative path
		#use explicit posixpath.join since the remote server will always use UNIX-style paths for sftp
		remote_base=posixpath.join(cfg.remote_root_path,mapping.remote)
		
		logger.info('Path mapping initializing:\nChanges at local path\n\t%s\nwill be reflected at remote path\n\t%s:%s'% (local_base,sftp_connection.ssh_prefix,remote_base))
		
		#create necessary objects for this particular mapping and schedule this mapping on the Watchdog observer as appropriate
		remote_control=RemoteControl(sftp_connection=sftp_connection,local_base=local_base,remote_base=remote_base,)
		event_handler=syncWatchdog(ignore_patterns=cfg.ignore_patterns, remote_control=remote_control)
		observer.schedule(event_handler,path=local_base,recursive=True)
		
	if no_valid_mappings:
		logger.error('No valid path mappings were configured, so there is nothing to sync')
		sys.exit('Terminating.')

	
	#if at least one valid mapping is found, start the watchdog observer
	observer.start()
	
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()



if __name__=="__main__":
	_main()

	








		
		

