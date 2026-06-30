import unittest
from datetime import date
from unittest.mock import patch

from app import create_app
from web_models import (
    Ingredient,
    MenuItem,
    Receipt,
    RecipeIngredient,
    StockReceipt,
    User,
    db,
)


class SmartGastroWebTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        user = User(login="admin", full_name="Admin")
        user.set_password("correct-password")
        db.session.add(user)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def login(self, password="correct-password"):
        return self.client.post(
            "/login",
            data={"login": "admin", "password": password},
        )

    def create_menu_item(self, stock=20):
        ingredient = Ingredient(
            name="Pan",
            unit="u",
            stock=stock,
            min_stock=2,
        )
        item = MenuItem(name="Hamburguesa", price=100)
        db.session.add_all([ingredient, item])
        db.session.flush()
        db.session.add(
            RecipeIngredient(
                menu_item_id=item.id,
                ingredient_id=ingredient.id,
                quantity=2,
            )
        )
        db.session.commit()
        return ingredient, item

    def test_login_and_protected_routes(self):
        self.assertEqual(self.client.get("/ingredients").status_code, 302)
        self.assertEqual(self.login("wrong-password").status_code, 200)
        self.assertEqual(self.login().status_code, 302)
        self.assertEqual(self.client.get("/ingredients").status_code, 200)

    def test_ingredient_create_edit_receive_and_delete(self):
        self.login()
        response = self.client.post(
            "/ingredients",
            data={
                "name": "Tomate",
                "unit": "kg",
                "stock": "5",
                "min_stock": "1",
            },
        )
        self.assertEqual(response.status_code, 302)
        ingredient = Ingredient.query.one()

        self.client.post(
            f"/ingredients/{ingredient.id}/edit",
            data={
                "name": "Tomate perita",
                "unit": "kg",
                "stock": "6",
                "min_stock": "2",
            },
        )
        self.client.post(
            f"/ingredients/{ingredient.id}/receive",
            data={"quantity": "4"},
        )
        self.assertEqual(ingredient.name, "Tomate perita")
        self.assertEqual(ingredient.stock, 10)
        movement = StockReceipt.query.one()
        self.assertEqual(
            (movement.stock_before, movement.quantity, movement.stock_after),
            (6, 4, 10),
        )

        self.client.post(f"/ingredients/{ingredient.id}/delete")
        self.assertEqual(Ingredient.query.count(), 0)

    def test_sale_updates_stock_and_returns_live_page_data(self):
        self.login()
        ingredient, item = self.create_menu_item()
        response = self.client.post(
            "/api/sales",
            json={
                "menu_item_id": item.id,
                "quantity": 3,
                "payment_method": "card",
            },
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["message"], "Venta registrada correctamente.")
        self.assertEqual(data["total"], 300)
        self.assertEqual(
            data["items"],
            [
                {
                    "name": "Hamburguesa",
                    "icon": "🍽️",
                    "quantity": 3,
                    "subtotal": 300,
                }
            ],
        )
        self.assertEqual(data["stats"]["count"], 1)
        self.assertEqual(data["top_items"], [["Hamburguesa", 3]])
        self.assertEqual(ingredient.stock, 14)
        self.assertEqual(Receipt.query.count(), 1)
        page = self.client.get("/sales").get_data(as_text=True)
        self.assertIn("updateSalesView(data)", page)
        self.assertNotIn("window.location.reload()", page)

    def test_sale_accepts_multiple_items_and_aggregates_stock(self):
        self.login()
        ingredient, first_item = self.create_menu_item(stock=20)
        second_item = MenuItem(name="Tostado", price=80)
        db.session.add(second_item)
        db.session.flush()
        db.session.add(
            RecipeIngredient(
                menu_item_id=second_item.id,
                ingredient_id=ingredient.id,
                quantity=1,
            )
        )
        db.session.commit()

        response = self.client.post(
            "/api/sales",
            json={
                "items": [
                    {"menu_item_id": first_item.id, "quantity": 2},
                    {"menu_item_id": second_item.id, "quantity": 3},
                ],
                "payment_method": "mercadopago",
            },
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["total"], 440)
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(Receipt.query.one().items[0].quantity, 2)
        self.assertEqual(len(Receipt.query.one().items), 2)
        self.assertEqual(ingredient.stock, 13)

    def test_sale_rolls_back_when_stock_is_insufficient(self):
        self.login()
        ingredient, item = self.create_menu_item(stock=1)
        response = self.client.post(
            "/api/sales",
            json={
                "menu_item_id": item.id,
                "quantity": 1,
                "payment_method": "cash",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Stock insuficiente", response.get_json()["error"])
        self.assertEqual(ingredient.stock, 1)
        self.assertEqual(Receipt.query.count(), 0)

    @patch("app.geocode", return_value=(-34.6, -58.4, "Buenos Aires", "Argentina"))
    @patch("app.get_forecast_for_date")
    def test_dashboard_uses_argentine_date_and_conditional_alert(self, forecast, _):
        self.login()
        forecast.return_value = {
            "date": "2026-07-01",
            "time": None,
            "rain_probability": 0,
            "rain_mm": 0,
            "temp_min": 10,
            "temp_max": 20,
            "status": "Condiciones favorables",
            "recommendation": "Todo bien.",
        }

        response = self.client.get("/?date=01%2F07%2F2026")
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('value="01/07/2026"', html)
        self.assertIn("status-panel all-clear", html)
        self.assertEqual(forecast.call_args.args[2], date(2026, 7, 1))

        db.session.add(
            Ingredient(name="Queso", unit="kg", stock=1, min_stock=2)
        )
        db.session.commit()
        html = self.client.get("/?date=01%2F07%2F2026").get_data(as_text=True)
        self.assertIn("status-panel has-alerts", html)
        self.assertIn("Stock bajo de Queso", html)


if __name__ == "__main__":
    unittest.main()
