from db import get_db


class FoodtruckRepository:

    def create(self, name, license_plate=None, description=""):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO foodtrucks (name, license_plate, description) VALUES (%s, %s, %s)",
                    (name, license_plate, description),
                )
                return self.find_by_id(cur.lastrowid)

    def find_by_id(self, ft_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, license_plate, description, active, created_at "
                    "FROM foodtrucks WHERE id = %s",
                    (ft_id,),
                )
                ft = cur.fetchone()
                if ft:
                    ft["staff"] = self._get_staff(cur, ft_id)
                return ft

    def _get_staff(self, cur, ft_id):
        cur.execute(
            "SELECT u.id, u.login, u.full_name, r.name AS role "
            "FROM user_foodtruck uf "
            "JOIN users u ON uf.user_id = u.id "
            "JOIN roles r ON u.role_id = r.id "
            "WHERE uf.foodtruck_id = %s",
            (ft_id,),
        )
        return cur.fetchall()

    def list_all(self, page=1, limit=20, activo=None, nombre=None):
        offset = (page - 1) * limit
        where, params = [], []
        if activo is not None:
            where.append("active = %s"); params.append(1 if activo else 0)
        if nombre:
            where.append("name LIKE %s"); params.append(f"%{nombre}%")
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS total FROM foodtrucks {clause}", params)
                total = cur.fetchone()["total"]
                cur.execute(
                    f"SELECT id, name, license_plate, description, active, created_at "
                    f"FROM foodtrucks {clause} ORDER BY name LIMIT %s OFFSET %s",
                    params + [limit, offset],
                )
                return cur.fetchall(), total

    def update(self, ft_id, data):
        fields = {k: v for k, v in data.items() if k in ("name", "license_plate", "description")}
        if not fields:
            return self.find_by_id(ft_id)
        with get_db() as conn:
            with conn.cursor() as cur:
                set_clause = ", ".join(f"{k} = %s" for k in fields)
                cur.execute(
                    f"UPDATE foodtrucks SET {set_clause} WHERE id = %s",
                    list(fields.values()) + [ft_id],
                )
                return self.find_by_id(ft_id)

    def add_staff(self, ft_id, user_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        "INSERT INTO user_foodtruck (user_id, foodtruck_id) VALUES (%s, %s)",
                        (user_id, ft_id),
                    )
                except Exception as e:
                    if "Duplicate" in str(e):
                        raise ValueError("El usuario ya está asignado a este foodtruck.")
                    raise
                return self.find_by_id(ft_id)

    def remove_staff(self, ft_id, user_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM user_foodtruck WHERE foodtruck_id = %s AND user_id = %s",
                    (ft_id, user_id),
                )

    def deactivate(self, ft_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE foodtrucks SET active = 0 WHERE id = %s", (ft_id,))

    def delete(self, ft_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM receipts WHERE foodtruck_id = %s", (ft_id,)
                )
                if cur.fetchone()["total"] > 0:
                    raise ValueError("El foodtruck tiene tickets. Use /desactivar.")
                cur.execute("DELETE FROM user_foodtruck WHERE foodtruck_id = %s", (ft_id,))
                cur.execute("DELETE FROM event_foodtrucks WHERE foodtruck_id = %s", (ft_id,))
                cur.execute("DELETE FROM foodtruck_stock WHERE foodtruck_id = %s", (ft_id,))
                cur.execute("DELETE FROM foodtrucks WHERE id = %s", (ft_id,))

    # ── Inventory ────────────────────────────────────────────
    def get_stock(self, ft_id, alerta_only=False):
        with get_db() as conn:
            with conn.cursor() as cur:
                clause = "AND fs.quantity < i.min_stock_alert" if alerta_only else ""
                cur.execute(
                    f"SELECT i.id AS ingredient_id, i.name, u.name AS unit, "
                    f"fs.quantity, i.min_stock_alert "
                    f"FROM foodtruck_stock fs "
                    f"JOIN ingredients i ON fs.ingredient_id = i.id "
                    f"JOIN units u ON i.unit_id = u.id "
                    f"WHERE fs.foodtruck_id = %s {clause} "
                    f"ORDER BY i.name",
                    (ft_id,),
                )
                return cur.fetchall()

    def add_stock(self, ft_id, ingredient_id, quantity):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO foodtruck_stock (foodtruck_id, ingredient_id, quantity) "
                    "VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                    (ft_id, ingredient_id, quantity, quantity),
                )
                cur.execute(
                    "SELECT i.id AS ingredient_id, i.name, u.name AS unit, fs.quantity, i.min_stock_alert "
                    "FROM foodtruck_stock fs "
                    "JOIN ingredients i ON fs.ingredient_id = i.id "
                    "JOIN units u ON i.unit_id = u.id "
                    "WHERE fs.foodtruck_id = %s AND fs.ingredient_id = %s",
                    (ft_id, ingredient_id),
                )
                return cur.fetchone()

    def deduct_stock(self, ft_id, ingredient_id, quantity):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT quantity FROM foodtruck_stock "
                    "WHERE foodtruck_id = %s AND ingredient_id = %s",
                    (ft_id, ingredient_id),
                )
                row = cur.fetchone()
                available = float(row["quantity"]) if row else 0
                if available < quantity:
                    raise ValueError(
                        f"Stock insuficiente. Disponible: {available}, necesario: {quantity}."
                    )
                cur.execute(
                    "UPDATE foodtruck_stock SET quantity = quantity - %s "
                    "WHERE foodtruck_id = %s AND ingredient_id = %s",
                    (quantity, ft_id, ingredient_id),
                )
