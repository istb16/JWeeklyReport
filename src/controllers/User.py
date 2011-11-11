# -*- coding: utf-8 -*-

import cgi
import os
import controllers
import models
from google.appengine.api import users
from google.appengine.api import memcache

class UserConf(controllers.LoginedBase):
	pass

class UserConfReceiver(UserConf):
	def get(self, key=None):
		# 指定されたOrganizationモデルを取得
		org = models.Organization.get(key)

		user = self.loginUser

		# 自分のメールアドレスが許可待ちかチェック
		isEnableEmail = (org.receiverWaitings.count(user.author.email()) == 0)
		if isEnableEmail:
			if user.receiveOrganizations.count(org.key()) == 0 and org.receivers.count(user.key()) == 0:
				self.error(403)
				return

		# UserモデルとOragnizationモデルに保存
		if user.receiveOrganizations.count(org.key()) == 0:
			user.receiveOrganizations.append(org.key())
		if org.receivers.count(user.key()) == 0:
			org.receivers.append(user.key())

		# 許可待ちから削除する
		if not isEnableEmail:
			org.receiverWaitings.remove(user.author.email())

		# 保存する
		user.put()
		memcache.delete("loginUser")
		org.put()

		self.render('views/user_confReceiver.html', {
			'orgKey': org.key(),
			'orgName': org.name,
		})

class UserConfAdminer(UserConf):
	def get(self, key=None):
		# 指定されたOrganizationモデルを取得
		org = models.Organization.get(key)

		user = self.loginUser

		# 自分のメールアドレスが許可待ちかチェック
		isEnableEmail = (org.adminerWaitings.count(user.author.email()) == 0)
		if isEnableEmail:
			if user.adminOrganizations.count(org.key()) == 0 and org.adminers.count(user.key()) == 0:
				self.error(403)
				return

		# UserモデルとOragnizationモデルに保存
		if user.adminOrganizations.count(org.key()) == 0:
			user.adminOrganizations.append(org.key())
		if org.adminers.count(user.key()) == 0:
			org.adminers.append(user.key())

		# 許可待ちから削除する
		if not isEnableEmail:
			org.adminerWaitings.remove(user.author.email())

		# 保存する
		user.put()
		memcache.delete("loginUser")
		org.put()

		self.render('views/user_confAdminer.html', {
			'orgKey': org.key(),
			'orgName': org.name,
		})

class UserConfReporter(UserConf):
	def get(self, key=None):
		# 指定されたOrganizationモデルを取得
		org = models.Organization.get(key)

		user = self.loginUser

		# 自分のメールアドレスが許可待ちかチェック
		isEnableEmail = (org.reporterWaitings.count(user.author.email()) == 0)
		if isEnableEmail:
			if user.reportOrganizations.count(org.key()) == 0 and org.reporters.count(user.key()) == 0:
				self.error(403)
				return

		# UserモデルとOragnizationモデルに保存
		if user.reportOrganizations.count(org.key()) == 0:
			user.reportOrganizations.append(org.key())
		if org.reporters.count(user.key()) == 0:
			org.reporters.append(user.key())

		# 許可待ちから削除する
		if not isEnableEmail:
			org.reporterWaitings.remove(user.author.email())

		# 保存する
		user.put()
		memcache.delete("loginUser")
		org.put()

		self.render('views/user_confReporter.html', {
			'orgKey': org.key(),
			'orgName': org.name,
		})

class User(controllers.LoginedBase):
	pass

class UserDelete(User):
	def get(self, key=None):
		# アクセス制限
		if not self.isAdminUser:
			self.error(403)
			return

		user = models.User.get(key)
		key = user.key()

		for oKey in user.reportOrganizations:
			org = models.Organization.get(oKey)
			while key in org.reporters: org.reporters.remove(key)
			org.put()

		for oKey in user.receiveOrganizations:
			org = models.Organization.get(oKey)
			while key in org.receivers: org.receivers.remove(key)
			org.put()

		for oKey in user.adminOrganizations:
			org = models.Organization.get(oKey)
			while key in org.adminers: org.adminers.remove(key)
			org.put()

		user.delete()

		msg = models.Message(
			user = self.loginUser.author,
			title = 'Well done!',
			message = 'You have successfully delete data',
		)
		msg.put()

		self.redirect('/User')

class UserList(User):
	def get(self):
		if not self.isAdminUser:
			self.error(403)
			return

		self.render('views/user_list.html', {
		})