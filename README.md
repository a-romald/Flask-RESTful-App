Flask RESTful Application with token authorization

Flask RESTful Application that implements Flask-Script application structure, restful requests and token authorization.

Features:

    Flask Application project that stores data in mysql database.
    Implements token authorization.
    Requires Python 3

Using:

	After installation the application allows to implement main restful features:
	- Get all products:
	curl -i -X GET 'http://flaskshop.loc/api/products/'

	- Register user:
	curl -XPOST 'http://flaskshop.loc/api/register/' -d "username=sport&password=qwerty&email=sport@mail.ru"
	Also it allows to use non-latin letters in username. In this case it is necessary to transorm it into url encoded string. 

	In python we can type:
	import urllib.parse
	str = 'Вебюзер'
  	str = urllib.parse.quote(str)
  	print(str)

  	In php we can type:
  	<?php $str = 'Вебюзер';
  	$str = urlencode($str);
	echo $str;

	And the result should be placed in curl request like this for word "Вебюзер":
	curl -i -X POST 'http://flaskshop.loc/api/register/' -d "username=%D0%92%D0%B5%D0%B1%D1%8E%D0%B7%D0%B5%D1%80&password=qwerty&email=f@mail.ru"

	-  Login user:
	curl -XPOST 'http://flaskshop.loc/api/login/' -d "email=sport@mail.ru&password=qwerty"
	After login the user gets his token and places it into request

	- Make order:
	curl -XPOST 'http://flaskshop.loc/api/neworder/' -d "token=e48e556a4c554a77b3d42f82b96c3975&products[]=2&products[]=3&products[]=4"
	curl -XPOST 'http://flaskshop.loc/api/neworder/' -d "token=e48e556a4c554a77b3d42f82b96c3975&products%5B0%5D=2&products%5B1%5D=3&products%5B2%5D=1"

	The last string is urlencoded string for [] and could be generated in php like this:
	<?php $ar = [2, 3, 4];
	$str = http_build_query(array('products' => $ar)); //products%5B0%5D=2&products%5B1%5D=3&products%5B2%5D=4
	echo $str;

	Both requests are possible.

	- Get all orders of user:
	curl -i -X GET 'http://flaskshop.loc/api/orders/?token=e48e556a4c554a77b3d42f82b96c3975'

	- Get single order of user:
	curl -i -X GET 'http://flaskshop.loc/api/order/1/?token=e48e556a4c554a77b3d42f82b96c3975'


Init project and install necessary software in Ubuntu 16. 

Install software from the user vagrant:

	- Add user vagrant into ww-data group:
	sudo usermod -a -G www-data vagrant

	- Install and upgrade pip:
	sudo apt-get install python3-pip
	sudo -H pip3 install --upgrade pip
	pip3 -V

	- Install packeges:
	sudo apt-get install build-essential libssl-dev libffi-dev python3-dev 
	sudo apt-get install uwsgi-plugin-python3
	sudo apt-get install libmysqlclient-dev

	- Install virtualwrapper:
	sudo -H pip3 install virtualenv virtualenvwrapper

	- Add environment variable called WORKON_HOME:
	echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
	echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bashrc
	echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
	source ~/.bashrc

	- Create virtual environment for flask:
	mkvirtualenv flaskshop
	If the project developed with python3, then first get path to python3:
	which python3 #/usr/bin/python3
	then type to create virtual environment:
	mkvirtualenv --python=/usr/bin/python3 flaskshop

	- Install packages for application:
	pip3 install Flask
	pip3 install Flask-Script	
	pip3 install mysqlclient
	pip3 install flask-sqlalchemy
	pip3 install flask-wtf
	- Also install uwsgi for virtual environment:
	pip3 install uwsgi

	- Create database shop in mysql server:
	CREATE DATABASE shop;

	- Create directory 'flaskshop' in user home directory and put all files of project into it.
	Run project in port 5000 in virtual environment:
	python run.py runserver

	- Deactivate from virtual environment:
	deactivate
	If we want to activate run command:
	workon flaskshop

	- Install uwsgi globally:
	sudo apt-get install python3-dev
	sudo -H pip3 install uwsgi

	- Allow port 9090:
	sudo ufw allow 9090

	- Run application with uwsgi:
	uwsgi --http-socket :9090 --home /home/vagrant/.virtualenvs/flaskshop --chdir /vagrant/flaskshop --wsgi-file run.py --callable app

	- For python3 and virtual environment to run:
	workon flaskshop
	which uwsgi #/home/vagrant/.virtualenvs/flaskshop/bin/uwsgi
	/home/vagrant/.virtualenvs/flaskshop/bin/uwsgi --http-socket :9090 --home /home/vagrant/.virtualenvs/flaskshop --chdir /vagrant/flaskshop --wsgi-file run.py --callable app

	- Run browser for localhost:9090
	- Delete port 9090:
	sudo ufw delete allow 9090	

	- Create configuration for uwsgi:
	nano /etc/uwsgi/sites/flaskshop.ini

	[uwsgi]
	plugins=python3
	project = flaskshop
	uid = vagrant
	base = /vagrant
	chdir = %(base)/%(project)
	#home = %(base)/.virtualenvs/%(project)
	home = /home/vagrant/.virtualenvs/flaskshop
	wsgi-file = run.py
	callable = app
	master = true
	processes = 5
	socket = /run/uwsgi/%(project).sock
	chown-socket = %(uid):www-data
	chmod-socket = 660
	vacuum = true

	-  Create configuration file for uwsgi service:
	nano /etc/systemd/system/uwsgi.service

	[Unit]
	Description=uWSGI Emperor service
	[Service]
	ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown roma:www-data /run/uwsgi'
	#ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
	ExecStart=/home/vagrant/.virtualenvs/flaskshop/bin/uwsgi --emperor /etc/uwsgi/sites
	Restart=always
	KillSignal=SIGQUIT
	Type=notify
	NotifyAccess=all

	[Install]
	WantedBy=multi-user.target

	- Create config for nginx:
	nano /etc/nginx/sites-available/flaskshop

	server {
	    listen 80;
	    server_name flaskshop.loc www.flaskshop.loc;                
	    location / {
	        include         uwsgi_params;
	        uwsgi_pass      unix:/run/uwsgi/flaskshop.sock;
	    }                                                                
	}

	- Create symbolic link for nginx site:
	sudo ln -s /etc/nginx/sites-available/flaskshop /etc/nginx/sites-enabled/flaskshop	

	- Start uwsgi service:
	sudo systemctl start uwsgi

	- Restart Nginx:
	sudo nginx -t
	sudo service nginx restart

	- In case of changes in /etc/uwsgi/sites/flaskshop.ini file:
	sudo systemctl daemon-reload
	sudo systemctl restart uwsgi

	- Show status of uwsgi:
	sudo systemctl status uwsgi

	- Show running sockets:
	sudo ls /run/uwsgi

	- Make changes in database for utf-8 encoding. Run mysql console:
	USE shop;
	ALTER TABLE users CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;

	- For local machine add lines to /etc/hosts:
	127.0.0.1  flaskshop.loc
	127.0.0.1  www.flaskshop.loc

	- Run application