"""Display index page with most recent pictures.
"""

import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class MainPage(webapp.RequestHandler):
  def get(self):
    """Simple get request handler."""
    self.response.headers["Content-Type"] = "text/html"
    self.response.out.write("Nothing here yet.")
    pass

  def post(self):
    """Simple post request handler."""
    pass


application = webapp.WSGIApplication([("/", MainPage), ],
                                     debug=False)

def main():
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
