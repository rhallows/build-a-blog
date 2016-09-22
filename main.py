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
import os
import jinja2
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)



class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class blog_posts(db.Model):
    title = db.StringProperty(required = True)
    blogPost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainHandler(Handler):
#    def render_front(self, title="", blogPost="", error=""):
#        self.render("newpost.html", title=title, blogPost=blogPost, error=error, posts=posts
        #    posts = db.GqlQuery("SELECT * FROM blog_posts ORDER BY created DESC")
    def get(self):
        self.render("front.html")


    def post(self):
        title = self.request.get("title")
        blogPost = self.request.get("blogPost")

        if title and blogPost:
            p = blog_posts(title = title, blogPost = blogPost)
            p.put()

            self.redirect('/blog/p.key().id()')
        else:
            error = "We need both a title and a blog post!"
            self.render("front.html", error = error, title=title, blogPost=blogPost)

class BlogRouteHandler(Handler):
    def render_blog(self, title="", blogPost=""):
        posts = db.GqlQuery("SELECT * FROM blog_posts ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, blogPost=blogPost, posts=posts)

    def get(self):
        self.render_blog()

class ViewPostHandler(Handler):
    def get(self, id):
        post = blog_posts.get_by_id(long(id))

        self.render("viewPost.html", title=post.title, blogPost=post.blogPost, post=post)


app = webapp2.WSGIApplication([webapp2.Route('/', MainHandler),
                               webapp2.Route('/blog', BlogRouteHandler),
                               webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
                               ], debug=True)
