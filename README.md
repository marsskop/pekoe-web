# Pekoe Web repo
⚠️ **WIP**

A web app for 🌿**PEKOE**🌿, crypto safe tips service. Written in Python3 x Django.

### 🔧 Development guide
#### Setup development environment
```
python3 -m venv ~/.virtualenvs/djangodev
source ~/.virtualenvs/djangodev/bin/activate
python3 -m pip install Django django-bulma django-widget-tweaks
python3 -m django --version
```
#### Migrations and admin creation
```
python3 manage.py makemigrations tips
python3 manage.py migrate
python3 manage.py createsuperuser
```
#### Startup
```
python3 manage.py runserver 0.0.0.0:8000
```
Access server on:
- [127.0.0.1:8000/admin]() -- administration app
- [127.0.0.1:8000/tips]() -- web app

## ⚠️ License
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://www.tldrlegal.com/license/mit-license)