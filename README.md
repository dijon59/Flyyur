Fyyur
-----

### Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between 
local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows 
with artists as a venue owner.

### How to launch the program
 * Make sure that you are using python3 and have a virtual environment running python3.
 
 * In order to create a virtual environment, type in the following command: `$ virtualenv (yourvirtualenvname)`
 
 * use the following command to access your virtual environment: `$ source (yourvirtualenvname)/bin/activate`
 
 * cd in the project directory `src` and type the following command in your command prompt: `$ pip install -r requirements.txt`
 
 * Make sure that you have Postgres installed on your machine
 
 * if you don't have Postgres, please click on the following link:  [postgres_installation](http://www.postgresqltutorial.com/install-postgresql/)
 
 * Now create a database called `flyyurDB`, you can create the database by running the following command: `$ createdb flyyurDB`
 
 * In you project directory `src` run the following command in your command prompt: `$ flask db migrate` and secondly run
 the following command: `$ flask db upgrade`. These will create the migrations
 
 * Run the development server with following command: `$ python3 app.py`
