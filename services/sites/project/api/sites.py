# services/users/project/api/users.py


from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc
from project.api.models import Site
# from project.api.models import User
from project import db


sites_blueprint = Blueprint('sites', __name__, template_folder='./templates')
# users_blueprint = Blueprint('users', __name__, template_folder='./templates')


@sites_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        site = request.form['site']
        db.session.add(Site(site=site))
        db.session.commit()
    sites = Site.query.all()
    return render_template('index.html', sites=sites)


@sites_blueprint.route('/sites/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@sites_blueprint.route('/sites', methods=['POST'])
def add_site():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    sitename = post_data.get('site')
    try:
        site_item = Site.query.filter_by(site=sitename).first()
        if not site_item:
            db.session.add(Site(site=sitename))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{sitename} was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That site already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400

@sites_blueprint.route('/sites/<site_id>', methods=['GET'])
def get_single_site(site_id):
    """Get single site details"""
    response_object = {
        'status': 'fail',
        'message': 'Site does not exist'
    }
    try:
        site = Site.query.filter_by(id=int(site_id)).first()
        if not site:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': site.id,
                    'site': site.site,
                    'active': site.active
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404

@sites_blueprint.route('/sites', methods=['GET'])
def get_all_sites():
    """Get all sites"""
    response_object = {
        'status': 'success',
        'data': {
            'sites': [site.to_json() for site in Site.query.all()]
        }
    }
    return jsonify(response_object), 200


# @users_blueprint.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         db.session.add(User(username=username, email=email))
#         db.session.commit()
#     users = User.query.all()
#     return render_template('index.html', users=users)


# @users_blueprint.route('/users/ping', methods=['GET'])
# def ping_pong():
#     return jsonify({
#         'status': 'success',
#         'message': 'pong!'
#     })


# @users_blueprint.route('/users', methods=['POST'])
# def add_user():
#     post_data = request.get_json()
#     response_object = {
#         'status': 'fail',
#         'message': 'Invalid payload.'
#     }
#     if not post_data:
#         return jsonify(response_object), 400
#     username = post_data.get('username')
#     email = post_data.get('email')
#     try:
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             db.session.add(User(username=username, email=email))
#             db.session.commit()
#             response_object['status'] = 'success'
#             response_object['message'] = f'{email} was added!'
#             return jsonify(response_object), 201
#         else:
#             response_object['message'] = 'Sorry. That email already exists.'
#             return jsonify(response_object), 400
#     except exc.IntegrityError as e:
#         db.session.rollback()
#         return jsonify(response_object), 400
# 
# 
# @users_blueprint.route('/users/<user_id>', methods=['GET'])
# def get_single_user(user_id):
#     """Get single user details"""
#     response_object = {
#         'status': 'fail',
#         'message': 'User does not exist'
#     }
#     try:
#         user = User.query.filter_by(id=int(user_id)).first()
#         if not user:
#             return jsonify(response_object), 404
#         else:
#             response_object = {
#                 'status': 'success',
#                 'data': {
#                     'id': user.id,
#                     'username': user.username,
#                     'email': user.email,
#                     'active': user.active
#                 }
#             }
#             return jsonify(response_object), 200
#     except ValueError:
#         return jsonify(response_object), 404


# @users_blueprint.route('/users', methods=['GET'])
# def get_all_users():
#     """Get all users"""
#     response_object = {
#         'status': 'success',
#         'data': {
#             'users': [user.to_json() for user in User.query.all()]
#         }
#     }
#     return jsonify(response_object), 200
