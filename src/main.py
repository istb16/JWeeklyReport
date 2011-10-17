# -*- coding: utf-8 -*-

import cgi
import os

import lib.CustomWebapp as webapp
webapp.template.register_template_library('viewfilters.CustomString')
import controllers

from google.appengine.ext.webapp.util import run_wsgi_app

application = webapp.CustomWSGIApplication([('/', controllers.Top),
											('/Dashboard', controllers.Dashboard),
											('/Organization', controllers.OrganizationList),
											('/Organization/add', controllers.OrganizationAdd),
											('/Organization/edit/(.*)', controllers.OrganizationEdit),
											('/Organization/delete/(.*)', controllers.OrganizationDelete),
											('/Organization/(.*)', controllers.Organization),
											('/Report', controllers.ReportList),
											('/Report/add', controllers.ReportAdd),
											('/Report/add/(.*)', controllers.ReportAdd),
											('/Report/edit/(.*)', controllers.ReportEdit),
											('/Report/delete/(.*)', controllers.ReportDelete),
											('/Report/(.*)', controllers.Report),
											('/Service/YW2Period/(.*)/(.*)', controllers.ServiceYW2Period),
											('/Service/GetReports/(.*)/(.*)', controllers.ServiceGetReports),
											('/Service/GetUsers/(.*)', controllers.ServiceGetUsers),
											('/User', controllers.UserList),
											('/User/delete/(.*)', controllers.UserDelete),
											('/User/ConfReporter/(.*)', controllers.UserConfReporter),
											('/User/ConfReceiver/(.*)', controllers.UserConfReceiver),
											('/User/ConfAdminer/(.*)', controllers.UserConfAdminer),
											('/System/Error/(.*)/(.*)', controllers.SystemError),
										   ],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()