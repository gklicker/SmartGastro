import os
from collections import Counter
from datetime import date, datetime, timedelta
from functools import wraps

import click
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from external.weather import geocode, get_forecast_for_date
from services.web_service import (
    BusinessRuleError,
    get_top_items,
    get_total_sales_stats,
    register_sale,
    register_stock_receipt,
)
from web_models import (
    Ingredient,
    MenuItem,
    Receipt,
    ReceiptItem,
    RecipeIngredient,
    StockReceipt,
    User,
    db,
)


load_dotenv()

ICONS = [
    "📦", "🥯", "🥩", "🍗", "🧀", "🥬", "🍅", "🧅", "🥒", "🥔",
    "🍟", "🥫", "🧂", "🥚", "🥛", "🧃", "🥤", "☕", "🍔", "🌭",
    "🍕", "🌮", "🥪", "🍽️",
]
UNITS = ["u", "g", "kg", "ml", "l"]


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-production"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL", "sqlite:///smartgastro.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    def ensure_schema():
        """Pequeña migración compatible con la base creada por la primera versión web."""
        db.create_all()
        inspector = inspect(db.engine)
        upgrades = {
            "ingredient": ("icon", "ALTER TABLE ingredient ADD COLUMN icon VARCHAR(12) NOT NULL DEFAULT '📦'"),
            "menu_item": ("icon", "ALTER TABLE menu_item ADD COLUMN icon VARCHAR(12) NOT NULL DEFAULT '🍽️'"),
        }
        for table_name, (column_name, statement) in upgrades.items():
            if table_name not in inspector.get_table_names():
                continue
            columns = {column["name"] for column in inspector.get_columns(table_name)}
            if column_name not in columns:
                db.session.execute(text(statement))
        db.session.commit()

    with app.app_context():
        ensure_schema()

    @app.context_processor
    def inject_catalogs():
        return {"icon_catalog": ICONS, "unit_catalog": UNITS}

    def login_required(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            user = (
                db.session.get(User, session.get("user_id"))
                if session.get("user_id")
                else None
            )
            if not user or not user.active:
                session.clear()
                flash("Iniciá sesión para continuar.", "warning")
                return redirect(url_for("login"))
            return view(**kwargs)

        return wrapped_view

    @app.context_processor
    def inject_user():
        user = db.session.get(User, session.get("user_id")) if session.get("user_id") else None
        return {"current_user": user}

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = User.query.filter_by(login=request.form.get("login", "").strip()).first()
            if user and user.active and user.check_password(request.form.get("password", "")):
                session.clear()
                session["user_id"] = user.id
                return redirect(url_for("dashboard"))
            flash("Usuario o contraseña incorrectos.", "danger")
        return render_template("login.html")

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    @login_required
    def dashboard():
        weather = None
        weather_error = None
        location = request.args.get("location", "Buenos Aires").strip()
        selected_date = request.args.get("date", date.today().strftime("%d/%m/%Y"))
        selected_time = request.args.get("time", "")
        try:
            forecast_date = datetime.strptime(selected_date, "%d/%m/%Y").date()
            latitude, longitude, place_name, country = geocode(location)
            weather = get_forecast_for_date(
                latitude, longitude, forecast_date, selected_time or None
            )
            weather["place"] = f"{place_name}, {country}"
        except Exception as exc:
            weather_error = str(exc) or "El servicio climático no está disponible."
        low_stock = Ingredient.query.filter(
            Ingredient.stock <= Ingredient.min_stock
        ).all()
        weather_alert = bool(
            weather
            and (
                weather.get("rain_probability", 0) >= 50
                or weather.get("rain_mm", 0) > 0
                or weather.get("hour_rain_probability", 0) >= 50
                or weather.get("hour_rain_mm", 0) > 0
            )
        )
        return render_template(
            "dashboard.html",
            weather=weather,
            weather_error=weather_error,
            location=location,
            selected_date=selected_date,
            selected_time=selected_time,
            today=date.today().strftime("%d/%m/%Y"),
            max_forecast_date=(date.today() + timedelta(days=15)).strftime("%d/%m/%Y"),
            low_stock=low_stock,
            weather_alert=weather_alert,
            sales_count=Receipt.query.count(),
            revenue=sum(receipt.total_amount for receipt in Receipt.query.all()),
        )

    @app.route("/ingredients", methods=["GET", "POST"])
    @login_required
    def ingredients():
        if request.method == "POST":
            try:
                stock = float(request.form["stock"])
                min_stock = float(request.form["min_stock"])
                if stock < 0 or min_stock < 0:
                    raise ValueError("El stock no puede ser negativo.")
                db.session.add(
                    Ingredient(
                        name=request.form["name"].strip(),
                        unit=request.form["unit"].strip(),
                        stock=stock,
                        min_stock=min_stock,
                        icon=request.form.get("icon", "📦"),
                    )
                )
                db.session.commit()
                flash("Ingrediente creado.", "success")
            except (ValueError, IntegrityError) as exc:
                db.session.rollback()
                flash(f"No se pudo crear el ingrediente: {exc}", "danger")
            return redirect(url_for("ingredients"))
        return render_template(
            "ingredients.html",
            ingredients=Ingredient.query.order_by(Ingredient.name).all(),
            stock_receipts=StockReceipt.query.order_by(
                StockReceipt.created_at.desc()
            ).limit(20).all(),
        )

    @app.post("/ingredients/<int:ingredient_id>/receive")
    @login_required
    def receive_ingredient(ingredient_id):
        ingredient = db.get_or_404(Ingredient, ingredient_id)
        try:
            quantity = float(request.form["quantity"])
            movement = register_stock_receipt(ingredient, quantity)
            db.session.commit()
            flash(
                f"Ingreso registrado: {ingredient.name} pasó de "
                f"{movement.stock_before:g} a {movement.stock_after:g} "
                f"{ingredient.unit}.",
                "success",
            )
        except (BusinessRuleError, ValueError, SQLAlchemyError) as exc:
            db.session.rollback()
            flash(f"No se pudo registrar el ingreso: {exc}", "danger")
        return redirect(url_for("ingredients"))

    @app.post("/ingredients/<int:ingredient_id>/edit")
    @login_required
    def edit_ingredient(ingredient_id):
        ingredient = db.get_or_404(Ingredient, ingredient_id)
        try:
            stock = float(request.form["stock"])
            min_stock = float(request.form["min_stock"])
            if stock < 0 or min_stock < 0:
                raise ValueError("El stock no puede ser negativo.")
            ingredient.name = request.form["name"].strip()
            ingredient.unit = request.form["unit"].strip()
            ingredient.icon = request.form.get("icon", ingredient.icon)
            ingredient.stock = stock
            ingredient.min_stock = min_stock
            db.session.commit()
            flash("Ingrediente actualizado.", "success")
        except (ValueError, IntegrityError) as exc:
            db.session.rollback()
            flash(f"No se pudo actualizar: {exc}", "danger")
        return redirect(url_for("ingredients"))

    @app.post("/ingredients/<int:ingredient_id>/delete")
    @login_required
    def delete_ingredient(ingredient_id):
        ingredient = db.get_or_404(Ingredient, ingredient_id)
        try:
            db.session.delete(ingredient)
            db.session.commit()
            flash("Ingrediente eliminado.", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("No se puede eliminar un ingrediente usado en ventas o recetas.", "danger")
        return redirect(url_for("ingredients"))

    @app.route("/menu", methods=["GET", "POST"])
    @login_required
    def menu():
        if request.method == "POST":
            try:
                price = float(request.form["price"])
                if price <= 0:
                    raise ValueError("El precio debe ser mayor a cero.")
                item = MenuItem(
                    name=request.form["name"].strip(),
                    price=price,
                    description=request.form.get("description", "").strip(),
                    icon=request.form.get("icon", "🍽️"),
                )
                db.session.add(item)
                db.session.flush()
                recipe_count = 0
                for ingredient in Ingredient.query.order_by(Ingredient.name).all():
                    quantity = request.form.get(
                        f"ingredient_{ingredient.id}", type=float
                    )
                    if not quantity:
                        continue
                    if quantity <= 0:
                        raise ValueError("Las cantidades de la receta deben ser positivas.")
                    db.session.add(
                        RecipeIngredient(
                            menu_item_id=item.id,
                            ingredient_id=ingredient.id,
                            quantity=quantity,
                        )
                    )
                    recipe_count += 1
                if recipe_count == 0:
                    raise ValueError("Agregá al menos un ingrediente a la receta.")
                db.session.commit()
                flash("Plato creado.", "success")
            except (ValueError, IntegrityError) as exc:
                db.session.rollback()
                flash(f"No se pudo crear el plato: {exc}", "danger")
            return redirect(url_for("menu"))
        return render_template(
            "menu.html",
            menu_items=MenuItem.query.order_by(MenuItem.name).all(),
            ingredients=Ingredient.query.order_by(Ingredient.name).all(),
        )

    @app.post("/menu/<int:item_id>/edit")
    @login_required
    def edit_menu_item(item_id):
        item = db.get_or_404(MenuItem, item_id)
        try:
            price = float(request.form["price"])
            if price <= 0:
                raise ValueError("El precio debe ser mayor a cero.")
            item.name = request.form["name"].strip()
            item.price = price
            item.description = request.form.get("description", "").strip()
            item.icon = request.form.get("icon", item.icon)
            item.active = request.form.get("active") == "on"
            db.session.commit()
            flash("Plato actualizado.", "success")
        except (ValueError, IntegrityError) as exc:
            db.session.rollback()
            flash(f"No se pudo actualizar: {exc}", "danger")
        return redirect(url_for("menu"))

    @app.route("/menu/<int:item_id>/recipe", methods=["GET", "POST"])
    @login_required
    def edit_recipe(item_id):
        item = db.get_or_404(MenuItem, item_id)
        ingredients_list = Ingredient.query.order_by(Ingredient.name).all()
        if request.method == "POST":
            try:
                RecipeIngredient.query.filter_by(menu_item_id=item.id).delete()
                recipe_count = 0
                for ingredient in ingredients_list:
                    quantity = request.form.get(
                        f"ingredient_{ingredient.id}", type=float
                    )
                    if not quantity:
                        continue
                    if quantity <= 0:
                        raise ValueError("Las cantidades deben ser positivas.")
                    db.session.add(
                        RecipeIngredient(
                            menu_item_id=item.id,
                            ingredient_id=ingredient.id,
                            quantity=quantity,
                        )
                    )
                    recipe_count += 1
                if recipe_count == 0:
                    raise ValueError("La receta debe tener al menos un ingrediente.")
                db.session.commit()
                flash("Receta actualizada.", "success")
                return redirect(url_for("menu"))
            except (ValueError, SQLAlchemyError) as exc:
                db.session.rollback()
                flash(f"No se pudo actualizar la receta: {exc}", "danger")
        quantities = {link.ingredient_id: link.quantity for link in item.recipe}
        return render_template(
            "recipe.html",
            item=item,
            ingredients=ingredients_list,
            quantities=quantities,
        )

    @app.post("/menu/<int:item_id>/delete")
    @login_required
    def delete_menu_item(item_id):
        item = db.get_or_404(MenuItem, item_id)
        try:
            db.session.delete(item)
            db.session.commit()
            flash("Plato eliminado.", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("El plato tiene ventas asociadas; desactivalo en lugar de eliminarlo.", "danger")
        return redirect(url_for("menu"))

    @app.get("/sales")
    @login_required
    def sales():
        item_id = request.args.get("menu_item_id", type=int)
        date_from_raw = request.args.get("date_from", "")
        date_to_raw = request.args.get("date_to", "")
        month_raw = request.args.get("month", "")
        query = Receipt.query.order_by(Receipt.created_at.desc())
        if date_from_raw:
            query = query.filter(Receipt.created_at >= datetime.fromisoformat(date_from_raw))
        if date_to_raw:
            query = query.filter(
                Receipt.created_at < datetime.fromisoformat(date_to_raw) + timedelta(days=1)
            )
        if month_raw:
            month_start = datetime.strptime(month_raw, "%Y-%m")
            next_month = (
                month_start.replace(year=month_start.year + 1, month=1)
                if month_start.month == 12
                else month_start.replace(month=month_start.month + 1)
            )
            query = query.filter(
                Receipt.created_at >= month_start, Receipt.created_at < next_month
            )
        receipts = query.all()
        if item_id:
            receipts = [
                receipt
                for receipt in receipts
                if any(line.menu_item_id == item_id for line in receipt.items)
            ]

        quantities = Counter()
        for receipt in receipts:
            for line in receipt.items:
                if not item_id or line.menu_item_id == item_id:
                    quantities[line.menu_item.name] += line.quantity
        revenue = sum(receipt.total_amount for receipt in receipts)
        top_items = quantities.most_common(5)
        sold_names = set(quantities)
        unsold_items = [
            item for item in MenuItem.query.filter_by(active=True).all()
            if item.name not in sold_names
        ]
        total_stats = get_total_sales_stats()
        return render_template(
            "sales.html",
            menu_items=MenuItem.query.filter_by(active=True).order_by(MenuItem.name).all(),
            receipts=receipts,
            stats={
                **total_stats,
                "top_items": top_items,
                "unsold_items": unsold_items,
            },
            filters={
                "menu_item_id": item_id,
                "date_from": date_from_raw,
                "date_to": date_to_raw,
                "month": month_raw,
            },
        )

    @app.post("/api/sales")
    @login_required
    def create_sale():
        payload = request.get_json(silent=True) or {}
        try:
            items = payload.get("items")
            if items is None:
                items = [
                    {
                        "menu_item_id": payload.get("menu_item_id"),
                        "quantity": payload.get("quantity"),
                    }
                ]
            receipt, sale_items = register_sale(
                items=items,
                payment_method=payload.get("payment_method", "cash"),
                cashier_id=session["user_id"],
            )
            db.session.commit()
            totals = get_total_sales_stats()
            return jsonify(
                {
                    "ok": True,
                    "message": "Venta registrada correctamente.",
                    "receipt_id": receipt.id,
                    "items": [
                        {
                            "name": menu_item.name,
                            "icon": menu_item.icon,
                            "quantity": quantity,
                            "subtotal": menu_item.price * quantity,
                        }
                        for menu_item, quantity in sale_items
                    ],
                    "payment_method": receipt.payment_method,
                    "total": receipt.total_amount,
                    "created_at": receipt.created_at.strftime("%d/%m/%Y %H:%M"),
                    "stats": totals,
                    "top_items": get_top_items(),
                }
            ), 201
        except (BusinessRuleError, ValueError, TypeError) as exc:
            db.session.rollback()
            return jsonify({"ok": False, "error": str(exc)}), 400
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"ok": False, "error": "No se pudo guardar la venta."}), 500

    @app.cli.command("init-db")
    def init_db_command():
        ensure_schema()
        if not User.query.filter_by(login="admin").first():
            admin = User(login="admin", full_name="Docente Demo", role="admin")
            admin.set_password(os.getenv("DEMO_PASSWORD", "SmartGastro2026!"))
            db.session.add(admin)
        if not Ingredient.query.first():
            db.session.add_all(
                [
                    Ingredient(name="Pan", unit="u", stock=100, min_stock=20),
                    Ingredient(name="Medallón", unit="u", stock=80, min_stock=15),
                ]
            )
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
        print("Base de datos inicializada.")

    @app.cli.command("seed-demo")
    @click.option("--reset", is_flag=True, help="Elimina los datos actuales antes de cargar la demo.")
    def seed_demo_command(reset):
        ensure_schema()
        if reset:
            for model in (
                ReceiptItem,
                Receipt,
                RecipeIngredient,
                StockReceipt,
                MenuItem,
                Ingredient,
                User,
            ):
                db.session.query(model).delete()
            db.session.commit()
        if Receipt.query.first() or MenuItem.query.first():
            print("La demo ya esta cargada. Usa --reset para recrearla.")
            return
        admin = User.query.filter_by(login="admin").first()
        if not admin:
            admin = User(login="admin", full_name="Administrador", role="admin")
            admin.set_password(os.getenv("DEMO_PASSWORD", "SmartGastro2026!"))
            db.session.add(admin)
            db.session.flush()

        ingredient_data = [
            ("Pan de hamburguesa", "u", 120, 20, "🥯"),
            ("Medallón de carne", "g", 18000, 3000, "🥩"),
            ("Queso cheddar", "g", 7000, 1200, "🧀"),
            ("Lechuga", "g", 4500, 700, "🥬"),
            ("Tomate", "g", 6000, 1000, "🍅"),
            ("Mayonesa", "ml", 5000, 800, "🥫"),
            ("Pan de pancho", "u", 70, 15, "🥯"),
            ("Salchicha", "u", 80, 15, "🌭"),
            ("Papa", "kg", 35, 6, "🥔"),
            ("Aceite", "l", 18, 4, "🫗"),
            ("Gaseosa", "u", 100, 20, "🥤"),
        ]
        ingredients_by_name = {}
        for name, unit, stock, minimum, icon in ingredient_data:
            ingredient = Ingredient(
                name=name, unit=unit, stock=stock, min_stock=minimum, icon=icon
            )
            db.session.add(ingredient)
            ingredients_by_name[name] = ingredient
        db.session.flush()

        menu_data = [
            ("Hamburguesa clásica", 7500, "🍔", {
                "Pan de hamburguesa": 1, "Medallón de carne": 150,
                "Lechuga": 20, "Tomate": 30, "Mayonesa": 15,
            }),
            ("Cheeseburger", 8200, "🍔", {
                "Pan de hamburguesa": 1, "Medallón de carne": 150,
                "Queso cheddar": 40, "Mayonesa": 15,
            }),
            ("Hot dog", 5200, "🌭", {
                "Pan de pancho": 1, "Salchicha": 1, "Mayonesa": 10,
            }),
            ("Papas fritas", 3900, "🍟", {"Papa": 0.3, "Aceite": 0.04}),
            ("Gaseosa", 2500, "🥤", {"Gaseosa": 1}),
        ]
        menu_by_name = {}
        for name, price, icon, recipe in menu_data:
            item = MenuItem(name=name, price=price, icon=icon, description="Producto demo")
            db.session.add(item)
            db.session.flush()
            menu_by_name[name] = item
            for ingredient_name, quantity in recipe.items():
                db.session.add(
                    RecipeIngredient(
                        menu_item_id=item.id,
                        ingredient_id=ingredients_by_name[ingredient_name].id,
                        quantity=quantity,
                    )
                )

        sale_pattern = [
            ("Hamburguesa clásica", 2), ("Cheeseburger", 1), ("Hot dog", 3),
            ("Papas fritas", 2), ("Gaseosa", 4), ("Hamburguesa clásica", 1),
            ("Cheeseburger", 2), ("Gaseosa", 2), ("Papas fritas", 1),
            ("Hamburguesa clásica", 3), ("Hot dog", 1), ("Gaseosa", 3),
        ]
        for index in reversed(range(len(sale_pattern))):
            item_name, quantity = sale_pattern[index]
            item = menu_by_name[item_name]
            receipt = Receipt(
                cashier_id=admin.id,
                payment_method=["cash", "card", "mercadopago"][index % 3],
                total_amount=item.price * quantity,
                created_at=datetime.now() - timedelta(days=index * 3),
            )
            receipt.items.append(
                ReceiptItem(menu_item_id=item.id, quantity=quantity, unit_price=item.price)
            )
            for link in item.recipe:
                link.ingredient.stock -= link.quantity * quantity
            db.session.add(receipt)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
        print("Datos de demostracion cargados.")

    @app.cli.command("renumber-tickets")
    def renumber_tickets_command():
        """Ordena los tickets desde la venta más antigua a la más reciente."""
        receipts = Receipt.query.order_by(Receipt.created_at, Receipt.id).all()
        mapping = [(receipt.id, new_id) for new_id, receipt in enumerate(receipts, 1)]
        if all(old_id == new_id for old_id, new_id in mapping):
            print("Los tickets ya estan ordenados cronologicamente.")
            return
        try:
            for old_id, _ in mapping:
                temporary_id = -old_id
                db.session.execute(
                    text(
                        "UPDATE receipt_item SET receipt_id = :temporary_id "
                        "WHERE receipt_id = :old_id"
                    ),
                    {"temporary_id": temporary_id, "old_id": old_id},
                )
                db.session.execute(
                    text(
                        "UPDATE receipt SET id = :temporary_id "
                        "WHERE id = :old_id"
                    ),
                    {"temporary_id": temporary_id, "old_id": old_id},
                )
            for old_id, new_id in mapping:
                temporary_id = -old_id
                db.session.execute(
                    text(
                        "UPDATE receipt SET id = :new_id "
                        "WHERE id = :temporary_id"
                    ),
                    {"new_id": new_id, "temporary_id": temporary_id},
                )
                db.session.execute(
                    text(
                        "UPDATE receipt_item SET receipt_id = :new_id "
                        "WHERE receipt_id = :temporary_id"
                    ),
                    {"new_id": new_id, "temporary_id": temporary_id},
                )
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
        print(f"Se renumeraron {len(mapping)} tickets cronologicamente.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
