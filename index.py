from __future__ import with_statement
from flask import Flask, render_template, g, request
from werkzeug import SharedDataMiddleware
from contextlib import closing
import os, sqlite3

#DB Configuration
DATABASE = '/tmp/pastie.db'
DEBUG = True
SECRET_KEY = 'random_key_here'

#Flask Configuration
app = Flask(__name__)
app.config.from_object(__name__)

# NOTE - This is just for debugging, static files should be served elsewhere
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
	'/': os.path.join(os.path.dirname(__file__), 'static')
})


def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/", methods=['POST','GET'])
def index():
	return render_template('index.html')

@app.route("/v1/shorten", methods=['GET'])
def shorten_url():
	longurl = request.args.get('longurl', '')
	if longurl:
		g.db.execute('INSERT INTO urls (longurl) VALUES (?)', [longurl])
		file_entry = query_db('SELECT last_insert_rowid()')
		g.db.commit()
		print file_entry[0].key
		return 'True'
	else:
		return 'ERROR - Missing Required Parameter'

@app.route("/v1/expand", methods=['GET'])
def expand_url():
	shorturl = request.args.get('shorturl', '')
	if shorturl:
		return shorturl
	else:
		return 'ERROR - Missing Required Parameter'

if __name__ == "__main__":
	app.run(host='0.0.0.0',debug=True)
