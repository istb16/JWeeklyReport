# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
register = webapp.template.create_template_register()

@register.filter
def truncatejp(value, arg):
	value = value.strip()
	if len(value) <= arg:
		return value
	return value[:arg].strip() + u'...'