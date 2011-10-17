# -*- coding: utf-8 -*-

import models
from google.appengine.ext import db

class Message(db.Model):
	user = db.UserProperty()
	mtype = db.IntegerProperty(default=0)
	title = db.StringProperty(multiline=False)
	message = db.StringProperty(multiline=False)
	createdAt = db.DateTimeProperty(auto_now_add=True)