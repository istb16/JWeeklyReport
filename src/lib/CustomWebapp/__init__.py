# -*- coding: utf-8 -*-

import cgi
import os
from google.appengine.ext.webapp import *
from google.appengine.ext.webapp import template

class CustomRequestHandler(RequestHandler):
	def __init__(self):
		self.template_file = 'index.html'
		self.template_vals = {}

	def __before__(self, *args):
		# Allows common code to be used for all get/post/delete methods
		return True

	def __after__(self, *args):
		# This runs AFTER response is returned to browser.
		# If you have follow up work that you don't want to do while
		# browser is waiting put it here such as sending emails etc
		pass

	def render(self, template_file=None, template_vals={}):
		# Helper method to render the appropriate template
		if not template_file == None:
			self.template_file = template_file
		self.template_vals.update(template_vals)

		path = os.path.abspath(self.template_file)
		self.response.out.write(template.render(path, self.template_vals))


class CustomWSGIApplication(WSGIApplication):
	def __init__(self, url_mapping, debug=False):
		self._init_url_mappings(url_mapping)
		self.__debug = debug
		WSGIApplication.active_instance = self
		self.current_request_args = ()

	def __call__(self, environ, start_response):
		# Called by WSGI when a request comes in.
		request = Request(environ)
		response = Response()

		WSGIApplication.active_instance = self

		handler = None
		groups = ()
		for regexp, handler_class in self._url_mapping:
			match = regexp.match(request.path)
			if match:
				handler = handler_class()
				handler.initialize(request, response)
				groups = match.groups()
				break

		self.current_request_args = groups

		if handler:
			try:
				if handler.__before__(*groups) == False:
					response.wsgi_write(start_response)
					return ['']
				method = environ['REQUEST_METHOD']
				if method == 'GET':
					handler.get(*groups)
				elif method == 'POST':
					handler.post(*groups)
				elif method == 'HEAD':
					handler.head(*groups)
				elif method == 'OPTIONS':
					handler.options(*groups)
				elif method == 'PUT':
					handler.put(*groups)
				elif method == 'DELETE':
					handler.delete(*groups)
				elif method == 'TRACE':
					handler.trace(*groups)
				else:
					handler.error(501)
				response.wsgi_write(start_response)
				handler.__after__(*groups)
			except Exception, e:
				handler.handle_exception(e, self.__debug)
		else:
			response.set_status(404)
			response.wsgi_write(start_response)
		return ['']