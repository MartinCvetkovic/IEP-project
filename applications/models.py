from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductOrder(database.Model):
    __tablename__ = "productorder"

    id = database.Column(database.Integer, primary_key=True)
    requestedQuantity = database.Column(database.Integer, nullable=False)
    receivedQuantity = database.Column(database.Integer, nullable=False)
    buyingPrice = database.Column(database.Float, nullable=False)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)


class ProductCategory(database.Model):
    __tablename__ = "productcategory"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)


class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    quantity = database.Column(database.Integer, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=ProductOrder.__table__, back_populates="products")

    def __repr__(self):
        return f"{self.id},{self.name},{self.price},{self.quantity}"


class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return f"{self.id},{self.name}"


class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    overallPrice = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    timeCreated = database.Column(database.DateTime, nullable=False)
    ownerId = database.Column(database.Integer, nullable=False)

    products = database.relationship("Product", secondary=ProductOrder.__table__, back_populates="orders")
