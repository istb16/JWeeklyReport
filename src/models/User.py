# -*- coding: utf-8 -*-

import models
from google.appengine.ext import db

class User(models.Base):
	author = db.UserProperty(required=True)
	adminOrganizations = db.ListProperty(db.Key)
	reportOrganizations = db.ListProperty(db.Key)
	receiveOrganizations = db.ListProperty(db.Key)