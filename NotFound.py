
import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class PageNotFoundHandler(webapp.RequestHandler):
  def get(self):
    logging.info("bad request logged")
    logging.info(self.request.uri)
    
    self.error(404)
    template_values = {'requestName': self.request.uri}
    path = os.path.join(os.path.dirname(__file__), 'templates/not_found.html')    
    self.response.out.write(template.render(path, template_values))
    
application = webapp.WSGIApplication([('/.*', PageNotFoundHandler)], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
