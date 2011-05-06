"""Serve images from the blobstore.
"""
from google.appengine.ext import webapp, blobstore
from google.appengine.ext.webapp import blobstore_handlers, template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import WebcamImage
import cgi
import logging
import os
import urllib

# Hmm, it seems I can only serve a single byte range at once...
#class ServeAllPics(blobstore_handlers.BlobstoreDownloadHandler):
#  """Handler class for outputting all pictures in an ordered format for HTML."""
#  def get(self):
#    logging.info("Serving all pictures...")
#    im = WebcamImage.all()
#    try:
#      for i in im:
#        self.send_blob(blobstore.BlobInfo.get(i.blob.key()))
#    except Exception, e:
#      logging.error("Error while serving all pictures: %s" % e)

class ServeAllPics(webapp.RequestHandler):
  """Triggers a html page showing multiple images."""
  def get(self):
    logging.info("Serving all pictures...")
    im = WebcamImage.all()
    im.order("-timestamp")
    im.order("webcam")
		# limiting pictures to 25 - otherwise we may run out of CPU quota
    results = im.fetch(25)
    # rewrite the values - blob is a BlobReferenceProperty, but we need to pass
    # the key
    pic_blobs = [{"blob": i.blob.key(),
                  "webcam": i.webcam,
                  "size": i.blob.size,
                  "timestamp": i.timestamp}
                   for i in results]
                   #"size": i.blob.size 
                   #size could be used in fetch to place in blob only new image, compare size to previous, ignore if same?

    template_values = {
        "images": pic_blobs
    }

    path = os.path.join(os.path.dirname(__file__), "images.html")
    self.response.out.write(template.render(path, template_values))

class ServeImage(blobstore_handlers.BlobstoreDownloadHandler):
#class ServeImage(webapp.RequestHandler):
  """Retrieve one image by blobkey."""
  def get(self, blob_key):
    logging.info("Retrieving image by blob key")
#    self.response.headers["Content-Type"] = "text/html"
#    self.response.out.write("<p>blob is %s" % urllib.unquote(blob_key))
    try:
      self.send_blob(blobstore.BlobInfo.get(urllib.unquote(blob_key)))
    except Exception, e:
      logging.error("Error while serving all pictures: %s" % e)
      return None


class ServeSinglePic(blobstore_handlers.BlobstoreDownloadHandler):
  """Handler class to serve a single picture from the blobstore."""
  def get(self, name, pic_index):
    if name == "" or pic_index == "":
      logging.warn("Encountered call for single picture with no params")
      return None
    logging.info("Serving a single picture:\n")

    q_images = WebcamImage.all()
    q_images.filter("webcam =", name.lower())
    q_images.order("-timestamp")
    pic_index = int(pic_index)

    q_results = q_images.fetch(limit=1, offset=pic_index)
    # len(q_results) should never be greater than pic_index, but just in case
    if len(q_results) != 0:
      self.send_blob(blobstore.BlobInfo.get(q_results[0].blob.key()))
    else:
      logging.warn("Query for single picture returned no results:\n%s"
                   % q_images)
      return None

  def post(self, name, pic_index):
    if name == "" or pic_index == "":
      logging.warn("Encountered call for single picture with no params")
      return None
    logging.info("Serving a single picture:\n")

    q_images = WebcamImage.all()
    q_images.filter("webcam =", name.lower())
    q_images.order("-timestamp")
    pic_index = int(pic_index)

    q_results = q_images.fetch(limit=1, offset=pic_index)
    # len(q_results) should never be greater than pic_index, but just in case
    if len(q_results) >= pic_index + 1:
      self.send_blob(blobstore.BlobInfo.get(q_results[pic_index].blob.key()))
    else:
      logging.warn("Query for single picture returned no results:\n%s"
                   % q_images)
      return None

class CatchAll(webapp.RequestHandler):
  def get(self):
    self.response.headers["Content-Type"] = "text/html"
    self.response.out.write("<p>CatchAll Get")

  def post(self):
    self.response.headers["Content-Type"] = "text/html"
    self.response.out.write("<p>CatchAll Post")


application = webapp.WSGIApplication([(r"/serve_all_pics*", ServeAllPics),
                                      (r"/image/(.*)", ServeImage),
                                      (r"/serve_single_pic/(.*)/(\d*)$",
                                       ServeSinglePic),
                                      (".*", CatchAll), ],
                                      debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
    main()
