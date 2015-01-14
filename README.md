
#Pastie-Sane

A sane (read: "working") version of the backend-less Pastie


##Requires:
  * Flask (http://flask.pocoo.org/)
  * Flask-And-Redis (https://github.com/playpauseandstop/Flask-And-Redis)
  * Redis-Py (https://github.com/andymccurdy/redis-py)
  * Redis (http://redis.io/)


##Running:
To run you must first setup your virtual environment

  mkdir venv
  virtualenv --no-site-packages venv
  . venv/bin/activate
  python index.py

It runs on port 8080 by default

##Docker:

To build as a docker image run

  docker build -t pastie .

You can then launch the container with

  docker run -it --link redis:redis -e REDIS_DB=0 pastie

