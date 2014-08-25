import os.path
import webapps
from google.appengine.api import user
import ndb	

class ChatRoomPage(webapp2.RequestHandler):
    def get(self):
	user = users.get_current_user()
	if user is None:
	    self.redirect(users.create_login_url(self.request.uri))
	else:
	    self.response.header['Content-Type'] = 'text/html'
	    messages = ndb.gql("SELECT * FROM Chatmessage ORDER BY timestamp")
	    template_values= {
		'title': "TMTC's AppEngine Chat Room",
		'msg_list': messages,
 
		}
 	    path = os.path.join(os.path.dirname(__file__), 'chat-template.html)
	    page = template.render(path, template_values)
	    self.response.out.write(page)
