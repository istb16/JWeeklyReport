# -*- coding: utf-8 -*-

import cgi
import os
import controllers
import models
import datetime
from google.appengine.api import users
from django.utils import simplejson
import viewfilters.CustomString

class ServiceYW2Period(controllers.PublicBase):
	def get(self, year, weekNum):
		data = self.getDateWithCalendar(int(year),int(weekNum))
		data = {
			'start':data['start'].isoformat(),
			'end':data['end'].isoformat(),
		}
		json = simplejson.dumps(data, ensure_ascii=False)
		self.response.content_type = 'application/json'
		self.response.out.write(json)

class ServiceGetReports(controllers.LoginedBase):
	def get(self, page, orgKey=None):
		page = int(page)
		displayLimit = controllers.Base.DisplayLimit

		if not orgKey:
			reports = models.Report.all().filter('user =', self.loginUser)
			reports = reports.order('-year').order('-weekNum')
		else:
			org = models.Organization.get(orgKey)

			# アクセス制限
			accessType = self.getAccessTypeOrganization(org)
			if not org or not self.haveReadAccessOrganization(org, accessType):
				self.error(403)
				return
			reports = models.Report.all().filter('organization =', org)
			if not accessType['Reporter'] and not accessType['Adminer']:
				reports = reports.filter('user =', self.loginUser)
			reports = reports.order('-year').order('-weekNum')

		data = {
			'reports': [],
		}
		for rpt in reports.fetch(limit=displayLimit, offset=page * displayLimit):
			cal = self.getDateWithCalendar(int(rpt.year),int(rpt.weekNum))
			data['reports'].append({
				'key': str(rpt.key()),
				'year': str(rpt.year),
				'weekNum': str(rpt.weekNum),
				'periodStart': cal['start'].isoformat(),
				'periodEnd': cal['end'].isoformat(),
				'content': viewfilters.CustomString.truncatejp(rpt.content, 70),
				'userName': rpt.user.author.nickname(),
				'orgName': rpt.organization.name,
			})

		json = simplejson.dumps(data, ensure_ascii=False)
		self.response.content_type = 'application/json'
		self.response.out.write(json)

class ServiceGetUsers(controllers.LoginedBase):
	def get(self, page):
		# アクセス制限
		if not self.isAdminUser:
			self.error(403)
			return

		page = int(page)
		displayLimit = controllers.Base.DisplayLimit

		us = models.User.all()

		data = {
			'users': [],
		}
		for user in us.fetch(limit=displayLimit, offset=page * displayLimit):
			data['users'].append({
				'key': str(user.key()),
				'userName': user.author.nickname(),
				'userEmail': user.author.email(),
				'userUniqueID': user.author.user_id(),
			})

		json = simplejson.dumps(data, ensure_ascii=False)
		self.response.content_type = 'application/json'
		self.response.out.write(json)