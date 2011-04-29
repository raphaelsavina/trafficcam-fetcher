"""Regularly fetch all pictures from remote location and store in the datastore."""
from __future__ import with_statement
from google.appengine.api import urlfetch, files
from google.appengine.ext import blobstore, webapp, db
from google.appengine.ext.webapp import blobstore_handlers, template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Webcam, WebcamImage
import logging
import os
import urllib

class FetchPage(webapp.RequestHandler):
  def get(self):
    """Simple get request handler."""
#    self.response.headers["Content-Type"] = "text/html"
#    self.response.out.write("<p>Starting fetch op")
    logging.info("Cron job started")
    webcams = Webcam.all()
    for cam in webcams:
      try:
#        self.response.out.write("<p>Fetching for webcam %s..." % cam.name)
        fetch_response = urlfetch.fetch(cam.image_url)
        image_data = fetch_response.content
        image_blob = files.blobstore.create(mime_type='image/jpeg')
        with files.open(image_blob, "a") as f:
		f.write(image_data)
        files.finalize(image_blob)
        im = WebcamImage()
        im.webcam = cam.name
        im.blob = files.blobstore.get_blob_key(image_blob)
        im.put()
        blob_info = blobstore.BlobInfo.get(im.blob.key())
#        self.response.out.write("Fetching for webcam %s %s <br>" % (blob_info.size, im.blob.key()))
#        self.response.out.write("Success!\n")
#       Getting (ALL?) the previously saved IMG to check size
#       but really we should make sure to maniputale only last saved
        q_images = WebcamImage.all()
        q_images.filter("webcam =", cam.name)
        q_images.order("-timestamp")
        pic_index = 1
        q_results = q_images.fetch(2)
        q_blob_info = blobstore.BlobInfo.get(q_results[pic_index].blob.key())
#        self.response.out.write("Size previsously saved: %s %s <br>" % (q_blob_info.size, q_blob_info.key()))
        if q_blob_info.size == blob_info.size:
#          This delete is now working...
           im.delete()
#       Just one entry into Log for info.
           logging.info("Fetch: same size as previous => blob for %s deleted" % cam.name)
      except Exception, e:
#        self.response.out.write("<p>Error encountered - please check the logs")
        logging.error("Error fetching data: %s" % e)
  def post(self):
    """Simple post request handler."""
    pass

application = webapp.WSGIApplication([("/fetchPics", FetchPage), ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()


