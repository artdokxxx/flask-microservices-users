from flask import Blueprint, jsonify, request
from flask import redirect, render_template, make_response
from sqlalchemy import exc

from project.api.models import User
from project import db

users_blueprint = Blueprint('users', __name__, template_folder='./templates')


@users_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username', False)
        email = request.form.get('email', False)
        try:
            db.session.add(User(username=username, email=email))
            db.session.commit()
            return redirect('/')
        except:
            return redirect('/')

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('index.pug', users=users)


@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return __success('pong!')


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details"""
    try:
        user = User.query.filter_by(id=int(user_id)).first()
    except ValueError:
        return __error('User does not exist', 404)

    if not user:
        return __error('User does not exist', 404)

    return __success({
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at,
    })


@users_blueprint.route('/users', methods=['GET'])
def get_all_user():
    """Get all users details"""
    result = {'users': []}
    users = User.query.all()
    for user in users:
        result['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at,
        })

    return __success(result)


@users_blueprint.route('/users', methods=['POST'])
def add_user():
    post_data = request.get_json()

    if not post_data:
        return __error('Invalid payload')

    email = post_data.get('email')

    try:
        # check unique email
        user = User.query.filter_by(email=email).first()
        if user:
            return __error('Sorry. That email already exists')

        db.session.add(User(
            username=post_data.get('username'),
            email=email,
        ))
        db.session.commit()
    except exc.IntegrityError:
        db.session().rollback()
        return __error('Invalid payload')

    return __success(f'{email} was added', 201)


def __success(message, code=200):
    response = {
        'status': 'success'
    }
    if type(message) is str:
        response['message'] = message

    if type(message) is dict:
        response['data'] = message

    return make_response(jsonify(response)), code


def __error(message, code=400):
    return make_response(jsonify({
        'message': message,
        'status': 'fail'
    })), code

