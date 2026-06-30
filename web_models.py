from datetime import datetime

import bcrypt
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="admin")
    active = db.Column(db.Boolean, nullable=False, default=True)

    def set_password(self, password):
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False, default="u")
    stock = db.Column(db.Float, nullable=False, default=0)
    min_stock = db.Column(db.Float, nullable=False, default=0)
    icon = db.Column(db.String(12), nullable=False, default="📦")
    recipe_links = db.relationship(
        "RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan"
    )
    stock_receipts = db.relationship(
        "StockReceipt", back_populates="ingredient", cascade="all, delete-orphan"
    )

    @property
    def low_stock(self):
        return self.stock <= self.min_stock


class StockReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id"), nullable=False
    )
    quantity = db.Column(db.Float, nullable=False)
    stock_before = db.Column(db.Float, nullable=False)
    stock_after = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ingredient = db.relationship("Ingredient", back_populates="stock_receipts")


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    active = db.Column(db.Boolean, nullable=False, default=True)
    icon = db.Column(db.String(12), nullable=False, default="🍽️")
    recipe = db.relationship(
        "RecipeIngredient", back_populates="menu_item", cascade="all, delete-orphan"
    )


class RecipeIngredient(db.Model):
    menu_item_id = db.Column(
        db.Integer, db.ForeignKey("menu_item.id"), primary_key=True
    )
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id"), primary_key=True
    )
    quantity = db.Column(db.Float, nullable=False)
    menu_item = db.relationship("MenuItem", back_populates="recipe")
    ingredient = db.relationship("Ingredient", back_populates="recipe_links")


class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cashier_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False, default="cash")
    total_amount = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cashier = db.relationship("User")
    items = db.relationship(
        "ReceiptItem", back_populates="receipt", cascade="all, delete-orphan"
    )


class ReceiptItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipt.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    receipt = db.relationship("Receipt", back_populates="items")
    menu_item = db.relationship("MenuItem")

    @property
    def subtotal(self):
        return self.quantity * self.unit_price
