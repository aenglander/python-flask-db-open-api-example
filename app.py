import os, sqlite3

import click

from flask import Flask, current_app, g
from flask.cli import with_appcontext
from flask_restplus import Api, Resource, fields

app = Flask(__name__)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            'todo.sq3', detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(_=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db():
    """Create database schema if nin exists."""
    get_db().execute("""
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT)""")


app.teardown_appcontext(close_db)
app.cli.add_command(init_db)

api = Api(app, version='1.0', title='To Do API',
          description='A example "To Do" API')

ns = api.namespace('todos', description='To Do operations')

todo = api.model('ToDo', {
    'id': fields.Integer(readOnly=True,
                         description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details')
})

todo_change = api.model('ToDo Change', {
    'task': fields.String(required=True, description='The task details')
})


class NotFoundException(Exception):
    pass


class TodoDAO(object):

    def all(self):
        rows = []
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, task FROM todo')
            for row in cursor:
                rows.append({'id': row[0], 'task': row[1]})
        return rows

    def get(self, id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, task FROM todo where id=?', (id, ))
            row = cursor.fetchone()
            if row is None:
                api.abort(404, "Todo {} doesn't exist".format(id))
            return {'id': row[0], 'task': row[1]}

    def create(self, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO todo (task) VALUES (?)',
                (data['task'],))
            data['id'] = cursor.lastrowid
        return data

    def update(self, id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'REPLACE INTO todo (id, task) VALUES (?, ?)',
                (id, data['task']))
        data['id'] = id
        return data

    def delete(self, id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM todo WHERE id=?', (id,))


DAO = TodoDAO()


@ns.route('/')
class TodoList(Resource):
    """Shows a list of all todos, and lets you POST to add new tasks"""

    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        """List all tasks"""
        return TodoDAO().all(), 200

    @ns.doc('create_todo')
    @ns.expect(todo_change)
    @ns.marshal_with(todo, code=201)
    def post(self):
        """Create a new task"""
        return TodoDAO().create(api.payload), 201


@ns.route('/<int:id>')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    """Show a single todo item and lets you delete them"""

    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    @ns.response(404, 'Todo not found')
    def get(self, id):
        """Fetch a given resource"""
        return TodoDAO().get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        """Delete a task given its identifier"""
        TodoDAO().delete(id)
        return None, 204

    @ns.expect(todo_change)
    @ns.marshal_with(todo)
    def put(self, id):
        """Update a task given its identifier"""
        return TodoDAO().update(id, api.payload)
