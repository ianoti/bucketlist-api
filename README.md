[![Coverage Status](https://coveralls.io/repos/github/ianoti/bucketlist-api/badge.svg?branch=develop)](https://coveralls.io/github/ianoti/bucketlist-api?branch=develop)
[![Build Status](https://travis-ci.org/ianoti/bucketlist-api.svg?branch=develop)](https://travis-ci.org/ianoti/bucketlist-api)
[![CircleCI](https://circleci.com/gh/ianoti/bucketlist-api/tree/develop.svg?style=shield&circle-token=0034f3307fcfda36cd98f8d23975d198855bd417)](https://circleci.com/gh/ianoti/bucketlist-api/tree/develop)

# Checkpoint 2 BucketList API
A python backend for an API that will securely store and handle users data on their bucketlists.

It's built on the Flask Micro-framework and security is token based.

## Installation
1. On GitHub clone the repo using the link `git@github.com:ianoti/bucketlist-api.git`
2. install the requirements by running
`pip install -r requirements.txt`
3. Usage of the application will require knowledge of using `curl` commands in the terminal or using the `postman` application for chrome.

## User Manual
`cd` to the directory you cloned the repo in. this current directory should have a `manage.py` file.
Running the application requires initialisation of the database.
do this by running :
- `python manage.py db init`
or
- `python manage.py initdb`

to drop the database and destroy all data in tables run, be careful this operation cannot be undone.
- `python manage.py dropdb`

the application is run by changing the directory to the location that has the `manage.py` file and running.
- `python manage.py runserver`

there are two methods of running tests.
- `python manage.py test`
- `pytest --cov=app tests/ --cov-report html:coverage`
    * this makes a HTML format code coverage report in a coverage directory in the same location as the repo.

the application has a shell interface that is accessed by running `python manage.py shell`

## API Endpoints
|Method | Endpoint | Usage |
|---- | -------| -------------------------|
|POST | `/api/v1/auth/register`| registers a new user to the system|
|POST | `/api/v1/auth/login` | login a user and give a token used for all subsequent requests|
|POST | `/api/v1/bucketlists` | create a new bucketlist for the logged in user|
|GET| `/api/v1/bucketlists`|retrieve a list of all bucketlists by the user|
| GET|  `/api/v1/bucketlists/<id>` | retrieve a single bucketlist given the id|
| PUT| `/api/v1/bucketlists/<id>` | update details of a single bucketlist|
| DELETE| `/api/v1/bucketlists/<id>` | delete a single bucketlist|
|POST|`/api/v1/bucketlists/<id>/items` | add an item to a bucketlist|
|PUT| `/api/v1/bucketlists/<id>/items/<item_id>`| update a bucketlist item|
|DELETE| `/api/v1/bucketlists/<id>/items/<item_id>`| delete a bucketlist item|
#### searching
to carry out a search, a `GET` request is made to the bucketlists endpoint in the following format to retrieve all bucketlists with _list_ in the name
`GET http://localhost:5555/bucketlists?q=list`

#### pagination and limits
the user has the option of limiting the number of bucketlists they can view as well as step through the paginated items. make a `GET` request in the following format `GET http://localhost:5555/bucketlists?limit=20&page=1` the parameter `limit` sets the maximum number of results to display and `page` parameter sets the page of the results to display.

The search, limit and pagination parameters can be combined to make one url for the `GET` request.
`GET http://localhost:5555/bucketlists?limit=20&page=1&q=list`

#### notes
remember to prefix the endpoint names with the server address e.g. `http://localhost/bucketlists`

the secret keys are kept in the `config.py` file as well as the database path configurations. edit these values to customise the application.

### Screenshots
<img width="927" alt="screen shot 2017-02-09 at 19 25 20" src="https://cloud.githubusercontent.com/assets/23119824/22792392/9f6bcabe-eefd-11e6-9afa-412baad5c03b.png">
<img width="557" alt="screen shot 2017-02-09 at 19 27 31" src="https://cloud.githubusercontent.com/assets/23119824/22792457/d9f9c942-eefd-11e6-8313-8b18069be5f7.png">
