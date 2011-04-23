"""Simple model to store picture information."""


from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore

class WebcamImage(db.Model):
  webcam = db.StringProperty()
  blob = blobstore.BlobReferenceProperty()
  timestamp = db.DateTimeProperty(auto_now_add=True)


class Webcam(db.Model):
  name = db.StringProperty()
  image_url = db.URLProperty()

