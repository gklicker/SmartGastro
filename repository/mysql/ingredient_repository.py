from db import get_db


def _get_or_create_unit(cur, unit_name):
    cur.execute("SELECT id FROM units WHERE name = %s", (unit_name,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute("INSERT INTO units (name) VALUES (%s)", (unit_name,))
    return cur.lastrowid


class IngredientRepository:

    def create(self, name, unit, min_stock_alert=0):
        with get_db() as conn:
            with conn.cursor() as cur:
                unit_id = _get_or_create_unit(cur, unit)
                cur.execute(
                    "INSERT INTO ingredients (name, unit_id, min_stock_alert) VALUES (%s, %s, %s)",
                    (name, unit_id, min_stock_alert),
                )
                return self.find_by_id(cur.lastrowid)

    def find_by_id(self, ingredient_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT i.id, i.name, u.name AS unit, i.min_stock_alert "
                    "FROM ingredients i JOIN units u ON i.unit_id = u.id WHERE i.id = %s",
                    (ingredient_id,),
                )
                return cur.fetchone()

    def find_by_name(self, name):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT i.id, i.name, u.name AS unit, i.min_stock_alert "
                    "FROM ingredients i JOIN units u ON i.unit_id = u.id WHERE i.name = %s",
                    (name,),
                )
                return cur.fetchone()

    def list_all(self, page=1, limit=20, nombre=None, unit=None):
        offset = (page - 1) * limit
        where, params = [], []
        if nombre:
            where.append("i.name LIKE %s")
            params.append(f"%{nombre}%")
        if unit:
            where.append("u.name = %s")
            params.append(unit)
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) AS total FROM ingredients i JOIN units u ON i.unit_id = u.id {clause}",
                    params,
                )
                total = cur.fetchone()["total"]
                cur.execute(
                    f"SELECT i.id, i.name, u.name AS unit, i.min_stock_alert "
                    f"FROM ingredients i JOIN units u ON i.unit_id = u.id {clause} "
                    f"ORDER BY i.name LIMIT %s OFFSET %s",
                    params + [limit, offset],
                )
                return cur.fetchall(), total

    def update(self, ingredient_id, data):
        with get_db() as conn:
            with conn.cursor() as cur:
                if "unit" in data:
                    data["unit_id"] = _get_or_create_unit(cur, data.pop("unit"))
                fields = {k: v for k, v in data.items() if k in ("name", "unit_id", "min_stock_alert")}
                if not fields:
                    return self.find_by_id(ingredient_id)
                set_clause = ", ".join(f"{k} = %s" for k in fields)
                cur.execute(
                    f"UPDATE ingredients SET {set_clause} WHERE id = %s",
                    list(fields.values()) + [ingredient_id],
                )
                return self.find_by_id(ingredient_id)

    def delete(self, ingredient_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM menu_item_ingredients WHERE ingredient_id = %s",
                    (ingredient_id,),
                )
                if cur.fetchone()["total"] > 0:
                    raise ValueError("El ingrediente está en uso en recetas. No se puede eliminar.")
                cur.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
