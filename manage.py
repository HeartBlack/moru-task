import click
from flask.cli import FlaskGroup

from app.extensions import bcrypt, db
from app.models.models import Role, User
from wsgi import app

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    # db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def createsuperuser():
    print("calling")
    while True:
        username = click.prompt("Username")
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User.query.filter_by(username=username).first()

        if user:
            click.echo("Username is already registered. Please try another one.")
        else:
            user = User(username=username, password=hashed_password, user_type=Role.ADMIN)
            db.session.add(user)
            db.session.commit()
            click.echo(f"Superuser created successfully. ID: {user.id}, Username: {user.username}")
            break


if __name__ == "__main__":
    cli()
