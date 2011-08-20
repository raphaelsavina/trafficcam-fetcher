"""Regularly fetch all pictures from remote location and store in the datastore."""
from __future__ import with_statement
from google.appengine.api import urlfetch, files, taskqueue, memcache
from google.appengine.ext import blobstore, webapp, db
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Webcam, WebcamImage
import logging
import os
import urllib

class FetchPage(webapp.RequestHandler):
  def get(self, index, offset):
	"""Simple get request handler."""
	self.response.headers["Content-Type"] = "text/html"
	self.response.out.write("<p>Sending fetch operation to Task Queues, one image at a time...</p>")
	logging.info("Cron job started")
	webcams = Webcam.all()
	webcams.order("-image_url")
	index = int(index)
	offset = int(offset)
	listcam = webcams.fetch(index, offset)
	logging.info("Index %s Offset %s" % (index, offset))
	for cam in listcam:
		try:
			check_size = urllib.urlopen(cam.image_url).read()
			image_size = len(check_size)
			q_images = WebcamImage.all()
			q_images.filter("webcam =", cam.name)
			q_images.order("-timestamp")
			pic_index = 0
			q_results = q_images.fetch(1)
			# Test just in case this is 1st time an image is checked
			try:
				q_blob_info = blobstore.BlobInfo.get(q_results[pic_index].blob.key())
				old_size = q_blob_info.size
			except:
				old_size = 0
			if old_size != image_size:
				logging.info("Cam: %s Size New %s != Size Old %s" % (cam.name, image_size, old_size))
				taskqueue.add(queue_name='fetching', url='/fetchQ', params={'cam': cam.name,'url': cam.image_url})
		except Exception, e:
			logging.error("Error fetching data: %s" % e)
			self.redirect("/fetchPics")
  def post(self):
    """Simple post request handler."""
    pass

class FetchQ(webapp.RequestHandler):
	def post(self):
		cam = self.request.get('cam')
		image_url = self.request.get('url')
		image_blob = files.blobstore.create(mime_type='image/jpeg')
		fetch_response = urlfetch.fetch(image_url)
		image_data = fetch_response.content
		with files.open(image_blob, "a") as f:
			f.write(image_data)
			logging.info("Write Image")
		files.finalize(image_blob)
		im = WebcamImage()
		im.webcam = cam
		im.blob = files.blobstore.get_blob_key(image_blob)
		im.put()
		blob_info = blobstore.BlobInfo.get(im.blob.key())
		logging.info("Fetching for webcam %s" % (cam))
	def get(self):
		"""Simple get request handler."""
	pass

application = webapp.WSGIApplication([(r"/fetchPics/(\d*)/(\d*)$", FetchPage),
                                      (r"/fetchQ", FetchQ)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()


