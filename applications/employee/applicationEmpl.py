from flask import Flask, request, Response, jsonify
from flask_jwt_extended import JWTManager
from redis import Redis
from applications.configuration import Configuration
from applications.models import database
import io
import csv
from roleCheck import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@roleCheck(role="employee")
def update():
    file = request.files.get("file", None)
    if file is None:
        return jsonify(message="Field file is missing."), 400
    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    i = 0
    with Redis(host=Configuration.REDIS_HOST) as redis:
        for row in reader:
            if len(row) != 4:
                return jsonify(message=f"Incorrect number of values on line {i}."), 400
            try:
                if int(row[2]) <= 0:
                    return jsonify(message=f"Incorrect quantity on line {i}."), 400
            except ValueError:
                return jsonify(message=f"Incorrect quantity on line {i}."), 400
            try:
                if float(row[3]) <= 0:
                    return jsonify(message=f"Incorrect price on line {i}."), 400
            except ValueError:
                return jsonify(message=f"Incorrect price on line {i}."), 400

            product = {"name": row[1], "quantity": row[2], "price": row[3]}
            categories = []
            for category in row[0].split("|"):
                redis.rpush(Configuration.REDIS_BUFFER_LIST, category)
                categories.append(category)
            product["categories"] = categories
            redis.rpush(Configuration.REDIS_BUFFER_LIST, product.__repr__())
            i += 1

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
