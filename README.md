# Cinema Social Media

This is an academic project for a Cinema Themed social media. We used the DJango
framework and built an SSR based website (with the extra challenge of not using any
custom JS) that also integrates with a movie database (in this case TMBD) to dynamically
retrieve the newest movies and keep the database always in sync.

## Configuration

This project requires:

1. Python 3.10
2. [Pipenv](https://pipenv.pypa.io/en/latest/index.html)
    - A dependency and venv manager for python inspired on bundler, composer, npm,
      cargo...
3. Setting up the `.env` file

In order to be able to correctly set up and run the project, you MUST configure your
.env
file, for this you can copy the `.env.example` on the root of the project. One tip is to
use the SQLite configuration suggested on the example's comment.

At the end, your `.env` file should look something like this:

```dotenv
DEBUG=1
SECRET_KEY='BAD_SECRET_KEY'
DATABASE_URL='sqlite:///db.sqlite3'
TMDB_API_KEY='your TMDB v4 api key'
```

## Build & Run

To run the build and run the project, the first thing to be done is installing the
dependencies and activating the environment (tip: every time you activate the
environment the `.env` is loaded). For this, you can do:

```bash
# Installs the dependencies and setup the venv
pipenv install

# Activates the venv in the current shell (also loads the .env)
pipenv shell --anyway
```

*Obs: the `--anyway` argument is optional, it allows you to have nested environments,
which are known to cause some issues, but is useful to reload the .env*

Now, with the environment active, you can go into the app folder `cd app`, and apply
the database migrations:

```bash
# Inside the app folder 

# Apply database migrations
python manage.py migrate
```

With all of that done, now you only need to actually run the development server, for
that, run:

```bash
# Again, inside the app folder

# Run the dev server
python manage.py runserver
```

## Docker

If you prefer, you can skip the pipenv configuration (.env will still be needed, at 
least for the API keys) and use docker-compose instead. For that, simply run:

```bash
# Turn on the containers detached from terminal
docker-compose up --build -d

# To see the logs, use
docker-compose logs --follow
```

To shut the app down, use:

```bash
# Shuts down the containers, add -v to also delete the database data
docker-compose down
```

## Improvements

Due to the timelines, we had to sacrifice some things we'd like to implement, namely:

1. More complete unit tests
    - We initially started building unit tests, but we had to abandon them in order to
      meet the timelines we had.
2. Algorithmic recommendations
    - One of the things we had thought of doing but also couldn't in time was making a
      recommendation algorithm to suggest posts of movies that meets the tastes of the
      user.
3. Implement actual i18n support for both pt-BR and en-US. Currently, only pt-BR is
   available.
