# Time-In

Group project for Software Engineering class. Clocks in and out employees, calculates pay, and has CRUD operations in the Admin view.

# Get Running

1. Install dependencies (preferably use a python venv). `pip install -r REQUIREMENTS.txt`. Built with Python 12.
2. set environment variables by creating a `.env` file following the `sample.env`
3. `python3 main.py`
4. access app at `http://127.0.0.1:5000/`

# Stack

Python Flask, SQLite, Vue+Vuetify

# Dev

If you need to start over with a fresh database, delete the `instance` folder.

We made the way to make a new page kind of silly. You need to make a `[page].html` in `templates` (see others for example) which has the name of the similarly named `[Page].vue` file in `status/js/components`. You then need to add a route in flask, either making one in `routes/general.py` or creating a new routes file and adding it as a blueprint in `app/__init__.py`. That is the way we chose to do it, but you could just as well make a single page app and do the routing within Vue itself