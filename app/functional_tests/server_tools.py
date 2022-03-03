import heroku3
from decouple import config

HEROKU_API_KEY = config('HEROKU_API_KEY')
HEROKU_STAGING_APP_NAME = config('HEROKU_STAGING_APP_NAME')

def reset_database():
    heroku_conn = heroku3.from_key(HEROKU_API_KEY)
    app = heroku_conn.apps()[HEROKU_STAGING_APP_NAME]
    app.run_command('python app/manage.py flush --no-input')

def create_session_on_server(email):
    heroku_conn = heroku3.from_key(HEROKU_API_KEY)
    app = heroku_conn.apps()[HEROKU_STAGING_APP_NAME]
    session_key = app.run_command(f'python app/manage.py create_session {email}')
    return session_key[0].split()[-1]
