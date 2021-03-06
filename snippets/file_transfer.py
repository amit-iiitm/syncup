from ftplib import FTP

#initialize connection to ftp server
#connect to the domainname
#ftp=FTP('domainname.com')
ftp=FTP('ftp.debian.org')
#login with your credentials
#ftp.loginuser(user='username', passwd='password')

#here u can login without credentials
ftp.login()
#change to specific directory
#ftp.cwd('/specificdomain-or-location')
ftp.cwd('debian')

#list all files in the dirctory
print ftp.retrlines('LIST')

#function to grab and copy files from remote server to local machine
def grabFile():
	filename='fileName.txt'
	localfile=open(filename,'wb')
	ftp.retrbinary('RETR ' + filename, localfile.write, 1024) #retrive remote file, local file write handle, buffer size
	#once the copying is closed quit the connection
	ftp.quit()
	localfile.close()


#function to store the file at remote server
def placeFile():
	filename='fileName.txt'
	ftp.storbinary('STOR '+filename, open(filename,'rb'))
	ftp.quit()

def grab_demo():
	filename='README'
	localfile=open('README_debian','wb')
	ftp.retrbinary('RETR '+filename,localfile.write)
	ftp.quit()

grab_demo()
