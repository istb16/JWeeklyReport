# -*- coding: utf-8 -*-

import cgi
import os
import controllers
from urllib import unquote
from google.appengine.api import users

class SystemError(controllers.PublicBase):
	def get(self, code, message):
		self.render('views/system/error.html',{'errorCode': unquote(code), 'errorMessage': unquote(message)})