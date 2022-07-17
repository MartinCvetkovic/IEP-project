from flask import Flask, jsonify
from sqlalchemy import func, desc
from applications.configuration import Configuration
from applications.models import database, Category, ProductOrder, Product, ProductCategory
from roleCheck import roleCheck
from flask_jwt_extended import JWTManager

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/productStatistics", methods=["GET"])
@roleCheck(role="admin")
def productStatistics():
    res = database.session.query(
        Product.name,
        func.sum(ProductOrder.receivedQuantity).label('sold'),
        (func.sum(ProductOrder.requestedQuantity) - func.sum(ProductOrder.receivedQuantity)).label('waiting')
    ).filter(
        Product.id == ProductOrder.productId
    ).group_by(
        Product.id
    ).all()

    ret = []
    for row in res:
        ret.append({"name": row.name, "sold": float(row.sold), "waiting": float(row.waiting)})

    return jsonify(statistics=ret), 200


@application.route("/categoryStatistics", methods=["GET"])
@roleCheck(role="admin")
def categoryStatistics():
    cats = Category.query.outerjoin(
        ProductCategory
    ).outerjoin(
        Product
    ).outerjoin(
        ProductOrder
    ).order_by(
        desc(func.sum(ProductOrder.receivedQuantity)), Category.name
    ).group_by(
        Category.id, Category.name
    ).all()

    res = []
    for cat in cats:
        res.append(cat.name)

    return jsonify(statistics=res), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
