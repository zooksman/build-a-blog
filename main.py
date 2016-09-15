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

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Index(MainHandler):
	def get(self):
		self.render("create.html", title_error = self.request.get("title_error"), art_error = self.request.get("art_error"))

class ListPosts(MainHandler):
    def get(self):
    	five_posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
    	# five_posts = [five_posts]
        self.render("list.html", posts = five_posts, header = "Recent Posts")
        
class AddPost(MainHandler):
	def post(self):
		post_title = self.request.get("title")
		post_content = self.request.get("art")
		is_title_error = False
		is_art_error = False
		title_error = ""
		art_error = ""
		error = ""
		if (not post_title) or (post_title.strip() == ""):
			title_error = "Please enter a title."
			is_title_error = True
		if (not post_content) or (post_content.strip() == ""):
			art_error = "Please enter some art."
			is_art_error = True
		if is_title_error:
			if error != "":
				error += "&"
			error += "title_error=" + title_error
		if is_art_error:
			if error != "":
				error += "&"
			error += "art_error=" + art_error
		if is_art_error or is_title_error:
			self.redirect("/?" + error)
		else:
			newpost = Post(title = post_title, content = post_content)
			newpost.put()
			self.redirect("/blog/" + str(newpost.key().id()))
			
class ViewPostHandler(MainHandler):
    def get(self, id):
    	id = int(id)
    	if not Post.get_by_id(id):
    		self.response.write("404 post not found")
        else: 
        	self.render("list.html", posts = [Post.get_by_id(id)], header = "Post #" + str(id))

app = webapp2.WSGIApplication([
	('/', Index),
    ('/blog', ListPosts),
    ('/newpost', AddPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)

], debug=True)
