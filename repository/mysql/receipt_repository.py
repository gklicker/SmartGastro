from db import get_db


class ReceiptRepository:

    def create(self, foodtruck_id, cashier_id, payment_method, event_id=None):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM payment_methods WHERE name = %s", (payment_method,)
                )
                pm = cur.fetchone()
                if not pm:
                    raise ValueError(f"Medio de pago inválido: '{payment_method}'")
                cur.execute(
                    "INSERT INTO receipts (foodtruck_id, cashier_id, payment_method_id, event_id) "
                    "VALUES (%s, %s, %s, %s)",
                    (foodtruck_id, cashier_id, pm["id"], event_id),
                )
                return self.find_by_id(cur.lastrowid)

    def find_by_id(self, receipt_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT r.id, r.foodtruck_id, r.cashier_id, r.event_id, pm.name AS payment_method, "
                    "r.status, r.total_amount, r.created_at, r.closed_at "
                    "FROM receipts r JOIN payment_methods pm ON r.payment_method_id = pm.id "
                    "WHERE r.id = %s",
                    (receipt_id,),
                )
                receipt = cur.fetchone()
                if receipt:
                    receipt["items"] = self._get_items(cur, receipt_id)
                return receipt

    def _get_items(self, cur, receipt_id):
        cur.execute(
            "SELECT ri.id, m.name AS plato, ri.quantity, ri.unit_price, ri.subtotal "
            "FROM receipt_items ri JOIN menu_items m ON ri.menu_item_id = m.id "
            "WHERE ri.receipt_id = %s",
            (receipt_id,),
        )
        return cur.fetchall()

    def add_item(self, receipt_id, menu_item_id, quantity, unit_price):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO receipt_items (receipt_id, menu_item_id, quantity, unit_price) "
                    "VALUES (%s, %s, %s, %s)",
                    (receipt_id, menu_item_id, quantity, unit_price),
                )
                total = self._recalculate_total(cur, receipt_id)
                cur.execute("UPDATE receipts SET total_amount = %s WHERE id = %s", (total, receipt_id))
                return self.find_by_id(receipt_id)

    def add_items_batch(self, receipt_id, items):
        with get_db() as conn:
            with conn.cursor() as cur:
                for item in items:
                    cur.execute(
                        "INSERT INTO receipt_items (receipt_id, menu_item_id, quantity, unit_price) "
                        "VALUES (%s, %s, %s, %s)",
                        (receipt_id, item["menu_item_id"], item["quantity"], item["unit_price"]),
                    )
                total = self._recalculate_total(cur, receipt_id)
                cur.execute("UPDATE receipts SET total_amount = %s WHERE id = %s", (total, receipt_id))
                return self.find_by_id(receipt_id)

    def _recalculate_total(self, cur, receipt_id):
        cur.execute(
            "SELECT COALESCE(SUM(subtotal), 0) AS total FROM receipt_items WHERE receipt_id = %s",
            (receipt_id,),
        )
        return cur.fetchone()["total"]

    def close(self, receipt_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE receipts SET status = 'closed', closed_at = NOW() WHERE id = %s AND status = 'open'",
                    (receipt_id,),
                )
                if cur.rowcount == 0:
                    raise ValueError("El ticket no está abierto o no existe.")
                return self.find_by_id(receipt_id)

    def cancel(self, receipt_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE receipts SET status = 'cancelled' WHERE id = %s AND status = 'open'",
                    (receipt_id,),
                )
                if cur.rowcount == 0:
                    raise ValueError("Solo se pueden cancelar tickets abiertos.")
                return self.find_by_id(receipt_id)

    def list_all(self, page=1, limit=20, evento_id=None, estado=None, cajero_id=None,
                 fecha_desde=None, fecha_hasta=None):
        offset = (page - 1) * limit
        where, params = [], []
        if evento_id:
            where.append("r.event_id = %s"); params.append(evento_id)
        if estado:
            where.append("r.status = %s"); params.append(estado)
        if cajero_id:
            where.append("r.cashier_id = %s"); params.append(cajero_id)
        if fecha_desde:
            where.append("r.created_at >= %s"); params.append(fecha_desde)
        if fecha_hasta:
            where.append("r.created_at <= %s"); params.append(fecha_hasta)
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS total FROM receipts r {clause}", params)
                total = cur.fetchone()["total"]
                cur.execute(
                    f"SELECT r.id, r.foodtruck_id, r.cashier_id, r.event_id, "
                    f"pm.name AS payment_method, r.status, r.total_amount, r.created_at, r.closed_at "
                    f"FROM receipts r JOIN payment_methods pm ON r.payment_method_id = pm.id {clause} "
                    f"ORDER BY r.created_at DESC LIMIT %s OFFSET %s",
                    params + [limit, offset],
                )
                return cur.fetchall(), total

    def event_revenue(self, event_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(SUM(total_amount), 0) AS revenue "
                    "FROM receipts WHERE event_id = %s AND status = 'closed'",
                    (event_id,),
                )
                return float(cur.fetchone()["revenue"])
