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


class Post(db.Model):
	title = db.StringProperty(required=True)
	body = db.TextProperty(required=True)
	publish_time = db.DateTimeProperty(auto_now_add=True)

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):
	"""Base request handler class for the entire app"""
	def renderError(self, error_code):
		self.error(error_code)
		self.response.write("Something went wrong while loading this page! If you'd like more info on the error, you can search for the error code above.")

class MainHandler(Handler):
	def get(self):
		self.redirect('/blog')
		
class MainBlog(Handler):
	def get(self):
		t = jinja_env.get_template("main-blog.html")
		page_content = t.render(post_title = "Test", post_body = "lorem ipsum text")
		self.response.write(page_content)
		
class NewPost(Handler):
	def get(self):
		t = jinja_env.get_template("new-post.html")
		page_content = t.render()
		self.response.write(page_content)

class ViewPost(Handler):
	def get(self):
		pass

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/blog', MainBlog),
	('/newpost', NewPost),
	webapp2.Route('/post/<post_id:\d+>', ViewPost)
], debug=True)
