EPHEMERAL MESSAGING SERVICE
============================

DESIGN
------
This service implements a production-grade, horizontally scalable REST service that implements a simple ephemeral
text message service.

Service is implemented using Python, Django framework, Redis and Postgres.

Why Django?
-----------
Django encourages rapid development and clean, pragmatic design. It's a complete framework with a lot of features
readily available (ORM, Forms, Admin, Templates), but only if you want them.

The current implementation of the service focuses only on building the three APIs. However, since it deals with
"username", there might be a need to implement a user model, login and authentication services for the users.
Django makes all of these readily available for you.

Django REST framework
---------------------
There are a lot of third party applications and packages written for the Django framework that makes it easy to
implement a vast variety of services. For our project, we use "Django REST framework". It is a powerful and
flexible toolkit for building RESTful APIs. Amongst other features, it provides:
- A web browsable API. It is a huge usability win for developers.
- Serialization that supports both ORM and non-ORM data sources. Serializers allow complex data such as
querysets and model instances to be converted to native Python datatypes that can then be easily rendered into
JSON, XML or other content types. Serializers also provide deserialization, allowing parsed data to be converted
back into complex types, after first validating the incoming data.
- Wide variety of customizations.
- Extensive documentation

Storage Solution
----------------
The service implements a hot/cold storage system where expired messages are stored separately from unexpired
messages.  For hot storage, we use Redis. For cold storage we use Postgres.

Redis is an in-memory but persistent on disk database.  It is also a remote data structure server, i.e, it
can be accessed by all the processes of the applications, possibly running on several nodes (horizantally scaled).
Redis can replicate its activity with a master/slave mechanism in order to implement high-availability.

Redis's footprint is quite small. 1 Million small Keys & String Value pairs use approximately 100MB of memory.
Given the scale of data, Redis can be run on several Extra-Large Memory instances. Occasionally shard across instances.

Basically, if you need the service to scale on several nodes sharing the same data, then something like Redis
is a good choice for the hot storage.

For cold storage, we go with a more traditional database - Postgres or MySQL. To scale cold storage data, we could
use sharding. The central database could include data like the 'Users' table, which includes user_id and a pointer to
which shard a user's data can be found on.

Webserver
---------
We use Nginx with Gunicorn as WSGI server.

IMPLEMENTATION SPECIFICS
========================
The service has three RESTful endpoints for accessing data:  POST /chat,  GET /chat/:id and GET /chats/:username.

* POST /chat:
Creates a new text message for passed in username.
Implementation:
Data is inserted into Hot and Cold storages at the same time. Alternate approach would be to insert into Hot storage
only at first, and move it to Cold storage up on expiration. But that involves additional process/callbacks to monitor
keys for expiration. Inserting data into both Hot and Cold storage at the same time obviates the need for such processes
and callbacks. Data inserted into Hot storage (Redis) is inserted with a timeout. Data inserted into Cold storage (DB)
is inserted with an expiration date, computed from the timeout.
Data in Hot storage is automatically purged after the timeout (using Redis's timeout feature).

* GET /chat/:id
Returns the message object for a given id. This service can return both expired or unexpired messages.
Implementation:
Service queries Hot storage for the id. If the id is not found (i.e, expired) in Hot storage, it queries Cold storage
and returns the message object.

* GET /chats/:username
Returns a list of all unexpired texts for the user with the given username. Any texts that are recieved are then
expired.
Implementation:
Service queries Hot storage for user's messages. Returns all the messages as an array of JSON objects. It also
queries Cold storage for these messages and updates expiration date on these messages, marking them as expired.
The service then uses Redis's "Expire" command to set the timeout for these messages in Hot storage to 0, essentially
purging those messages from Hot storage(Redis).


* API UI (Bonus future :-)
This API service provides a simple Web UI for posting message, and retrieving them.
http://159.203.228.191/

* User management:
User Model/Auth/Validation is not explored in current implementation as it is not listed as a requirement.
NOTE: Username validation, case validation (in POST /chats/:username request) is not implemented in this 
version. Django makes it pretty easy to set it up though.

REST API
----------
Basic principles of RESTful web service are considered during this implementation (Client–server separation,
Stateless-ness, Caching, Uniform interface etc).


* Rate limiting
Service implements rate limiting. Users could abuse the system by repeatedly sending the same message over and
over again. One way to address this is by checking if the exact same message exists in the DB. If not, proceed
with storing the message, else, discard. But that's a lot of work on the DB/Server side. Easier alternative is to
implement THROTTLING. A parameter CHAT_THROTTLE_RATE is configured in settings.py. It's set to 100/day out of the box.
If the number of messages from same IP address exceeds 100/day, the service rejects rest of the messages from that
IP for that day.

```
CHAT_THROTTLE_RATE = '100/day'
```
The X-Forwarded-For and Remote-Addr HTTP headers are used to uniquely identify client IP addresses for throttling.
If the X-Forwarded-For header is present then it will be used, otherwise the value of the Remote-Addr header will be
used. See: http://www.django-rest-framework.org/api-guide/throttling/


* Versioning
Implementation provides enough hooks to enable versioning of the API, using Django REST framework. It
can be implemented with just a few config steps as listed here: http://www.django-rest-framework.org/api-guide/versioning/
AcceptHeaderVersioning is best suited for this service, as the requirement spec doesn't indicate a version number
in the POST/GET URLs.

* Pagination
Implementation provides enough hooks to enable pagination of the API, using Django REST framework. It
can be implemented with just a few config steps as listed here:
http://www.django-rest-framework.org/api-guide/pagination/

* Caching
Service already uses a cache (Redis). Additional caching components can be added if necessary.

Misc
----
* Advanced language constructs:
Several Python decorators are implemented/used for efficiency (cleaner and reusable code).

* Test cases and error handling.
A set of test cases are included in Django project to address a few different test scenarios. Errors are handled
through out the code and appropriate message is displayed to the end user. Enough care has been taken in the code
to ensure that there is no data inconsistency, by making use of exception handling.  Testcases are executed with "nose".

* Cleaner code:
Code has been cleaned with "pyflakes" and "pep-8"

* Deployment:
Code is deployed at http://159.203.228.191/ in prod mode.


ADDITIONAL CONSIDERATIONS
-------------------------
Consider the following to build a more advanced service:

- Setup and configure Pingdom for external monitoring of the service.
- Setup and conifgure supervisord (a system that allows its users to monitor and control a number of
processes on UNIX-like operating systems)
- Setup and configure Sentry for Python error reporting.
- Measure application metrics with Datadog, StatsD ( http://docs.datadoghq.com/guides/dogstatsd/ )
- As the service expands into multiple sub-services, consider using a microservies architecture, docker containers etc.
