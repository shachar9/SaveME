import web
import urlparse
import json
import saveme
from saveme import StorylineProcessor
        
urls = (
	'/hello/(.*)', 'hello',
	'/', 'home',
	'/go', 'Go'
)

app = web.application(urls, globals())

render = web.template.render('templates')

class hello:        
	def GET(self, name):
		return render.index(name)

class home:        
	def GET(self):
		return render.home()

class Go:
	def POST(self):
		post_args = urlparse.parse_qs(web.data())
		resp = saveme.go(post_args['fb_token'][0])
		web.header('Content-Type', 'application/json')
		return json.dumps(resp);

if __name__ == "__main__":
	app.run()

