# -*- coding: utf-8 -*-

import cgi
import os
import controllers
import models
from google.appengine.api import users
from datetime import date, timedelta

class Dashboard(controllers.LoginedBase):
	def get(self):
		user = self.loginUser
		# 報告する組織を取得
		# 報告期限を過ぎた組織を取得（期限は前の週の報告がない場合とする）
		lmtCal = self.getCalendarWithDate(date.today() - timedelta(days=7))
		reportOrganizations = []
		overReportOrganization = []
		for oKey in user.reportOrganizations:
			org = models.Organization.get(oKey)
			reportOrganizations.append({
				'orgKey': org.key(),
				'orgName': org.name,
			})
			# 期限切れか判定し、切れていたら追加
			q = models.Report.all().filter('user =', user).filter('organization =', org)
			q = q.filter('year =', lmtCal['year']).filter('weekNum =', lmtCal['weekNum'])
			isLimitOver = False
			if q.count(limit=1) <= 0: isLimitOver = True
			else:
				for rpt in q:
					if not rpt.isFinish:
						isLimitOver = True
						break
			if isLimitOver:
				overReportOrganization.append({
					'orgKey': org.key(),
					'orgName': org.name,
				})

		# 管理する組織を取得
		adminOrganizations = []
		for oKey in user.adminOrganizations:
			org = models.Organization.get(oKey)
			adminOrganizations.append({
				'orgKey': org.key(),
				'orgName': org.name,
			})

		# 受付する組織を取得
		# 受付した報告（件数制限）を取得
		receiveOrganizations = []
		receiveReports = []
		for oKey in user.receiveOrganizations:
			org = models.Organization.get(oKey)
			receiveOrganizations.append({
				'orgKey': org.key(),
				'orgName': org.name,
			})
			q = models.Report.all().filter('organization =', org)
			q = q.order('updatedAt')
			for rpt in q.fetch(limit=controllers.Base.DisplayLimitShort):
				week = self.getDateWithCalendar(rpt.year, rpt.weekNum)
				receiveReports.append({
					'rptKey': rpt.key(),
					'rptYear': rpt.year,
					'rptWeekStart': week['start'],
					'rptWeekEnd': week['end'],
					'rptContent': rpt.content,
					'rptUpdatedAt': rpt.updatedAt,
					'orgName': rpt.organization.name,

				})
		receiveReports.sort(key=lambda r: r['rptUpdatedAt'], reverse=True)
		if receiveReports:
			receiveReports = receiveReports[:controllers.Base.DisplayLimitShort]

		# 報告した報告（件数制限）を取得
		updatedReports = []
		q = models.Report.all().filter('user =', user)
		q = q.order('-updatedAt')
		for rpt in q.fetch(limit=controllers.Base.DisplayLimitShort):
			week = self.getDateWithCalendar(rpt.year, rpt.weekNum)
			updatedReports.append({
				'rptKey': rpt.key(),
				'rptYear': rpt.year,
				'rptWeekStart': week['start'],
				'rptWeekEnd': week['end'],
				'rptContent': rpt.content,
				'orgName': rpt.organization.name,
			})

		self.render('views/dashboard_index.html', {
			'reportOrganizations': reportOrganizations,
			'adminOrganizations': adminOrganizations,
			'receiveOrganizations': receiveOrganizations,
			'updatedReports': updatedReports,
			'overReportOrganization': overReportOrganization,
			'receiveReports': receiveReports,
			'isHaveAdminOrganization': (len(adminOrganizations) > 0),
		})
