from sqlalchemy import and_

from applications.models import database, Category, Product, ProductCategory, Order, ProductOrder
from redis import Redis
from applications.configuration import Configuration
from flask import Flask
from sqlalchemy_utils import database_exists, create_database
import json

application = Flask(__name__)
application.config.from_object(Configuration)

if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

database.init_app(application)

with application.app_context() as context:
    with Redis(host=Configuration.REDIS_HOST) as redis:
        while True:
            result = redis.blpop(Configuration.REDIS_BUFFER_LIST)[1].decode("utf-8")
            if result.find("{") == -1:
                if Category.query.filter(Category.name == result).first() is None:
                    category = Category(name=result)
                    database.session.add(category)
                    database.session.commit()
            else:
                result = result.replace('\'', '\"')
                result = json.loads(result)
                name = result.get('name')
                quantity = int(result.get('quantity'))
                price = float(result.get('price'))
                categories = result.get('categories')

                product = Product.query.filter(Product.name.like(name)).first()
                if product is None:
                    product = Product(name=name, quantity=quantity, price=price)
                    database.session.add(product)
                    database.session.commit()

                    for category in categories:
                        pc = ProductCategory(
                            productId=Product.query.filter(Product.name == name).first().id,
                            categoryId=Category.query.filter(Category.name == category).first().id
                        )
                        database.session.add(pc)
                        database.session.commit()
                else:
                    continueFlag = False
                    for category in categories:
                        found = False
                        for prodCat in product.categories:
                            if category == prodCat.name:
                                found = True
                                break
                        if not found:
                            continueFlag = True
                            break
                    if continueFlag:
                        continue

                    newPrice = (product.quantity * product.price + quantity * price) / (product.quantity + quantity)
                    product.quantity += quantity
                    product.price = newPrice
                    database.session.commit()

                    pendingOrders = ProductOrder.query.filter(and_(
                        ProductOrder.productId == product.id,
                        ProductOrder.receivedQuantity != ProductOrder.requestedQuantity
                    )).all()

                    for pendingOrder in pendingOrders:
                        if product.quantity > 0:
                            if product.quantity < pendingOrder.requestedQuantity - pendingOrder.receivedQuantity:
                                pendingOrder.receivedQuantity += product.quantity
                                product.quantity = 0
                            else:
                                product.quantity -= (pendingOrder.requestedQuantity - pendingOrder.receivedQuantity)
                                pendingOrder.receivedQuantity = pendingOrder.requestedQuantity

                                database.session.commit()

                                isComplete = ProductOrder.query.filter(and_(
                                    ProductOrder.orderId == pendingOrder.orderId,
                                    ProductOrder.receivedQuantity != ProductOrder.requestedQuantity
                                )).first() is None

                                if isComplete:
                                    entireOrder = Order.query.filter(Order.id == pendingOrder.orderId).first()
                                    entireOrder.status = "COMPLETE"

                            database.session.commit()
                        else:
                            break
