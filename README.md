# CS348-PROJECT
 University of Waterloo CS348 Project

## Installation

Make sure you have python3 and pip installed

Create and activate virtual environment using virtualenv
```bash
$ python -m venv python3-virtualenv
$ source python3-virtualenv/bin/activate
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependencies!

```bash
pip install -r requirements.txt
```

## How to setup the database
You should install MySQL based on your system (https://dev.mysql.com/doc/refman/8.0/en/installing.html)

run
```
$ sudo mysql -u root
$ CREATE USER 'CS348USER'@'localhost' IDENTIFIED BY 'mypassword';
$ GRANT ALL PRIVILEGES ON *.* TO 'CS348USER'@'localhost' WITH GRANT OPTION;
$ FLUSH PRIVILEGES;
$ exit
$ mysql -u myportfolio -p
```
```
$ CREATE DATABASE testDB;
```
For now - manually change the fields in the app.py file, we are not using .env files at the moment.
```
.env file
URL=localhost:5000
MYSQL_HOST=localhost
MYSQL_USER=CS348USER
MYSQL_PASSWORD=mypassword
MYSQL_DATABASE=testDB
```

## Usage

Create a .env file using the example.env template (make a copy using the variables inside of the template)

Start flask development server
```bash
$ export FLASK_ENV=development
$ python app.py
```

You should get a response like this in the terminal:
```
❯ flask run
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

You'll now be able to access the website at `localhost:5000` or `127.0.0.1:5000` in the browser! 
