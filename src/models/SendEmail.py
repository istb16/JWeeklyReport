# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.api import mail

class SendMail:
	#
	# Reporter追加確認メール
	#
	@classmethod
	def confReporter(self, to, orgKey, orgName):
		user = users.get_current_user()
		if user:
			mail.send_mail(
				sender = user.email(),
				to = to,
				subject = 'Confirmation for add Reporter in Weekly Report System',
				body = '''TO: %(email)s

You has been required to register as a Reporter in Weekly Report System.
The registered organization is %(orgName)s.
You can now visit http://jweeklyreport.appspot.com/User/ConfReporter/%(orgKey)s and sign in using your Google Account to get new access permission.
'''
					% {'email': to, 'orgKey': orgKey, 'orgName': orgName})

	#
	# Receiver追加確認メール
	#
	@classmethod
	def confReceiver(self, to, orgKey, orgName):
		user = users.get_current_user()
		if user:
			mail.send_mail(
				sender = user.email(),
				to = to,
				subject = 'Confirmation for add Receiver in Weekly Report System',
				body = '''TO: %(email)s

You has been required to register as a Receiver in Weekly Report System.
The registered organization is %(orgName)s.
You can now visit http://jweeklyreport.appspot.com/User/ConfReceiver/%(orgKey)s and sign in using your Google Account to get new access permission.
''' % {'email': to, 'orgKey': orgKey, 'orgName': orgName})

	#
	# Administrator追加確認メール
	#
	@classmethod
	def confAdminer(self, to, orgKey, orgName):
		user = users.get_current_user()
		if user:
			mail.send_mail(
				sender = user.email(),
				to = to,
				subject = 'Confirmation for add Administrator in Weekly Report System',
				body = '''TO: %(email)s

You has been required to register as a Administrator in Weekly Report System.
The registered organization is %(orgName)s.
You can now visit http://jweeklyreport.appspot.com/User/ConfAdminer/%(orgKey)s and sign in using your Google Account to get new access permission.
''' % {'email': to, 'orgKey': orgKey, 'orgName': orgName})

	#
	# 受信レポート通知メール
	#
	@classmethod
	def receiveReport(self, to, rpt, rptCal):
		user = users.get_current_user()
		if user:
			rptCal['start'] = rptCal['start'].strftime('%Y-%m-%d')
			rptCal['end'] = rptCal['end'].strftime('%Y/%m/%d')
			mail.send_mail(
				sender = user.email(),
				to = to,
				subject = 'Weekly Report: %(userName)s %(periodStart)s - %(periodEnd)s [%(orgName)s]' % {'userName': rpt.user.author.nickname(), 'periodStart': rptCal['start'], 'periodEnd':rptCal['end'], 'orgName': rpt.organization.name},
				body = '''%(content)s
----------------------------------------------------------------------
http://jweeklyreport.appspot.com/Report/%(rptKey)s
from JWeekly Report''' % {'rptKey': rpt.key(), 'periodStart': rptCal['start'], 'periodEnd': rptCal['end'], 'content': rpt.content})