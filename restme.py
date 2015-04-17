import sys
import os.path as path
import web
import urlparse
import json
import logging
logging.basicConfig(level=logging.INFO)

import saveme
from saveme import StorylineProcessor

basePath = path.dirname(path.abspath(__file__))

urls = (
	'/hello/(.*)', 'hello',
	'/', 'home',
	'/go', 'Go'
)

render = web.template.render(path.join(basePath, 'templates'))

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
		if resp['status'] < 0:
			web.ctx.status = '501 Server Error'
		web.header('Content-Type', 'application/json')
		return json.dumps(resp);

application = web.application(urls, globals()).wsgifunc()

if __name__ == "__main__":
	logging.info('Main')

	app = web.application(urls, globals())
	app.run()

