Open API Example App w/Python, Flask, and DB API
================================================

Overview
--------

This project shows, very quickly, how to utilize common
frameworks and libraries to quickly and easily build an 
Open API v2 based REST service using Python.

*This is not an example of a well layed out Python or Flask
project. It is built for simplicity in order to see the source
code for the example in one file in order to make it easier to
follow for beginners.*

Installation
------------

### Installing the Application

1. [Install Pipenv](https://pipenv.readthedocs.io/en/latest/install)
(if necessary)
2. Clone or download the repository
3. From the project directory, install the dependencies via pipenv
    ```bash
    pipenv install
    ```

### Setting Up the Database

If you are running this example for the first time or have
deleted the database file, `todo.sq3`, then you will need to
create the database and schema. You can do so via a Flask command:

```bash
flask init-db
```

*The command will only affect the database if the schema did not
previously exist. If you want to start over and reset the
database, simply delete the file `todo.sq3` and run the `init-db`
command.*

Running the Application
-----------------------

### Start the Server

As this is a standard Flask application, just run it as any
other flask application via the `run` command in the project
directory. Here is an example of starting the app in develop
mode:

```bash
FLASK_ENV=develop flask run
```

### Interact With the Server

The Flask REST+ plugin provides a Web based Swagger UI interface
that can be accessed in the browser. If you have utilize the
default settings for host and port, you can access the Swagger UI
at [http://localhost:5000/](http://localhost:5000/)

References
----------

This project utilizes on the following items which can be
investigated further should you choose:

* [Flask](http://flask.pocoo.org)
* [Flask REST+](https://flask-restplus.readthedocs.io)
* [DB-API Interface for for SQLite](https://docs.python.org/3/library/sqlite3.htm)
* [Open API Specification v2 \[OAS **2**\]](https://swagger.io/docs/specification/2-0/)
* [SQLite](https://www.sqlite.org)
* [Pipenv](https://pipenv.readthedocs.io)
