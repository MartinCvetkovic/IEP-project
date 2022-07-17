from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class Role(database.Model):
    __tablename__ = "roles"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    users = database.relationship("User", back_populates="roles")


class User(database.Model):
    __tablename__ = "users"

    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    firstname = database.Column(database.String(256), nullable=False)
    lastname = database.Column(database.String(256), nullable=False)
    roleId = database.Column(database.Integer, database.ForeignKey("roles.id"), nullable=False)

    roles = database.relationship("Role", back_populates="users")
