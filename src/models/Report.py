# -*- coding: utf-8 -*-

import models
from google.appengine.ext import db

class Report(models.Base):
	year = db.IntegerProperty(required=True)
	weekNum = db.IntegerProperty(required=True)
	content = db.TextProperty(required=True)
	user = db.ReferenceProperty(models.User)
	organization = db.ReferenceProperty(models.Organization)
	isFinish = db.BooleanProperty(default=False)
