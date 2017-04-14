import smtplib
import socket
import time

time.sleep(5)

ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1] 

to = 'auguste.colle@kuleuven.be'
gmail_user = 'rienausolutions@gmail.com'
gmail_pwd = 'rienenauguste'
smtpserver = smtplib.SMTP("smtp.gmail.com",587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_pwd)
header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:testing \n'
print header
msg = header + '\n ip address: '+str(ip)+' \n\n'
smtpserver.sendmail(gmail_user, to, msg)
print 'done!'
smtpserver.close()



