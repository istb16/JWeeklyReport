# -*- coding: utf-8 -*-

import controllers
import models
from google.appengine.api import users
from google.appengine.api import memcache

class LoginedBase(controllers.Base):
	def __init__(self):
		controllers.Base.__init__(self)

		self.loginUser = None
		self.isAdminUser = False

	def __before__(self, *args):
		controllers.Base.__before__(self, args)

		guser = users.get_current_user()
		if not guser:
			self.redirect(users.create_login_url(self.request.url))
			return False

		user = memcache.get('loginUser')
		if not user or user.author != guser:
			user = models.User.all().filter('author =', guser).get()
		if not user:
			user = models.User(
				author = guser,
			)
			user.put()
		memcache.add("loginUser", user, 43,200)

		self.isAdminUser = users.is_current_user_admin()
		self.loginUser = user

		tmpl = {
			'isLogin': True,
			'isAdmin': self.isAdminUser,
			'loginUser': user,
			'alertSuccess': [],
		}

		msgs = models.Message.all().filter('user =', self.loginUser.author).fetch(limit=controllers.Base.DisplayLimit)
		if msgs:
			for msg in msgs:
				if msg.mtype == 0:
					tmpl['alertSuccess'].append({
						'title': msg.title,
						'message': msg.message,
					})
				msg.delete()

		self.template_vals.update(tmpl)

		return True

	def haveReadAccessOrganization(self, org, accessType=None):
		if not accessType:
			accessType = self.getAccessTypeOrganization(org)

		return (accessType['Reporter'] or accessType['Receiver'] or accessType['Adminer'])

	def haveFullAccessOrganization(self, org, accessType=None):
		if org:
			if not accessType:
				accessType = self.getAccessTypeOrganization(org)
			return (accessType['Adminer'])
		else:
			user = self.loginUser
			return self.isAdminUser or (user.adminOrganizations != None and len(user.adminOrganizations) > 0)

	def getAccessTypeOrganization(self, org):
		uKey = self.loginUser.key()

		return {
			'Reporter': (org.reporters.count(uKey) > 0),
			'Receiver': (org.receivers.count(uKey) > 0),
			'Adminer': (org.adminers.count(uKey) > 0),
		}

	def haveReadAccessReport(self, rpt, accessType=None):
		if not accessType:
			accessType = self.getAccessTypeReport(rpt)

		return (accessType['Reporter'] or accessType['Receiver'] or accessType['Adminer'])

	def haveFullAccessReport(self, rpt, accessType=None):
		if rpt:
			if not accessType:
				accessType = self.getAccessTypeReport(rpt)
			return (accessType['Reporter'] or accessType['Adminer'])
		else:
			user = self.loginUser
			return (user.reportOrganizations != None and len(user.reportOrganizations) > 0)

	def getAccessTypeReport(self, rpt):
		user = self.loginUser
		oKey = rpt.organization.key()

		return {
			'Reporter': (user.reportOrganizations.count(oKey) > 0),
			'Receiver': (user.receiveOrganizations.count(oKey) > 0),
			'Adminer': (user.adminOrganizations.count(oKey) > 0),
		}