from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, User
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

done = False
while not done:
    try:
        if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"])

        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message="Production migration")
            upgrade()

            adminRole = Role(name="admin")
            cutomerRole = Role(name="customer")
            employeeRole = Role(name="employee")

            database.session.add(adminRole)
            database.session.add(cutomerRole)
            database.session.add(employeeRole)
            database.session.commit()

            admin = User(
                email="admin@admin.com",
                password="1",
                firstname="admin",
                lastname="admin",
                roleId=1
            )

            database.session.add(admin)
            database.session.commit()

        done = True
    except Exception as error:
        print(error)