"""Display index page and admin page.
"""

import logging
import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp import blobstore_handlers, template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import WebcamImage

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
		im = WebcamImage.all()
		im.order("webcam")
		im.order("-timestamp")
		# limiting pictures to 25 - otherwise we may run out of CPU quota
		results = im.fetch(1000)
		# rewrite the values - blob is a BlobReferenceProperty, but we need to pass
		# the key
		pic_blobs = [{"blob": i.blob.key(),
	                  "webcam": i.webcam,
	                  "size": i.blob.size,
	                  "timestamp": i.timestamp}
	                   for i in results]
		template_values = {
			"images": pic_blobs,
	    }
		path = os.path.join(os.path.dirname(__file__), "admin.html")
		self.response.out.write(template.render(path, template_values))

	def post(self):
		"""Simple post request handler."""
	pass

application = webapp.WSGIApplication([("/", MainPage),("/admin", AdminPage) ],
                                     debug=False)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
