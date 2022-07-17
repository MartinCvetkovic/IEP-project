from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt
from sqlalchemy import and_
from roleCheck import roleCheck
from applications.configuration import Configuration
from applications.models import database, Product, Category, ProductOrder, Order
from datetime import datetime

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/search", methods=["GET"])
@roleCheck(role="customer")
def search():
    name = request.args.get("name", "")
    category = request.args.get("category", "")

    result = {}

    if name != "":
        products = Product.query.filter(Product.name.like("%" + name + "%")).all()
    else:
        products = Product.query.all()
    if category != "":
        categories = Category.query.filter(Category.name.like("%" + category + "%")).all()
    else:
        categories = Category.query.all()

    productList = []
    categoryList = []

    for category in categories:
        categoryList.append(category.name)
    for product in products:
        prodDict = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity
        }
        prodCats = []
        for category in product.categories:
            prodCats.append(category.name)
        prodDict['categories'] = prodCats
        productList.append(prodDict)

    result['categories'] = categoryList
    result['products'] = productList

    return jsonify(result), 200


@application.route("/order", methods=["POST"])
@roleCheck(role="customer")
def order():
    requests = request.json.get("requests", None)

    if requests is None:
        return jsonify(message="Field requests is missing."), 400

    i = 0
    overallPrice = 0
    products = []
    productRequests = []
    isPending = False
    for req in requests:
        reqId = req.get("id", "")
        if reqId == "":
            return jsonify(message=f"Product id is missing for request number {i}."), 400
        reqQuantity = req.get("quantity", "")
        if reqQuantity == "":
            return jsonify(message=f"Product quantity is missing for request number {i}."), 400
        if int(reqId) <= 0:
            return jsonify(message=f"Invalid product id for request number {i}."), 400
        if int(reqQuantity) <= 0:
            return jsonify(message=f"Invalid product quantity for request number {i}."), 400
        reqId = int(reqId)
        reqQuantity = int(reqQuantity)
        product = Product.query.filter(Product.id == reqId).first()
        if product is None:
            return jsonify(message=f"Invalid product for request number {i}."), 400
        products.append(product)

        overallPrice += reqQuantity * product.price
        availableQuantity = product.quantity
        if availableQuantity < reqQuantity:
            product.quantity = 0
            fulfilledQuantity = availableQuantity
            isPending = True
        else:
            product.quantity -= reqQuantity
            fulfilledQuantity = reqQuantity

        productRequests.append({"fulfilledQuantity": fulfilledQuantity, "reqQuantity": reqQuantity})

        i += 1

    orderObj = Order(
        overallPrice=overallPrice,
        status="PENDING" if isPending else "COMPLETE",
        timeCreated=datetime.now().isoformat(),
        ownerId=int(get_jwt()["id"])
    )
    database.session.add(orderObj)
    database.session.commit()

    for product in products:

        req = productRequests.pop(0)

        prodOrd = ProductOrder(
            requestedQuantity=req.get("reqQuantity"),
            receivedQuantity=req.get("fulfilledQuantity"),
            buyingPrice=product.price,
            productId=product.id,
            orderId=orderObj.id
        )

        database.session.add(prodOrd)
        database.session.commit()

    return jsonify(id=orderObj.id), 200


@application.route("/status", methods=["GET"])
@roleCheck(role="customer")
def status():
    orders = Order.query.filter(Order.ownerId == int(get_jwt()["id"])).all()
    result = {'orders': []}
    for orderObj in orders:
        orderDict = {
            'price': orderObj.overallPrice,
            'status': orderObj.status,
            'timestamp': datetime.isoformat(orderObj.timeCreated) + "Z",
            'products': []
        }

        prodCats = []
        for product in orderObj.products:
            for category in product.categories:
                prodCats.append(category.name)
            relation = ProductOrder.query.filter(and_(
                    ProductOrder.orderId == orderObj.id,
                    ProductOrder.productId == product.id)
            ).first()
            productDict = {
                "categories": prodCats,
                "name": product.name,
                "price": relation.buyingPrice,
                "received": relation.receivedQuantity,
                "requested": relation.requestedQuantity
            }

            orderDict['products'].append(productDict)

        result['orders'].append(orderDict)

    return jsonify(result), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
