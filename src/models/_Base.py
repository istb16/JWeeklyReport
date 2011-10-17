# -*- coding: utf-8 -*-

from google.appengine.ext import db

class Base(db.Model):
	createdAt = db.DateTimeProperty(auto_now_add=True)
	updatedAt = db.DateTimeProperty(auto_now=True)
