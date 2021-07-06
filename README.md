# Djangomon
The most interesting part of this project is the AI that selects the moves. It probably outperforms a human in evaluating the combinations of power, accuracy, priority and recoil damage, by computing probability distributions.
For example, for a Raichu against a Bulbasaur, it could select slam, then thunderbolt, then quick attack, to have the highest probability of winning within 3 turns.

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
