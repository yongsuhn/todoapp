from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yongsuhn:password@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    # this includes __init__ method
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolist.id'), nullable=False)
    
    def __repr__(self):
        return f'Todo <{self.id}, {self.description}, list{self.list_id}>'

class TodoList(db.Model):
    __tablename__ = 'todolist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'TodoList <{self.id}, {self.name}>'

#db.create_all()   #no need for migration

@app.route('/todos/create', methods=['POST'])
def create_todo():
    # create a new todo item and add into db
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        listid = request.get_json()['list_id']
        todo = Todo(description=description, completed=False, list_id=listid)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['description'] = todo.description
        body['completed'] = todo.completed
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/todolist/create', methods=['POST'])
def create_todolist():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        todolist = TodoList(name=name)
        db.session.add(todolist)
        db.session.commit()
        body['id'] = todolist.id
        body['name'] = todolist.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/todos/<dataid>/set-completed', methods=['POST'])
def set_completed(dataid):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(dataid)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todolist/<listid>/set-completed', methods=['POST'])
def set_todolist_completed(listid):
    try:
        todolist = TodoList.query.get(listid)

        for todo in todolist.todos:
            todo.completed = True
        
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<dataid>', methods=['DELETE'])
def delete_todo(dataid):
    try:
        todo = Todo.query.get(dataid)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success' : True})

@app.route('/todolist/<listid>', methods=['DELETE'])
def delete_todolist(listid):
    try:
        todolist = TodoList.query.get(listid)

        for todo in todolist.todos:
            db.session.delete(todo)
        
        db.session.delete(todolist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html',
        lists=TodoList.query.all(),
        active_list=TodoList.query.get(list_id),
        todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))

if __name__ == '__main__':
    app.run(debug=True)

