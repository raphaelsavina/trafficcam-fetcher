"""Display index page and admin page.
"""

import logging
import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp import blobstore_handlers, template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import WebcamImage, Webcam

class MainPage(webapp.RequestHandler):
	def get(self):
		"""Simple get request handler."""
		self.response.headers["Content-Type"] = "text/html"
		self.response.out.write("Nothing here yet.")
	pass

	def post(self):
		"""Simple post request handler."""
	pass

class AdminPage(webapp.RequestHandler):
	def get(self):
		cam = Webcam.all()
		cam.order("-name")
		counti = 0
		pic_blobs = []
		for j in cam:
			try:
				im = WebcamImage.all()
				im.filter("webcam =", j.name.lower())
				im.order("webcam")
				results = im.fetch(4)
				for i in results:
					try: 
						pic_blobs = pic_blobs + [{"blob": i.blob.key(),"webcam": i.webcam,"size": i.blob.size,"timestamp": i.timestamp, "count" : counti}]
						counti = counti + 1
					except Exception, e:
						logging.error("Error fetching data: %s %s" % e)
				counti = 0
			except Exception, f:
				logging.error("Error fetching data: %s" % f)
		cam_name = [{"name":j.name}for j in cam]

		template_values = {
			"images": pic_blobs, "names" : cam_name
	    }

		path = os.path.join(os.path.dirname(__file__), "admin.html")
		self.response.out.write(template.render(path, template_values))

	def post(self):
		"""Simple post request handler."""
	pass

application = webapp.WSGIApplication([("/", MainPage),("/adminpage", AdminPage) ],
                                     debug=False)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
