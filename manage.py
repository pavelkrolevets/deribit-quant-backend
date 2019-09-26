from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from celery import Celery
from application.app import app, db

migrate = Migrate(app, db)
manager = Manager(app)
server = Server(host="0.0.0.0", port=5002, threaded=True, ssl_crt='/etc/letsencrypt/live/ton618.tech/fullchain.pem', ssl_key='/etc/letsencrypt/live/ton618.tech/privkey.pem')

# migrations
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", server)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


if __name__ == '__main__':
    manager.run()
