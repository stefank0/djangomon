# Getting started

* -- install Python (3.8) and Git -- 
* git clone https://github.com/stefank0/djangomon.git
* python -m venv env-djangomon
* source env-djangomon/bin/activate
* cd djangomon
* pip install -r requirements.txt
* python manage.py migrate
* python manage.py createsuperuser
* python manage.py test
* python manage.py shell (pokemon.load.load_all() and pokemon.simulator.battle())
* python manage.py runserver
