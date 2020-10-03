# Getting started

* -- install Python (3.7) and Git -- 
* git clone https://github.com/stefank0/djangomon.git
* python -m venv env-djangomon
* source env-djangomon/bin/activate
* cd djangomon
* pip install -r requirements.txt
* python manage.py migrate
* python manage.py shell
* python manage.py createsuperuser
* python manage.py runserver
* python manage.py test

# Playing Pokemon

* Proposal I: for playing Pokemon with the VisualBoy Advanced emulator
* Proposal II: for playing Pixelmon with a later version

However a check should be made for the later version of Pixelmon with stability and Minecraft 
availablity (used Pixelmon version is 4.1.4 for PixelmonLAN)
For now (23-05-2020) latest generation pokemon moves and types included

# Research Pokemon game versions and type inclusion

* Fairy type introduction seems standard in Pokemon API. Find out if this can be excluded or not