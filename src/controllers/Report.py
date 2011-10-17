# -*- coding: utf-8 -*-

import cgi
import os
import controllers
import models
from datetime import date, timedelta
from google.appengine.api import users

class Report(controllers.LoginedBase):

	def get(self, key=None):
		rpt = models.Report.get(key)

		# アクセス制限
		if not self.haveReadAccessReport(rpt):
			self.error(403)
			return

		week = self.getDateWithCalendar(rpt.year, rpt.weekNum)

		self.render('views/report/index.html', {
			'rptKey': rpt.key(),
			'rptWeekStart': week['start'],
			'rptWeekEnd': week['end'],
			'rptContent': rpt.content,
			'userNickname': rpt.user.author.nickname(),
			'orgName': rpt.organization.name,
		})

class ReportAdd(Report):
	def get(self, orgKey=None):
		# アクセス制限
		if not self.haveFullAccessReport(None):
			self.error(403)
			return

		user = self.loginUser

		if orgKey == None:
			orgKey = user.reportOrganizations[0]

		orgs = []
		for oKey in user.reportOrganizations:
			org = models.Organization.get(oKey)
			orgs.append({
				'key': str(oKey),
				'name': org.name,
				'reportTemplate': org.reportTemplate,
			})

		cal = self.getCalendarWithDate(date.today() - timedelta(days=7))

		self.render('views/report/add.html', {
			'rptYear': cal['year'],
			'rptWeekNum': cal['weekNum'],
			'userNickname': user.author.nickname(),
			'orgKey': orgKey,
			'orgs': orgs,
			'rangeYear': controllers.Base.RangeYear,
			'rangeWeekNum': controllers.Base.RangeWeekNum,
		})

	def post(self):
		# アクセス制限
		if not self.haveFullAccessReport(None):
			self.error(403)
			return

		orgKey = self.request.get('organization')

		user = self.loginUser
		org = models.Organization.get(orgKey)

		rpt = models.Report(
			year = int(self.request.get('year')),
			weekNum = int(self.request.get('weekNum')),
			content = self.request.get('content'),
			user = user,
			organization = org,
		)
		rpt.put()

		msg = models.Message(
			user = self.loginUser.author,
			title = 'Well done!',
			message = 'You have successfully saved data',
		)
		msg.put()

		self.redirect('/Report/' + str(rpt.key()))

class ReportEdit(Report):
	def get(self, key=None):
		rpt = models.Report.get(key);

		# アクセス制限
		if not self.haveFullAccessReport(rpt):
			self.error(403)
			return

		self.render('views/report/edit.html', {
			'rptKey': rpt.key(),
			'rptYear': rpt.year,
			'rptWeekNum': rpt.weekNum,
			'rptContent': rpt.content,
			'userNickname': rpt.user.author.nickname(),
			'orgName': rpt.organization.name,
			'rangeYear': controllers.Base.RangeYear,
			'rangeWeekNum': controllers.Base.RangeWeekNum,
		})

	def post(self, key=None):
		rpt = models.Report.get(key)

		# アクセス制限
		if not self.haveFullAccessReport(rpt):
			self.error(403)
			return

		year = int(self.request.get('year'))
		weekNum = int(self.request.get('weekNum'))
		content = self.request.get('content')

		rpt.year = year
		rpt.weekNum = weekNum
		rpt.content = content
		rpt.put()

		msg = models.Message(
			user = self.loginUser.author,
			title = 'Well done!',
			message = 'You have successfully saved data',
		)
		msg.put()

		self.redirect('/Report/' + str(rpt.key()))

class ReportDelete(Report):
	def get(self, key=None):
		rpt = models.Report.get(key)

		# アクセス制限
		if not self.haveFullAccessReport(rpt):
			self.error(403)
			return

		rpt.delete()

		msg = models.Message(
			user = self.loginUser.author,
			title = 'Well done!',
			message = 'You have successfully delete data',
		)
		msg.put()

		self.redirect('/Report')

class ReportList(Report):
	def get(self):
		user = self.loginUser

		receiveOrganizations = []
		for oKey in user.receiveOrganizations:
			org = models.Organization.get(oKey)
			receiveOrganizations.append({
				'key': org.key(),
				'name': org.name,
			})

		self.render('views/report/list.html', {
			'receiveOrganizations': receiveOrganizations,
		})