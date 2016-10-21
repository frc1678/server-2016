import smtplib
import threading

emails = ['5307238454@tmomail.net']
gmail_user = 'abhi@vemulapati.com'

class EmailThread(threading.Thread):
	def reportServerCrash(self, message):
		smtpserver = smtplib.SMTP("smtp.gmail.com",587)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo()
		smtpserver.login(gmail_user, "espn589")
		header = 'To:' + ', '.join(emails) + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: Server Crash \n'
		msg = header + '\n' + message
		smtpserver.sendmail(gmail_user, emails, msg)
		smtpserver.close()

