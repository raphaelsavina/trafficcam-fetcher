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
    logging.info("Cleanup process")
    time_now = datetime.datetime.now()
    query_time = time_now - datetime.timedelta(days=3)
    d_images = WebcamImage.all()
    d_images.filter("timestamp <", query_time)
    d_images.order("timestamp")
    for l in d_images:
      del_blob = blobstore.BlobInfo.get(l.blob.key())
      if del_blob:
        del_blob.delete()
      l.delete()

  def post(self):
    """Simple post request handler."""
    pass

application = webapp.WSGIApplication([("/cleanUp", CleanUp), ],
                                     debug=False)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
