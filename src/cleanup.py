"""Regularly remove oldest images from the datastore"""
from __future__ import with_statement
from google.appengine.api import urlfetch, files, taskqueue
from google.appengine.ext import blobstore, webapp, db
from google.appengine.ext.webapp import blobstore_handlers, template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import WebcamImage, Webcam
import logging
import datetime
import os
import urllib

class CleanUp(webapp.RequestHandler):
	def get(self):
		"""Simple get request handler."""
		taskqueue.add(queue_name='cleaning', url='/cleanQ')
	def post(self):
		"""Simple post request handler."""
		pass

class CleanQ(webapp.RequestHandler):
	def post(self):
		"""Simple get request handler."""
		time_now = datetime.datetime.now()
		query_time = time_now - datetime.timedelta(hours=12)
		cam = Webcam.all()
		cam.order("name")
		for j in cam:
			try:
				d_images = WebcamImage.all()
				d_images.filter("webcam =", j.name )			
				d_images.filter("timestamp <", query_time)
				d_images.order("timestamp")
				# We need to keep at least 10 images
				d_count = d_images.count()
				if d_count > 10:
					for l in d_images:
						del_blob = blobstore.BlobInfo.get(l.blob.key())
						if del_blob:
							del_blob.delete()
							logging.info("From %s - Delete %s/ Name:%s " % (query_time, l.timestamp, l.webcam))
						l.delete()
						d_count = d_count - 1
						if d_count == 10:
							break
			except Exception, f:
				logging.error("Error fetching data: %s" % f)
	def get(self):
		"""Simple post request handler."""
		pass

application = webapp.WSGIApplication([(r"/cleanUp", CleanUp),
									  (r"/cleanQ", CleanQ)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
