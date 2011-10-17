# -*- coding: utf-8 -*-

import cgi
import os
import datetime
import controllers
import models
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import memcache

class Organization(controllers.LoginedBase):
	def __init__(self):
		controllers.LoginedBase.__init__(self)

	def get(self, key=None):
		org = models.Organization.get(key)

		# アクセス制限
		accessType = self.getAccessTypeOrganization(org)
		if not self.haveReadAccessOrganization(org, accessType):
			self.error(403)
			return

		orgReporters = []
		for userKey in org.reporters:
			orgReporters.append(models.User.get(userKey).author.nickname())
		orgReceivers = []
		for userKey in org.receivers:
			orgReceivers.append(models.User.get(userKey).author.nickname())
		orgAdminers = []
		for userKey in org.adminers:
			orgAdminers.append(models.User.get(userKey).author.nickname())

		self.render('views/organization/index.html', {
			'orgKey': org.key(),
			'orgName': org.name,
			'orgReportTemplate': org.reportTemplate,
			'orgReporterWaitings': org.reporterWaitings,
			'orgReceiverWaitings': org.receiverWaitings,
			'orgAdminerWaitings': org.adminerWaitings,
			'orgReporters': orgReporters,
			'orgReceivers': orgReceivers,
			'orgAdminers': orgAdminers,
			'accessType': accessType,
		})

	def convUserNickname(self, userKeys):
		rtValues = []
		for userKey in userKeys:
			rtValues.append(models.User.get(userKey).author.nickname())
		return rtValues

	def convUsers(self, userKeys):
		rtValues = []
		for userKey in userKeys:
			user = models.User.get(userKey).author
			rtValues.append({
				'key': userKey,
				'name': user.nickname(),
			})
		return rtValues

class OrganizationAdd(Organization):
	def get(self):
		# アクセス制限
		if not self.haveFullAccessOrganization(None):
			self.error(403)
			return

		orgAdminers = []
		orgAdminers.append(self.loginUser.author.nickname())

		self.render('views/organization/add.html', {
			'orgAdminers': orgAdminers,
		})

	def post(self):
		# アクセス制限
		if not self.haveFullAccessOrganization(None):
			self.error(403)
			return

		name = self.request.get('name')
		reportTemplate = self.request.get('reportTemplate')
		reporterWaitings = self.request.get_all('reporterWaitings')
		receiverWaitings = self.request.get_all('receiverWaitings')
		adminerWaitings = self.request.get_all('adminerWaitings')

		# データチェック
		validErrors = []
		for email in reporterWaitings:
			if not mail.is_email_valid(email):
				validErrors.append({
					'title': 'Email invalid!',
					'message': mail.invalid_email_reason(email, 'Reporter Waitings'),
				})
		for email in receiverWaitings:
			if not mail.is_email_valid(email):
				validErrors.append({
					'title': 'Email invalid!',
					'message': mail.invalid_email_reason(email, 'Receiver Waitings'),
				})
		for email in adminerWaitings:
			if not mail.is_email_valid(email):
				validErrors.append({
					'title': 'Email invalid!',
					'message': mail.invalid_email_reason(email, 'Administrator Waitings'),
				})

		if len(validErrors) == 0:
			# データ保存
			org = models.Organization(
				name = name,
				adminers = [self.loginUser.key(), ],
				reportTemplate = reportTemplate,
				reporterWaitings = reporterWaitings,
				receiverWaitings = receiverWaitings,
				adminerWaitings = adminerWaitings,
			)
			org.put()

			# メール送信
			for email in reporterWaitings:
				models.SendMail.confReporter(email, org.key(), name)
			for email in receiverWaitings:
				models.SendMail.confReceiver(email, org.key(), name)
			for email in adminerWaitings:
				models.SendMail.confAdminer(email, org.key(), name)

			self.loginUser.adminOrganizations.append(org.key())
			self.loginUser.put()
			memcache.delete("loginUser")

			msg = models.Message(
				user = self.loginUser.author,
				title = 'Well done!',
				message = 'You have successfully saved data',
			)
			msg.put()

			self.redirect('/Organization/' + str(org.key()))
		else:
			for error in validErrors:
				msg = models.Message(
					user = self.loginUser.author,
					title = error['title'],
					message = error['message'],
				)
				msg.put()

class OrganizationEdit(Organization):
	def get(self, key=None):
		org = models.Organization.get(key)

		# アクセス制限
		if not self.haveFullAccessOrganization(org):
			self.error(403)
			return

		self.render('views/organization/edit.html', {
			'orgKey': org.key(),
			'orgName': org.name,
			'orgReportTemplate': org.reportTemplate,
			'orgReporterWaitings': org.reporterWaitings,
			'orgReceiverWaitings': org.receiverWaitings,
			'orgAdminerWaitings': org.adminerWaitings,
			'orgReporters': self.convUsers(org.reporters),
			'orgReceivers': self.convUsers(org.receivers),
			'orgAdminers': self.convUsers(org.adminers),
			'userKey': self.loginUser.key(),
		})

	def post(self, key=None):
		org = models.Organization.get(key)

		# アクセス制限
		if not self.haveFullAccessOrganization(None):
			self.error(403)
			return

		name = self.request.get('name')
		reportTemplate = self.request.get('reportTemplate')
		reportersDisabled = self.request.get_all('reportersDisabled')
		receiversDisabled = self.request.get_all('receiversDisabled')
		adminersDisabled = self.request.get_all('adminersDisabled')
		reporterWaitings = self.request.get_all('reporterWaitings')
		receiverWaitings = self.request.get_all('receiverWaitings')
		adminerWaitings = self.request.get_all('adminerWaitings')

		# データチェック
		validErrors = []
		for email in reporterWaitings:
			if not mail.is_email_valid(email):
				validErrors.append({
					'title': 'Email invalid!',
					'message': mail.invalid_email_reason(email, 'Reporter Waitings'),
				})
		for email in receiverWaitings:
			if not mail.is_email_valid(email):
				validErrors.append({
					'title': 'Email invalid!',
					'message': mail.invalid_email_reason(email, 'Receiver Waitings'),
				})
		for email in adminerWaitings:
			if not mail.is_email_valid(email):
				validErrors.append({
					'title': 'Email invalid!',
					'message': mail.invalid_email_reason(email, 'Administrator Waitings'),
				})

		if len(validErrors) == 0:
			# メール送信
			for email in reporterWaitings:
				if org.reporterWaitings.count(email) == 0:
					models.SendMail.confReporter(email, key, name)
			for email in receiverWaitings:
				if org.receiverWaitings.count(email) == 0:
					models.SendMail.confReceiver(email, key, name)
			for email in adminerWaitings:
				if org.adminerWaitings.count(email) == 0:
					models.SendMail.confAdminer(email, key, name)

			# データ更新
			org.name = name
			org.reportTemplate = reportTemplate
			org.reporterWaitings = reporterWaitings
			org.receiverWaitings = receiverWaitings
			org.adminerWaitings = adminerWaitings
			for userDisabled in reportersDisabled:
				if len(userDisabled) > 0:
					userDisabled = models.db.Key(userDisabled)
					while userDisabled in org.reporters: org.reporters.remove(userDisabled)

					u = models.User.get(userDisabled)
					while org.key() in u.reportOrganizations: u.reportOrganizations.remove(org.key())
					u.put()
			for userDisabled in receiversDisabled:
				if len(userDisabled) > 0:
					userDisabled = models.db.Key(userDisabled)
					while userDisabled in org.receivers: org.receivers.remove(userDisabled)

					u = models.User.get(userDisabled)
					while org.key() in u.receiveOrganizations: u.receiveOrganizations.remove(org.key())
					u.put()
			for userDisabled in adminersDisabled:
				if len(userDisabled) > 0:
					userDisabled = models.db.Key(userDisabled)
					while userDisabled in org.adminers: org.adminers.remove(userDisabled)

					u = models.User.get(userDisabled)
					while org.key() in u.adminOrganizations: u.adminOrganizations.remove(org.key())
					u.put()
			memcache.delete("loginUser")

			org.put()

			msg = models.Message(
				user = self.loginUser.author,
				title = 'Well done!',
				message = 'You have successfully saved data',
			)
			msg.put()

			self.redirect('/Organization/edit/' + str(org.key()))
		else:
			for error in validErrors:
				msg = models.Message(
					user = self.loginUser.author,
					title = error['title'],
					message = error['message'],
				)
				msg.put()

class OrganizationDelete(Organization):
	def get(self, key=None):
		org = models.Organization.get(key)

		# アクセス制限
		if not self.haveFullAccessOrganization(None):
			self.error(403)
			return

		key = org.key()

		for uKey in org.reporters:
			user = models.User.get(uKey)
			while key in user.reportOrganizations: user.reportOrganizations.remove(key)
			user.put()

		for uKey in org.receivers:
			user = models.User.get(uKey)
			while key in user.receiveOrganizations: user.receiveOrganizations.remove(key)
			user.put()

		for uKey in org.adminers:
			user = models.User.get(uKey)
			while key in user.adminOrganizations: user.adminOrganizations.remove(key)
			user.put()
		memcache.delete("loginUser")


		rpts = models.Report.all().filter('organization =', org)
		while rpts.count(limit=1) > 0:
			for rpt in rpts.fetch(limit=10):
				rpt.delete()

		org.delete()

		msg = models.Message(
			user = self.loginUser.author,
			title = 'Well done!',
			message = 'You have successfully delete data',
		)
		msg.put()

		self.redirect('/Organization')

class OrganizationList(Organization):
	def get(self):
		user = self.loginUser
		reportOrganizations = []
		for oKey in user.reportOrganizations:
			org = models.Organization.get(oKey)
			reportOrganizations.append({
				'key': org.key(),
				'name': org.name,
				'reporters': self.convUserNickname(org.reporters),
				'receivers': self.convUserNickname(org.receivers),
				'adminers': self.convUserNickname(org.adminers),
			})

		receiveOrganizations = []
		for oKey in user.receiveOrganizations:
			org = models.Organization.get(oKey)
			receiveOrganizations.append({
				'key': org.key(),
				'name': org.name,
				'reporters': self.convUserNickname(org.reporters),
				'receivers': self.convUserNickname(org.receivers),
				'adminers': self.convUserNickname(org.adminers),
			})

		adminOrganizations = []
		for oKey in user.adminOrganizations:
			org = models.Organization.get(oKey)
			adminOrganizations.append({
				'key': org.key(),
				'name': org.name,
				'reporters': self.convUserNickname(org.reporters),
				'receivers': self.convUserNickname(org.receivers),
				'adminers': self.convUserNickname(org.adminers),
			})

		self.render('views/organization/list.html', {
			'reportOrganizations': reportOrganizations,
			'receiveOrganizations': receiveOrganizations,
			'adminOrganizations': adminOrganizations,
		})