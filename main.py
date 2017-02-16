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
import string
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
		self.response.write("Something went wrong while loading this page! If you'd like more info on the error, you can search for the error code below: <br />" + str(error_code))

		
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
		error_msg = self.request.get("error")
		t = jinja_env.get_template("new-post.html")
		page_content = t.render(error = error_msg)
		self.response.write(page_content)

		
class PublishPost(Handler):
	def post(self):
		# Get user input from the form in new-post.html
		post_title = cgi.escape(self.request.get("post-title"), quote=True)
		post_body = cgi.escape(self.request.get("post-body"), quote=True)
		
		# Initialize a string for the Key Name to be used in the new BlogPost below.
		# The Key Name will be the post title with hyphens separating each word.
		key_name_str = ""
		
		# Split the words and put them into a list called title_words.
		title_words = post_title.lower().split()
		
		# Remove punctuation from each word, add each word to new list
		title_words_no_punc = []
		for word in title_words:	
			word_no_punc = ""
			for chara in word:
				if chara not in string.punctuation:
					word_no_punc += chara
			title_words_no_punc.append(word_no_punc)
			
		# Compare the entered title to other titles in the database, to make sure the title does not already exist.
		posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY publish_time DESC")
		error_msg = ""
		error_occured = False
		
		# If another post has the same title (case insensitive), return an error.
		for post in posts:
			if cgi.escape(post.title.lower()) == cgi.escape(post_title.lower()):
				error_occured = True
		
		if error_occured == True:
			error_msg = "There is already another post with that ID (note: IDs are obtained through the post title, lowercase and with punctuation removed)."
			self.redirect("/newpost?error=error_msg")
		else:
			# Re-construct the string using join() with '-' as the separator.
			key_name_str = "-".join(title_words_no_punc)
			
			
			# Create a BlogPost object and save it in the database
			new_post = BlogPost(key_name = key_name_str, title = post_title, body = post_body)
			new_post.put()
			
			self.redirect("/blog/post/" + key_name_str)

		
class ViewPost(Handler):
	def get(self, post_id):
		post_to_display = BlogPost.get_by_key_name(post_id)
		
		if not post_to_display:
			self.renderError(404)
		else:
			t = jinja_env.get_template("view-post.html")
			page_content = t.render(post_title = post_to_display.title,
									post_body = post_to_display.body,
									timestamp = post_to_display.publish_time)
			
			self.response.write(page_content)

		
app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/blog', MainBlog),
	('/newpost', NewPost),
	('/publish', PublishPost),
	webapp2.Route('/blog/post/<post_id:.+>', ViewPost)
], debug=True)
