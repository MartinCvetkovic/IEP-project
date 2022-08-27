from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt
from sqlalchemy import and_
from roleCheck import roleCheck
from applications.configuration import Configuration
from applications.models import database, Product, Category, ProductOrder, Order, ProductCategory
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

    products = Product.query.outerjoin(
        ProductCategory
    ).outerjoin(
        Category
    ).filter(
        and_(
            Product.name.like("%" + name + "%"),
            Category.name.like("%" + category + "%")
        )
    ).all()

    categories = Category.query.outerjoin(
        ProductCategory
    ).outerjoin(
        Product
    ).filter(
        and_(
            Product.name.like("%" + name + "%"),
            Category.name.like("%" + category + "%")
        )
    ).all()

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
        try:
            if int(reqId) <= 0:
                return jsonify(message=f"Invalid product id for request number {i}."), 400
        except ValueError:
            return jsonify(message=f"Invalid product id for request number {i}."), 400
        try:
            if int(reqQuantity) <= 0:
                return jsonify(message=f"Invalid product quantity for request number {i}."), 400
        except ValueError:
            return jsonify(message=f"Invalid product quantity for request number {i}."), 400
        reqId = int(reqId)
        product = Product.query.filter(Product.id == reqId).first()
        if product is None:
            return jsonify(message=f"Invalid product for request number {i}."), 400
        products.append(product)
        i += 1

    for index, req in enumerate(requests):
        product = products[index]
        reqQuantity = int(req.get("quantity", ""))
        overallPrice += reqQuantity * product.price
        availableQuantity = product.quantity
        if availableQuantity < reqQuantity:
            product.quantity = 0
            fulfilledQuantity = availableQuantity
            isPending = True
        else:
            product.quantity -= reqQuantity
            fulfilledQuantity = reqQuantity

        database.session.commit()
        productRequests.append({"fulfilledQuantity": fulfilledQuantity, "reqQuantity": reqQuantity})

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

        for product in orderObj.products:
            prodCats = []
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
