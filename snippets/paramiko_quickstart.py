import paramiko

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#connect with the local ssh with admin password and username of the system
ssh.connect('127.0.0.1', username='amit', password='amit48')

#see the contents of etc folder
stdin,stdout,stderr = ssh.exec_command("ls /etc/")
for line in stdout.readlines():
	print line.strip()

#open a secureftp connection and list tmp contents
sftp=ssh.open_sftp()
sftp.chdir("/tmp/")
print sftp.listdir()

stdin, stdout, stderr=ssh.exec_command("uptime")
type(stdin)

print stdout.readlines()


#ftp file transfer using ssh
ftp=ssh.open_sftp()
ftp.get('localfile.py','remotefile.py')
ftp.close()
ssh.close()


