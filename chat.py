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
import datetime
import sys
import urllib
from google.appengine.ext import ndb
from google.appengine.api import users
import os
import os.path
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/html"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ChatMessage(ndb.Model):
    user = ndb.StringProperty(required = True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    message = ndb.TextProperty(required = True)
    chat = ndb.StringProperty(required = True)
    def __str__(self):
    	return "%s (%s): %s" % (self.user, self.timestamp, self.message)

CHATS = ['main', 'book', 'flame']


class ChatRoomLandingPage(webapp2.RequestHandler):
    def get(self):
	user = users.get_current_user()
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            
        else:
            
	    self.response.headers['Content-Type'] = 'text/html'
	    messages = ndb.gql("SELECT * FROM ChatMessage ORDER BY timestamp " 					"DESC LIMIT 20")
	    msg_list = messages.fetch()
	    for msg in msg_list:
		msg.deltatime = datetime.datetime.now() - msg.timestamp
	    current_time = datetime.datetime.now() 
            template_values = {
		'title': "TMTC's AppEngine Chat Room",
		'msg_list': messages.fetch(),
		'current_time': current_time,
		'chats': CHATS
		}
	    template = JINJA_ENVIRONMENT.get_template('landing.html')
	    page = template.render(template_values)
	    self.response.out.write(page)
    def post(self):
	user = users.get_current_user()
	if user is None:
	    self.redirect(users.create_login_url(self.request.uri))
	msgtext = self.request.get("message")
	
	if user.nickname() is None or user.nickname() == "":
	    nick = "Anonymous"
	else:
	    nick = user.nickname()
	msg = ChatMessage(user=nick,
			  message=msgtext,
			  chat="chat")
	msg.put()
	sys.stderr.write("****** Just stored message: %s" % msg)
	# Now that we've added the message to the chat, we'll redirect 
	# to the root page, which will make the user's browser refresh to 
	# show the chat including their new message.
	self.redirect('/')

class GenericChatPage(webapp2.RequestHandler):
    def get(self):
	requested_chat = self.request.get("chat", default_value=None)
	current_time = datetime.datetime.now()
	if requested_chat == None or requested_chat not in CHATS:
	    template_params = {
		'title': "Error! Requested chat not found!",
		'chatname': requested_chat,
		'chats': CHATS,
		'current_time': current_time
		}
	    self.redirect('../html/error.html')
	else:
	    messages = ndb.gql("SELECT * FROM ChatMessage WHERE chat = :1 " 
			       "ORDER BY timestamp", requested_chat)
	    for msg in messages:
		msg.deltatime = datetime.datetime.now() - msg.timestamp
	    current_time = datetime.datetime.now() 
	    template_params = {
	    	'title': "TMTC's AppEngine Chat Room",
		'msg_list': messages,
		'chat': requested_chat,
		'chats': CHATS,
		'current_time': current_time
		}
	    template = JINJA_ENVIRONMENT.get_template('multichat.html')
	    page = template.render(template_params)
	    self.response.out.write(page)
    def post(self):
	user = users.get_current_user()
	if user is None:
	    self.redirect(users.create_login_url(self.request.uri))
	msgtext = self.request.get("message")
	if user.nickname() is None or user.nickname() == "":
	    nick = "Anonymous"
	else:
	    nick = user.nickname()
	chat = self.request.get("chat")	
	msg = ChatMessage(user=nick,
			  message=msgtext,
			  chat=chat)
	msg.put()
	sys.stderr.write("****** Just stored message: %s" % msg)
	# Now that we've added the message to the chat, we'll redirect 
	# to the root page, which will make the user's browser refresh to 
	# show the chat including their new message.
	url = self.request.url
	self.redirect(url)

class ChatRoomPoster(webapp2.RequestHandler):
    def get(self):
	self.redirect('../html/poster.html')


app = webapp2.WSGIApplication([('/', ChatRoomLandingPage),
				('/talk', ChatRoomPoster),
				('/enterchat', GenericChatPage)])
