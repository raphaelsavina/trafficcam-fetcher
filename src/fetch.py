"""Regularly fetch all pictures from remote location and store in the datastore."""

from google.appengine.api import urlfetch, files
from google.appengine.ext import blobstore, webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Webcam, WebcamImage
import logging


class FetchPage(webapp.RequestHandler):
  def get(self):
    """Simple get request handler."""
    self.response.headers["Content-Type"] = "text/html"
    self.response.out.write("<p>Starting fetch op")
    logging.info("Cron job started")
    webcams = Webcam.all()
    for cam in webcams:
      try:
        self.response.out.write("<p>Fetching for webcam %s..." % cam.name)
        fetch_response = urlfetch.fetch(cam.image_url)
        image_data = fetch_response.content
        image_blob = files.blobstore.create(mime_type='image/jpeg')
				
				f = files.open(image_blob, "a")
				f.write(image_data)
        files.finalize(image_blob)

        im = WebcamImage()
        im.webcam = cam.name
        im.blob = files.blobstore.get_blob_key(image_blob)
        im.put()
        self.response.out.write("Success!\n")
      except Exception, e:
        self.response.out.write("<p>Error encountered - please check the logs")
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


