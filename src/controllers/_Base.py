# -*- coding: utf-8 -*-

import lib.CustomWebapp as webapp
from urllib import quote
from datetime import date, timedelta
from google.appengine.api import users

class Base(webapp.CustomRequestHandler):
	def __before__(self, *args):
		webapp.CustomRequestHandler.__before__(self, args)

		self.template_vals.update({
			'isLogin': False,
			'urlLogin': users.create_login_url('/'),
			'urlLogout': users.create_logout_url('/'),
		})

		return True

	#
	# エラー表示
	#
	def error(self, code, message = 'an error occured.'):
		if code == 404:
			message = 'Sorry, we were not able to find the requested page.	We have logged this error and will look into it.'
		elif code == 403:
			message = 'Sorry, that page is forbidden.'
		elif code == 500:
			message = "Sorry, the server encountered an error.  We have logged this error and will look into it."

		self.redirect('/System/Error/' + quote(str(code)) + '/' + quote(message))

	#
	# dateから年と週番号を取得
	# デフォルトは、ISOモード
	#
	def getCalendarWithDate(self, d, weekNumType = 0):
		if weekNumType == Base.WeekNumTypeISO:
			cal = d.isocalendar()
			rtValue = {
				'year': cal[0],
				'weekNum': cal[1],
			}
		elif weekNumType == Base.WeekNumTypeMon:
			rtValue = {
				'year': d.year,
				'weekNum': int(d.strftime('%W')),
			}
		elif weekNumType == Base.WeekNumTypeSun:
			rtValue = {
				'year': d.year,
				'weekNum': int(d.strftime('%U')),
			}
		else:
			rtValue = {}

		return rtValue

	#
	# 年と週番号から開始日と終了日のdateを取得
	# デフォルトは、ISOモード
	#
	def getDateWithCalendar(self, year, weekNum, weekNumType = 0):
		if weekNumType == Base.WeekNumTypeISO:
			# 指定された年の1/4を取得し、その日を含む週を1週目として、指定された週番号の開始日と終了日を取得
			dStart = date(year, 1, 4)
			while dStart.weekday() > 0:
				dStart -= timedelta(days=1)
			dStart += timedelta(days=((weekNum - 1) * 7))
			rtValue = {
				'start': dStart,
				'end': dStart + timedelta(days=6),
			}
		elif weekNumType == Base.WeekNumTypeMon:
			# 指定された年の月曜日を取得し、その日を含む週を1週目として、指定された週番号の開始日と終了日を取得
			dStart = date(year, 1, 1)
			while dStart.weekday() != 0:
				dStart += timedelta(days=1)
			dStart += timedelta(days=((weekNum - 1) * 7))
			rtValue = {
				'start': dStart,
				'end': dStart + timedelta(days=6),
			}
		elif weekNumType == Base.WeekNumTypeSun:
			# 指定された年の日曜日を取得し、その日を含む週を1週目として、指定された週番号の開始日と終了日を取得
			dStart = date(year, 1, 1)
			while dStart.weekday() != 6:
				dStart += timedelta(days=1)
			dStart += timedelta(days=((weekNum - 1) * 7))
			rtValue = {
				'start': dStart,
				'end': dStart + timedelta(days=6),
			}
		else:
			rtValue = {}
		return rtValue


Base.WeekNumTypeISO = 0
Base.WeekNumTypeMon = 1
Base.WeekNumTypeSun = 2

Base.DisplayLimitShort = 5
Base.DisplayLimit = 10

Base.RangeYear = range(2001, 2051)
Base.RangeWeekNum = range(0, 53)

Base.RSA_KEY = 'AXETDZSE'