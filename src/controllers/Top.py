# -*- coding: utf-8 -*-

import cgi
import os
import controllers
from google.appengine.api import users

class Top(controllers.PublicBase):
	def get(self):
		user = users.get_current_user()
		if user:
			self.redirect('/Dashboard')
		else:
			self.render('views/top_index.html', {'urlLogin': users.create_login_url(self.request.uri)})
