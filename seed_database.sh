#!/bin/bash

#rm db.sqlite3
rm -rf ./recipeapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations recipeapi
python3 manage.py migrate recipeapi
#python3 manage.py loaddata users
#python3 manage.py loaddata tokens
python3 manage.py loaddata recipes
python3 manage.py loaddata ingredients
python3 manage.py loaddata recipe_pictures

