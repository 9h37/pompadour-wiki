# Pompadour Wiki

This project was started by [9h37 SAS](http://9h37.fr).

This is a simple yet efficient Wiki engine based on git and Django.

## Features

* Pages are editable as Markdown
* Support of OAuth as an authentification backend, for use with Google Apps
* Backend storage powered by git
* Manage namespaces via folders
* Written in Python2.7 with Django and Twitter-Bootstrap

## Installation

Clone the repository

    git clone git@github.com:9h37/pompadour-wiki.git

Edit the ```pompadour_wiki/pompadour_wiki/settings.sample.py``` settings file to your convenience.

Django will take care of creating your tables.


Create a virtualenv for your app

    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Create your database and super-user

    python manage.py syncdb

Run the app

    python manage.py runserver

PROFIT !


## Pompadour ?

We're based in the North of France and there are many different kind
of potatoes up there. The pompadour is one of them. It's also a very
nice city in the south-west of France.

## Authors

* David Delassus, 9h37 SAS
* Nabil Servais, 9h37 SAS
* Florian Le Goff, 9h37 SAS

## Licence

As detailed in LICENCE.txt
