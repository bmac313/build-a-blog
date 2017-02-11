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


class BlogPost(db.Model):
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
		# TODO vary the offset by what is sent in the URL
		blog_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY publish_time DESC LIMIT 5")
		t = jinja_env.get_template("main-blog.html")
		page_content = t.render(posts = blog_posts)
		self.response.write(page_content)
		
class NewPost(Handler):
	def get(self):
		t = jinja_env.get_template("new-post.html")
		page_content = t.render()
		self.response.write(page_content)

class PublishPost(Handler):
	# TODO 1: New post does not show up on the blog page on redirect, but does when you refresh / revisit page.
	# TODO 2: Set up error messages for form
	def post(self):
		# Get user input from the form in new-post.html
		post_title = cgi.escape(self.request.get("post-title"), quote=True)
		post_body = cgi.escape(self.request.get("post-body"), quote=True)
		
		# Create a BlogPost object and save it in the database
		new_post = BlogPost(title = post_title, body = post_body)
		new_post.put()
		
		self.redirect("/")

class ViewPost(Handler):
	def get(self):
		pass

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/blog', MainBlog),
	('/newpost', NewPost),
	('/publish', PublishPost),
	webapp2.Route('/blog/post/<post_id:\d+>', ViewPost)
], debug=True)
