"""Regularly remove oldest images from the datastore"""
from __future__ import with_statement
from google.appengine.api import urlfetch, files
from google.appengine.ext import blobstore, webapp, db
from google.appengine.ext.webapp import blobstore_handlers, template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import WebcamImage
import logging
import datetime
import os
import urllib

class CleanUp(webapp.RequestHandler):
  def get(self):
    """Simple get request handler."""
#    self.response.headers["Content-Type"] = "text/html"
#    self.response.out.write("Cleanup of old images<br>")
    logging.info("Cleanup process")
#   Built GQL
    time_now = datetime.datetime.now()
    query_time = time_now - datetime.timedelta(days=5)
    d_images = WebcamImage.all()
    d_images.filter("timestamp <", query_time)
    d_images.order("timestamp")
    d_results = d_images.fetch(800)
    for l in d_results:
#      self.response.out.write("%s - Query time is %s. List only for now image from %s<br>" % (time_now, query_time, l.timestamp))
      logging.info("Query time is %s. will delete one image from saved at %s" % (query_time, l.timestamp))
      l.delete()
  def post(self):
    """Simple post request handler."""
    pass

application = webapp.WSGIApplication([("/cleanup", CleanUp), ],
                                     debug=False)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
