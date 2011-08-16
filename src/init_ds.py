"""Entry form to add more cams.
Necessary because the admin console seems to be missing an option to add 
key names."""

import logging
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Webcam
import cgi
import os

class InitPage(webapp.RequestHandler):
  def get(self):
    """Simple get request handler."""
    logging.info("Getting InitPage()")
    cams = Webcam().all()

    template_values = {
        "msg": "",
        "webcam": cams
    }

    path = os.path.join(os.path.dirname(__file__), "init.html")
    self.response.out.write(template.render(path, template_values))

  def post(self):
    """Store camera values in the DataStore."""
    try:
      #TODO: Fix trimming of unicode object
      cname = cgi.escape(self.request.get("cam_name")).lower()
      sourceurl = cgi.escape(self.request.get("source_name"))
      # Cams Dublin City Council 
      if sourceurl == "dc":
        clink = "http://www.dublincity.ie/dublintraffic/" + cname + ".jpg"
      # South Dublin Council Cams
      if sourceurl == "sd":
        clink = "http://traffic.southdublin.ie/TrafficCamImages/" + cname + "/snap.jpg"
      # NRA Cams
      if sourceurl == "nra":
        clink = "http://www.nratraffic.ie/Camera%20Images/" + cname + ".jpg"
      logging.info("Trying to store webcam data:\n"
                   "cam: %s\n"
                   "link: %s\n" % (cname, clink))
      w = Webcam(key_name=cname)

      w.name = cname
      w.image_url = clink
      w.put()
      msg = "Stored data successfully!"
    except Exception, e:
      msg = "Failed to store data: %s" % e
      logging.error("Failed to store data: %s" % e)

    cams = Webcam().all()
    template_values = {
        "msg": msg,
        "webcam": cams
    }

    path = os.path.join(os.path.dirname(__file__), "init.html")
    self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([("/init", InitPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
