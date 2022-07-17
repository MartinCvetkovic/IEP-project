from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, Role
from re import fullmatch
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from roleCheck import roleCheck
import json

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    firstname = request.json.get("forename", "")
    lastname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", None)

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    firstnameEmpty = len(firstname) == 0
    lastnameEmpty = len(lastname) == 0
    isCustomerEmpty = isCustomer is None

    if firstnameEmpty:
        return jsonify(message="Field forename is missing."), 400
    if lastnameEmpty:
        return jsonify(message="Field surname is missing."), 400
    if emailEmpty:
        return jsonify(message="Field email is missing."), 400
    if passwordEmpty:
        return jsonify(message="Field password is missing."), 400
    if isCustomerEmpty:
        return jsonify(message="Field isCustomer is missing."), 400

    regex = r'\b[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not fullmatch(regex, email):
        return jsonify(message="Invalid email."), 400

    if len(password) < 8 or \
            not any(letter.isupper() for letter in password) or \
            not any(letter.islower() for letter in password) or \
            not any(letter.isdigit() for letter in password):
        return jsonify(message="Invalid password."), 400

    if len(User.query.filter(User.email == email).all()) > 0:
        return jsonify(message="Email already exists."), 400

    user = User(email=email, password=password, firstname=firstname, lastname=lastname,
                roleId=2 if isCustomer is True else 3)
    database.session.add(user)
    database.session.commit()

    return Response(status=200)


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = str(request.json.get("password", ""))

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if emailEmpty:
        return jsonify(message="Field email is missing."), 400
    if passwordEmpty:
        return jsonify(message="Field password is missing."), 400

    regex = r'\b[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not fullmatch(regex, email):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(and_(User.email.like(email), User.password.like(password))).first()

    if not user:
        return jsonify(message="Invalid credentials."), 400

    additionalClaims = {
        "id": user.id,
        "forename": user.firstname,
        "surname": user.lastname,
        "roleId": Role.query.filter(Role.id == user.roleId).first().name
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken), 200


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "id": refreshClaims["id"],
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roleId": refreshClaims["roleId"]
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims)), 200


@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def delete():
    email = request.json.get("email", "")

    emailEmpty = len(email) == 0

    if emailEmpty:
        return json.dumps({"message": "Field email is missing."}), 400

    regex = r'\b[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not fullmatch(regex, email):
        return json.dumps({"message": "Invalid email."}), 400

    user = User.query.filter(User.email == email).first()

    if not user:
        return json.dumps({"message": "Unknown user."}), 400

    User.query.filter(User.id == user.id).delete()
    database.session.commit()
    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)
