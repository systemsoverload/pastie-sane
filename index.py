from flask import Flask, render_template, request
from flask import url_for
from flask.ext.redis import Redis
from werkzeug import SharedDataMiddleware
import bz2
import gzip
import json
import mimetypes
import os
import settings

try:
    import magic
except ImportError:
    magic = None


#Flask Configuration
app = Flask(__name__)
app.config.from_object(settings)

#setup Redis connection
redis = Redis(app)

# NOTE - This is just for debugging, static files should be served elsewhere
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/': os.path.join(os.path.dirname(__file__), 'static')
})


# keep namespace clean...
[
    mimetypes.add_type(typ, ext)
    for typ, ext in (
        ('text/x-sql', '.sql'),
        ('text/x-lua', '.lua'),
    )
    if ext not in mimetypes.guess_all_extensions(typ)
]

_lang_map = {
    # technically, application/* supports unicode and text/* "does not"
    'text/plain': 'text',
    'text/x-python': 'python',
    'text/x-perl': 'perl',
    'application/xml': 'xml',
    'text/x-sh': 'shell',
    'application/json': 'json',
    'application/x-javascript': 'javascript',
    'text/x-sql': 'mysql',
    'text/x-lua': 'lua',
    'text/x-c': 'clike',
}

_mime_map = {
    'text/xml': 'application/xml',
    'text/x-shellscript': 'text/x-sh',
    'text/x-csrc': 'text/x-c',
    'text/x-chdr': 'text/x-c',
}


def _decompress(fd):
    blob = None
    filename = getattr(fd, 'filename', None)

    # if no filename sent... fail
    if not filename:
        return None, None, None

    # ...is gzip encoded?
    try:
        fd.seek(0)
        blob = gzip.GzipFile(fileobj=fd).read()
    except IOError:
        # ...or bz2 encoded?
        try:
            fd.seek(0)
            blob = bz2.decompress(fd.read())
        except IOError:
            pass

    if blob is None:
        fd.seek(0)
        blob = fd.read()
    else:
        # found compressed; fixup name to improve accuracy
        _filename, ext = os.path.splitext(filename)
        if ext in mimetypes.suffix_map:
            _filename, ext = os.path.splitext(
                _filename + mimetypes.suffix_map[ext])
        if ext in mimetypes.encodings_map:
            filename = _filename

    return fd, blob, filename


def _decode(fd):
    fd, blob, filename = _decompress(fd)

    # if standard info is missing... fail
    if not all([blob, filename]):
        return None, None

    # verify valid UTF-8 or... fail
    try:
        blob.decode('UTF-8')
    except UnicodeDecodeError:
        return None, None

    # guess mimetype via both methods; fallback to plain text
    mime_magic = (
        magic.from_buffer(blob, mime=True)
        if magic else 'text/plain'
    )
    mime_filename = mimetypes.guess_type(filename)[0] or 'text/plain'

    # create filters (unique)
    _plain = set(('text/plain',))
    _mimes = set((mime_magic, mime_filename))

    # if there is disagreement between methods, see if one looks like a
    # shorter variation of the other
    if len(_mimes) > 1:
        _short = min(_mimes, key=len)
        _long = mime_filename if _short is mime_magic else mime_magic
        if _long.startswith(_short):
            _mimes.remove(_long)

    # normalize variants
    for mime in _mimes.copy():
        _mime = _mime_map.get(mime, mime)
        if _mime != mime:
            _mimes.add(_mime)
            _mimes.remove(mime)

    # match found?
    if len(_mimes) == 1:
        return blob, _lang_map.get(_mimes.pop(), '')

    # ...drop plain text
    _mimes -= _plain

    # match found?
    if len(_mimes) == 1:
        return blob, _lang_map.get(_mimes.pop(), '')

    # both methods claim to know the mime; either a new _mime_map entry is
    # needed, or one match is more generic than the other

    # ...if detected mime matches user provided mime, run with it
    for x in _mimes:
        if _mime_map.get(fd.mimetype, fd.mimetype).startswith(x):
            return blob, _lang_map.get(x, '')

    # ...if mime exists in _lang_map, run with it
    for x in _mimes:
        if x in _lang_map:
            return blob, _lang_map[x]

    # ...else assume plain text; options exhausted
    return blob, 'text'


#index page
@app.route("/")
def index():
    return render_template('index.html')


#Take in pasted data blob and return base62 db index
@app.route("/", methods=['POST'])
@app.route("/v1/save", methods=['POST'])
def savePaste():
    if 'data' in request.form:
        return_str = '%s'
        data = request.form['data']
    elif 'data' in request.files:
        return_str = url_for('.index', _external=True) + '#%s\n'
        blob, lang = _decode(request.files['data'])
        if (blob, lang) == (None, None):
            return 'Error - upload malformed/rejected/incomplete\n', 400
        data = json.dumps({
            'paste_data': blob,
            'language': lang,
        })
    else:
        return 'Error - missing `data` key\n', 400
    curIndex = redis.dbsize() + 1
    redis.set( curIndex, data )
    return return_str % curIndex


@app.route("/v1/get/<pasteId>", methods=['GET'])
def getPaste(pasteId=""):
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
    app.run(host='0.0.0.0', debug=True, port=8080)
