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

		self.render('views/report_index.html', {
			'rpt': rpt,
			'rptWeekStart': week['start'],
			'rptWeekEnd': week['end'],
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

		self.render('views/report_add.html', {
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
		isFinish = (self.request.get('isFinish') == 'True')

		user = self.loginUser
		org = models.Organization.get(orgKey)

		# データ保存
		rpt = models.Report(
			year = int(self.request.get('year')),
			weekNum = int(self.request.get('weekNum')),
			content = self.request.get('content'),
			user = user,
			organization = org,
			isFinish = isFinish,
		)
		rpt.put()


		# メール送信
		if rpt.isFinish:
			if len(rpt.organization.notifyEmail) > 0:
				models.SendMail.receiveReport(rpt.organization.notifyEmail, rpt, self.getDateWithCalendar(rpt.year, rpt.weekNum))

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
		if rpt.isFinish:
			self.error(403)
			return

		self.render('views/report_edit.html', {
			'rpt': rpt,
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
		isFinish = (self.request.get('isFinish') == 'True')

		# データ保存
		rpt.year = year
		rpt.weekNum = weekNum
		rpt.content = content
		rpt.isFinish = isFinish
		rpt.put()

		# メール送信
		if rpt.isFinish:
			if len(rpt.organization.notifyEmail) > 0:
				models.SendMail.receiveReport(rpt.organization.notifyEmail, rpt, self.getDateWithCalendar(rpt.year, rpt.weekNum))

		msg = models.Message(
			user = self.loginUser.author,
			title = 'Well done!',
			message = 'You have successfully saved data',
		)
		msg.put()

		self.redirect('/Report/' + str(rpt.key()))

class ReportFinish(Report):
	def get(self, key=None):
		rpt = models.Report.get(key);

		# アクセス制限
		if not self.haveFullAccessReport(rpt):
			self.error(403)
			return
		if rpt.isFinish:
			self.error(403)
			return

		rpt.isFinish = True
		rpt.put()

		# メール送信
		if rpt.isFinish:
			if len(rpt.organization.notifyEmail) > 0:
				models.SendMail.receiveReport(rpt.organization.notifyEmail, rpt, self.getDateWithCalendar(rpt.year, rpt.weekNum))

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
		receiveOrganizations = []
		for oKey in self.loginUser.receiveOrganizations:
			org = models.Organization.get(oKey)
			receiveOrganizations.append({
				'key': org.key(),
				'name': org.name,
			})

		self.render('views/report_list.html', {
			'receiveOrganizations': receiveOrganizations,
		})