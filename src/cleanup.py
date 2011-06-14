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
#   self.response.headers["Content-Type"] = "text/html"
#   self.response.out.write("Cleanup of old images<br>")
    logging.info("Cleanup process")
#   Built GQL
    time_now = datetime.datetime.now()
    query_time = time_now - datetime.timedelta(days=4)
    d_images = WebcamImage.all()
    d_images.filter("timestamp <", query_time)
    d_images.order("timestamp")
    # iterate over query to delete all the old stuff
    for l in d_images:
      logging.info("Query time is %s. Will delete one image from saved at %s" % (query_time, l.timestamp))
      # logging.info("Blobkey is %s." % l.blob.key())
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
