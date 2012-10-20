from flask import Flask, render_template, request
from flask.ext.redis import Redis
from werkzeug import SharedDataMiddleware
import os, settings, base62

#Flask Configuration
app = Flask(__name__)
app.config.from_object(settings)

#setup Redis connection
redis = Redis(app)

# NOTE - This is just for debugging, static files should be served elsewhere
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
	'/': os.path.join(os.path.dirname(__file__), 'static')
})

#index page
@app.route("/")
def index():
	return render_template('index.html')

#Take in pasted data blob and return base62 db index
@app.route("/v1/save", methods=['POST'])
def savePaste():

	curIndex = redis.dbsize() + 1
	redis.set( curIndex, request.form['data'] )
	return str( curIndex )

@app.route("/v1/get/<pasteId>", methods=['GET'])
def getPaste( pasteId = "" ):
	if( pasteId ):
		if redis.exists(pasteId):
			return redis.get(pasteId)
		else:
			return "Error - Non-existant paste id"
	else:
		return "Error - Missing paste id"

@app.route("/debug")
def debug():
	return str(redis.dbsize())

if __name__ == "__main__":
	app.run(host='0.0.0.0',debug=True,port=8080)

# vim: set noexpandtab:
