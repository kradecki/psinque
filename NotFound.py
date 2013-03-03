
import os
import logging
import webapp2
import jinja2

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

class PageNotFoundHandler(webapp2.RequestHandler):
  def get(self):
    logging.error("bad request logged")
    logging.error(self.request.uri)
    
    self.error(404)
    template = jinja_environment.get_template('templates/notFound.html')
    self.response.out.write(template.render(requestName = self.request.uri))
    
app = webapp2.WSGIApplication([('/.*', PageNotFoundHandler)], debug=True)
