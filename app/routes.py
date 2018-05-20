from . import app
from flask import render_template, redirect, url_for
from flask import url_for, jsonify, request, abort, current_app, g
from .models import User, Product, Order, db
from .forms import UserForm, LoginForm
from urllib.parse import unquote #urldecode
import re
from datetime import datetime
from sqlalchemy.exc import OperationalError
import json


# ERRORS
@app.errorhandler(404)
def not_found(e):
	response = jsonify({'status': 404, 'error': 'not found',
						'message': 'invalid resource URI'})
	response.status_code = 404
	return response

@app.errorhandler(500)
def internal_server_error(e):
	response = jsonify({'status': 500, 'error': 'internal server error',
						'message': e.args[0]})
	response.status_code = 500
	return response


class ValidationError(ValueError):
	pass


@app.errorhandler(ValidationError)
def bad_request(e):
	response = jsonify({'status': 400, 'error': 'bad request',
						'message': e.args[0]})
	response.status_code = 400
	return response



# ROUTES
#curl -i -X GET 'http://flaskshop.loc'
@app.route('/', methods=['GET'])
def index():
	return jsonify({'result': 'ok', 'message': 'This is index page'})


#curl -i -X GET 'http://flaskshop.loc/api/products/'
@app.route('/api/products/', methods=['GET'])
def products():
	try:
		allproducts = Product.query.all()
		products = []
		if allproducts :
			for one in allproducts:
				item = {}
				item['id'] = one.id
				item['title'] = one.title
				item['alias'] = one.alias
				products.append(item)    
		return jsonify({'result': 'ok', 'products': products})
	except OperationalError:
		return jsonify({'result': 'error', 'message': 'No database connection'})




#curl -XPOST 'http://flaskshop.loc/api/register/' -d "username=asport&password=123456&email=sport2@mail.ru"
#curl -i -X POST 'http://flaskshop.loc/api/register/' -d "username=%D0%92%D0%B5%D0%B1%D1%8E%D0%B7%D0%B5%D1%80&password=qwerty&email=f4@mail.ru"
@app.route('/api/register/', methods=['POST'])
def register() : 
	try :   
		form = UserForm(request.form)
		errors = {}
		if request.method == 'POST' and form.validate():
			try:
				username = unquote(form.username.data) ##request.form['username']				
			except :
				errors['username'] = ['Not a valid urlencoded string']
				return jsonify({ 'result': 'error', 'errors': errors })
			password = form.password.data #request.form['password']
			email = form.email.data #request.form['email']
			user = User(username = username, email = email)
			user.set_password(password)
			user.generate_auth_token()
			db.session.add(user)
			db.session.commit()
			return jsonify({ 'result': 'ok', 'username': user.username, 'token': user.token })
		else :        
			if form.username.errors :
				errors['username'] = form.username.errors
			if form.password.errors :
				errors['password'] = form.password.errors
			if form.email.errors :
				errors['email'] = form.email.errors
		return jsonify({ 'result': 'error', 'errors': errors })
	except OperationalError:
		return jsonify({ 'result': 'error', 'message': 'No database connection' })
	


#curl -XPOST 'http://flaskshop.loc/api/login/' -d "email=sport@mail.ru&password=123456"
@app.route('/api/login/', methods=['POST'])
def login() :
	try :
		form = LoginForm(request.form)
		errors = {}
		if request.method == 'POST' and form.validate():
			email = form.email.data
			password = form.password.data
			user = User.query.filter_by(email=email).first()
			if user is None or not user.verify_password(password):
				errors['password'] = ['Incorrect user or password']
				return jsonify({ 'result': 'error', 'errors': errors })
			return jsonify({ 'result': 'ok', 'username': user.username, 'token': user.token })
		else :        
			if form.password.errors :
				errors['password'] = form.password.errors
			if form.email.errors :
				errors['email'] = form.email.errors
		return jsonify({ 'result': 'error', 'errors': errors })
	except OperationalError:
		return jsonify({ 'result': 'error', 'message': 'No database connection' })



   


#curl -XPOST 'http://flaskshop.loc/api/neworder/' -d "token=e48e556a4c554a77b3d42f82b96c3975&products[]=2&products[]=3&products[]=4"
#curl -XPOST 'http://flaskshop.loc/api/neworder/' -d "token=e48e556a4c554a77b3d42f82b96c3975&products%5B0%5D=2&products%5B1%5D=3&products%5B2%5D=1"
@app.route('/api/neworder/', methods=['POST'])
def neworder() :
	try :
		token = request.form.get('token')    
		prods = request.form.getlist("products[]")
		errors = {}
		rf = request.form
		reg = re.compile( r"^products" ) #only 'products' from POST data taken into account
		items = [] # for products%5B1%5D - urlencoded products[]
		for key in rf.keys():
			if reg.match(key) :            
				try :
					pr = int(rf[key])
					pr = str(pr)
					items.append(pr)
				except:
					pass
		products = prods + items
		products = list(set(products))
		# Add order to database
		#user = User.query.filter_by(token=token).first()
		try :
			User.verify_auth_token(token)
			user = g.user #from User.verify_auth_token(token)
			user_id = user.id
			order = Order()
			order.user_id = user_id
			for prod_id in products :
				p = Product.query.get(prod_id)
				order.products.append(p)
			db.session.add(order)
			db.session.commit()
			return jsonify({ 'result': 'ok', 'token': token, 'products': products })
		except AttributeError :
			errors['token'] = ['Incorrect token']
			return jsonify({ 'result': 'error', 'errors': errors })
		
	except OperationalError:
		return jsonify({ 'result': 'error', 'message': 'No database connection' })




#curl -i -X GET 'http://flaskshop.loc/api/orders/?token=e48e556a4c554a77b3d42f82b96c3975'
@app.route('/api/orders/', methods=['GET'])
def orders() :
	try:
		token = request.args.get("token")
		errors = {}
		try :
			User.verify_auth_token(token)
			user = g.user #from User.verify_auth_token(token)
			user_id = user.id
			allorders = Order.query.filter_by(user_id = user_id).all()
			orders = []
			for one in allorders:
				item = {}
				item['id'] = one.id
				item['created'] = one.created
				products = one.products.all()
				items = []
				for product in products :
					pr = {}
					pr['id'] = product.id
					pr['title'] = product.title
					pr['alias'] = product.alias
					items.append(pr)
				item['products'] = items
				orders.append(item)
			return jsonify({ 'result': 'ok', 'token': token, 'orders': orders })
		except AttributeError :
			errors['token'] = ['Incorrect token']
			return jsonify({ 'result': 'error', 'errors': errors })
	except OperationalError:
		return jsonify({'result': 'error', 'message': 'No database connection'})




#curl -i -X GET 'http://flaskshop.loc/api/order/1/?token=e48e556a4c554a77b3d42f82b96c3975'
@app.route('/api/order/<num>/', methods=['GET'])
def order(num) :
	try :
		token = request.args.get("token")
		errors = {}
		try :
			User.verify_auth_token(token)
			user = g.user #from User.verify_auth_token(token)
			user_id = user.id
			order = Order.query.get(num)
			#order = Order.query.filter_by(id = num).first()
			if order is None :
				errors['order'] = ['Incorrect order']
				return jsonify({ 'result': 'error', 'errors': errors })
			owner_id = order.user_id
			if owner_id != user_id :
				errors['order'] = ['Incorrect order token']
				return jsonify({ 'result': 'error', 'errors': errors })
			products = order.products.all()
			items = []
			for product in products :
				item = {}
				item['id'] = product.id
				item['title'] = product.title
				item['alias'] = product.alias
				items.append(item)
			return jsonify({ 'result': 'ok', 'token': token, 'order': num, 'products': items })
		except AttributeError :
			errors['token'] = ['Incorrect token']
			return jsonify({ 'result': 'error', 'errors': errors })
	except OperationalError:
		return jsonify({'result': 'error', 'message': 'No database connection'})
	
