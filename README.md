#Syncup
Automatically synchronize local folder with a remote one, uses sftp connection over ssh to transfer files and folders.
Script monitors the local folder and emit an event whenever a new file is created or a file is modified or if a file/folder is deleted.

#Satisfying requirements
uses python's paramiko for ssh connection and watchdog module for monitoring changes in a folder
all the requirements have been specified in requirements.txt
To install all required modules use "pip install -r requirements.txt" 

#Configuration
file syncup.cfg.dst contains all configurations of remote address, ssh key file address, remote username,password, local_root and remote_root to synchronize.
remote_host: 'addr_remote_computer'
remote_username: 'remote_username'
private_key_file: 'path_to_ssh_keyfile'
remote_password: 'remote_login_password'
remote_root_path: 'path_to_remote_folder'
local_root_path: 'path_to_local_folder'

folder:permission_script has
change_permission.sh :- to change the permissions of local filesystem so that it can be accessed via the network
run_chmod.sh :- python script to run above 
You need to put these files in a place which is above or equal to the directory local_root_path in file system so that it can change permission of all files and folders.
Also change the behaviour of change_permission.sh so that it can run without asking for sudo password everytime by modifying '/etc/sudoers.tmp'
using following steps:
	1. type 'sudo visudo' in terminal
	2. now add a line 'user ALL=(ALL) NOPASSWD: /home/user/change_permission.sh' below the line '%sudo   ALL=(ALL:ALL) ALL' in that file
	3. this will enable change_permission.sh script to run without asking sudo password everytime.

#Deployment
Open two terminals:
1. Navigate to the sync_folders and run '__init__.py', this will show a message that any changes made to your local_root shall be reflected to remote_root
2. In the other terminal run the file 'run_chmod.py' by first navigating to its appropriate location


The changes should be propagated within 10-20 seconds based upon the volume of changes 
