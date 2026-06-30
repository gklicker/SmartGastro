from collections import Counter

from web_models import (
    Ingredient,
    MenuItem,
    Receipt,
    ReceiptItem,
    StockReceipt,
    db,
)


class BusinessRuleError(ValueError):
    pass


def register_stock_receipt(ingredient, quantity):
    if quantity <= 0:
        raise BusinessRuleError("La cantidad recibida debe ser mayor a cero.")

    stock_before = ingredient.stock
    ingredient.stock += quantity
    movement = StockReceipt(
        ingredient=ingredient,
        quantity=quantity,
        stock_before=stock_before,
        stock_after=ingredient.stock,
    )
    db.session.add(movement)
    return movement


def register_sale(items, payment_method, cashier_id):
    if not items:
        raise BusinessRuleError("Agregá al menos un producto a la venta.")

    normalized_items = []
    ingredient_requirements = {}
    for item_data in items:
        try:
            menu_item_id = int(item_data.get("menu_item_id", 0))
            quantity = int(item_data.get("quantity", 0))
        except (TypeError, ValueError) as exc:
            raise BusinessRuleError("Producto o cantidad inválidos.") from exc
        if quantity <= 0:
            raise BusinessRuleError("La cantidad debe ser mayor a cero.")

        menu_item = db.session.get(MenuItem, menu_item_id)
        if not menu_item or not menu_item.active:
            raise BusinessRuleError("Uno de los platos no está disponible.")
        if not menu_item.recipe:
            raise BusinessRuleError(
                f"{menu_item.name} no tiene una receta configurada."
            )
        normalized_items.append((menu_item, quantity))
        for link in menu_item.recipe:
            requirement = ingredient_requirements.setdefault(
                link.ingredient_id,
                {"ingredient": link.ingredient, "quantity": 0},
            )
            requirement["quantity"] += link.quantity * quantity

    for requirement in ingredient_requirements.values():
        ingredient = requirement["ingredient"]
        if ingredient.stock < requirement["quantity"]:
            raise BusinessRuleError(
                f"Stock insuficiente de {ingredient.name}. "
                f"Disponible: {ingredient.stock:g} {ingredient.unit}."
            )

    receipt = Receipt(
        cashier_id=cashier_id,
        payment_method=payment_method,
        total_amount=sum(item.price * quantity for item, quantity in normalized_items),
    )
    for menu_item, quantity in normalized_items:
        receipt.items.append(
            ReceiptItem(
                menu_item_id=menu_item.id,
                quantity=quantity,
                unit_price=menu_item.price,
            )
        )
    for requirement in ingredient_requirements.values():
        requirement["ingredient"].stock -= requirement["quantity"]
    db.session.add(receipt)
    return receipt, normalized_items


def get_total_sales_stats():
    receipts = Receipt.query.all()
    revenue = sum(receipt.total_amount for receipt in receipts)
    return {
        "count": len(receipts),
        "revenue": revenue,
        "average": revenue / len(receipts) if receipts else 0,
    }


def get_top_items(limit=5):
    quantities = Counter()
    for receipt in Receipt.query.all():
        for line in receipt.items:
            quantities[line.menu_item.name] += line.quantity
    return quantities.most_common(limit)
