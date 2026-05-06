from db import get_db


class MenuItemRepository:

    def create(self, name, price, description=""):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO menu_items (name, price, description) VALUES (%s, %s, %s)",
                    (name, price, description),
                )
                return self.find_by_id(cur.lastrowid)

    def find_by_id(self, item_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, price, description, active FROM menu_items WHERE id = %s",
                    (item_id,),
                )
                item = cur.fetchone()
                if item:
                    item["ingredients"] = self._get_ingredients(cur, item_id)
                return item

    def _get_ingredients(self, cur, item_id):
        cur.execute(
            "SELECT i.id AS ingredient_id, i.name, u.name AS unit, mii.quantity "
            "FROM menu_item_ingredients mii "
            "JOIN ingredients i ON mii.ingredient_id = i.id "
            "JOIN units u ON i.unit_id = u.id "
            "WHERE mii.menu_item_id = %s",
            (item_id,),
        )
        return cur.fetchall()

    def list_active(self, page=1, limit=20, nombre=None, precio_max=None):
        return self._list(page, limit, active_only=True, nombre=nombre, precio_max=precio_max)

    def list_all(self, page=1, limit=20, nombre=None, precio_max=None):
        return self._list(page, limit, active_only=False, nombre=nombre, precio_max=precio_max)

    def _list(self, page, limit, active_only, nombre, precio_max):
        offset = (page - 1) * limit
        where, params = [], []
        if active_only:
            where.append("active = 1")
        if nombre:
            where.append("name LIKE %s")
            params.append(f"%{nombre}%")
        if precio_max is not None:
            where.append("price <= %s")
            params.append(precio_max)
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS total FROM menu_items {clause}", params)
                total = cur.fetchone()["total"]
                cur.execute(
                    f"SELECT id, name, price, description, active FROM menu_items {clause} "
                    f"ORDER BY name LIMIT %s OFFSET %s",
                    params + [limit, offset],
                )
                items = cur.fetchall()
                for item in items:
                    item["ingredients"] = self._get_ingredients(cur, item["id"])
                return items, total

    def update(self, item_id, data):
        fields = {k: v for k, v in data.items() if k in ("name", "price", "description")}
        if fields:
            with get_db() as conn:
                with conn.cursor() as cur:
                    set_clause = ", ".join(f"{k} = %s" for k in fields)
                    cur.execute(
                        f"UPDATE menu_items SET {set_clause} WHERE id = %s",
                        list(fields.values()) + [item_id],
                    )
        return self.find_by_id(item_id)

    def add_ingredient(self, item_id, ingredient_id, quantity):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity) "
                    "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = %s",
                    (item_id, ingredient_id, quantity, quantity),
                )
                return self.find_by_id(item_id)

    def remove_ingredient(self, item_id, ingredient_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM menu_item_ingredients WHERE menu_item_id = %s AND ingredient_id = %s",
                    (item_id, ingredient_id),
                )

    def deactivate(self, item_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE menu_items SET active = 0 WHERE id = %s", (item_id,))

    def delete(self, item_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM receipt_items WHERE menu_item_id = %s", (item_id,)
                )
                if cur.fetchone()["total"] > 0:
                    raise ValueError("El plato tiene tickets asociados. Use /desactivar.")
                cur.execute("DELETE FROM menu_item_ingredients WHERE menu_item_id = %s", (item_id,))
                cur.execute("DELETE FROM menu_items WHERE id = %s", (item_id,))
