import sqlite3

import click

from flask import Flask, g
from flask.cli import with_appcontext
from flask_restplus import Api, Resource, fields

# Create the Flask application
app = Flask(__name__)


def get_db():
    """
    Helper function to obtain a database connection from the global application
    context.
    :rtype: sqlite.Connection
    """
    if 'db' not in g:
        g.db = sqlite3.connect('todo.sq3',
                               detect_types=sqlite3.PARSE_DECLTYPES)

        g.db.row_factory = sqlite3.Row

    return g.db


# Define the function to close the database connection
def close_db(_=None):
    """
    Remove the database connection from the global application context
    and close the connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Add the close_db to the teardown of the app context tp ensure the
# connection is closed when the Flask application shuts down.
app.teardown_appcontext(close_db)


# Add the command toi initialize the database
@click.command('init-db')
@with_appcontext
def init_db():
    """Create database schema if none exists."""
    get_db().execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detail TEXT)
        """)


# Add the init-db command to the Flask application
app.cli.add_command(init_db)

# Create the Flask Rest+ API definition
api = Api(app, version='1.0', title='To Do API',
          description='A example "To Do" API')

# Create the tasks namespace /tasks
ns = api.namespace('tasks', description='Task operations')

# Create the model for displaying tasks
task_show_model = api.model(
    'Task Show', {
        'id': fields.Integer(readOnly=True,
                             description='The task unique identifier'),
        'detail': fields.String(required=True, description='The task detail')
    })

# Create the model for creating or updating tasks
task_change_model = api.model(
    'Task Change', {
        'detail': fields.String(required=True, description='The task detail')
    })


# Create the resource for the root of the tasks namespace /tasks/
@ns.route('/')
class Tasks(Resource):
    """
    Provides for management of the task resources as a whole such
    as adding a new task or showing a complete list of tasks.
    """

    @ns.doc('list_tasks')
    @ns.marshal_list_with(task_show_model)
    def get(self):
        """List all tasks"""
        rows = []
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, detail FROM tasks')
            for row in cursor:
                rows.append({'id': row[0], 'detail': row[1]})
        return rows, 200

    @ns.doc('create_task')
    @ns.expect(task_change_model, validate=True)
    @ns.marshal_with(task_show_model, code=201)
    def post(self):
        """Create a new task"""
        data = api.payload
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO tasks (detail) VALUES (?)',
                (data['detail'],))
            data['id'] = cursor.lastrowid
        return data, 201



@ns.route('/<int:id>')
@ns.param('id', 'The task identifier')
class Task(Resource):
    """Interact with a particular task item"""

    @ns.doc('get_task')
    @ns.marshal_with(task_show_model)
    @ns.response(404, 'Task not found')
    def get(self, id):
        """Fetch a task"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, detail FROM tasks where id=?', (id,))
            row = cursor.fetchone()
            if row is None:
                api.abort(404, "Task {} doesn't exist".format(id))
            return {'id': row[0], 'detail': row[1]}

    @ns.doc('delete_task')
    @ns.response(204, 'Task deleted')
    def delete(self, id):
        """Delete a task"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id=?', (id,))
        return None, 204

    @ns.expect(task_change_model, validate=True)
    @ns.marshal_with(task_show_model)
    def put(self, id):
        """Set a task"""
        data = api.payload
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'REPLACE INTO tasks (id, detail) VALUES (?, ?)',
                (id, data['detail']))
        data['id'] = id
        return data
