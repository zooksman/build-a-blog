#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Post(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    content = db.TextProperty(required = True)

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Hoo boy that's an error.")

class MainHandler(Handler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Index(Handler):
	def get(self):
		
		t = jinja_env.get_template("front.html")
        response = t.render()
        self.response.write(response)

class ListPosts(Handler):
    def get(self):
    	five_posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
    	five_posts = [five_posts]
        t = jinja_env.get_template("list.html")
        response = t.render(five_posts = five_posts)
        self.response.write(response)
        
class AddPost(Handler):
	def post(self):
		
		t = jinja_env.get_template("create.html")
        response = t.render()
        self.response.write(response)

app = webapp2.WSGIApplication([
	('/', Index),
    ('/blog', ListPosts),
    ('/newpost', AddPost)
], debug=True)
