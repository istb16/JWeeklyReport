# -*- coding: utf-8 -*-

import models
from google.appengine.ext import db

class Organization(models.Base):
	name = db.StringProperty(required=True, multiline=False)
	reportTemplate = db.TextProperty()

	reporters = db.ListProperty(db.Key)
	receivers = db.ListProperty(db.Key)
	adminers = db.ListProperty(db.Key)

	reporterWaitings = db.StringListProperty()
	receiverWaitings = db.StringListProperty()
	adminerWaitings = db.StringListProperty()

	notifyEmail = db.StringProperty(default='')