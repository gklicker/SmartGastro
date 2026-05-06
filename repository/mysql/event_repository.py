from db import get_db


class EventRepository:

    def create(self, name, address, date_start, date_end, created_by, weather_forecast="Sin datos"):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (name, address, date_start, date_end, created_by) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (name, address, date_start, date_end, created_by),
                )
                event_id = cur.lastrowid
                # weather_forecast is not in schema — stored in memory for now, returned in response
                row = self._fetch(cur, event_id)
                if row:
                    row["weather_forecast"] = weather_forecast
                return row

    def find_by_id(self, event_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                return self._fetch(cur, event_id)

    def find_by_name(self, name):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT e.id, e.name, e.address, e.date_start, e.date_end, e.status, "
                    "e.cancellation_comment, e.created_by, e.created_at "
                    "FROM events e WHERE e.name = %s",
                    (name,),
                )
                return cur.fetchone()

    def _fetch(self, cur, event_id):
        cur.execute(
            "SELECT e.id, e.name, e.address, e.date_start, e.date_end, e.status, "
            "e.cancellation_comment, e.created_by, e.created_at "
            "FROM events e WHERE e.id = %s",
            (event_id,),
        )
        return cur.fetchone()

    def list_all(self, page=1, limit=20, estado=None, fecha_desde=None, fecha_hasta=None):
        offset = (page - 1) * limit
        where, params = [], []
        if estado:
            where.append("e.status = %s")
            params.append(estado)
        if fecha_desde:
            where.append("e.date_start >= %s")
            params.append(fecha_desde)
        if fecha_hasta:
            where.append("e.date_end <= %s")
            params.append(fecha_hasta)
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS total FROM events e {clause}", params)
                total = cur.fetchone()["total"]
                cur.execute(
                    f"SELECT e.id, e.name, e.address, e.date_start, e.date_end, e.status, "
                    f"e.created_by, e.created_at FROM events e {clause} "
                    f"ORDER BY e.date_start DESC LIMIT %s OFFSET %s",
                    params + [limit, offset],
                )
                return cur.fetchall(), total

    def list_upcoming(self):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, address, date_start, date_end, status, created_by, created_at "
                    "FROM events WHERE status IN ('planned', 'ongoing') AND date_end >= NOW() "
                    "ORDER BY date_start"
                )
                return cur.fetchall()

    def update_status(self, event_id, status, cancellation_reason=None, cancellation_comment=None):
        with get_db() as conn:
            with conn.cursor() as cur:
                if cancellation_reason:
                    cur.execute(
                        "SELECT id FROM cancellation_reasons WHERE name = %s", (cancellation_reason,)
                    )
                    reason_row = cur.fetchone()
                    reason_id = reason_row["id"] if reason_row else None
                    cur.execute(
                        "UPDATE events SET status = %s, cancellation_reason_id = %s, "
                        "cancellation_comment = %s WHERE id = %s",
                        (status, reason_id, cancellation_comment, event_id),
                    )
                else:
                    cur.execute("UPDATE events SET status = %s WHERE id = %s", (status, event_id))

    def update(self, event_id, data):
        fields = {k: v for k, v in data.items() if k in ("name", "address", "date_start", "date_end")}
        if not fields:
            return self.find_by_id(event_id)
        with get_db() as conn:
            with conn.cursor() as cur:
                set_clause = ", ".join(f"{k} = %s" for k in fields)
                cur.execute(
                    f"UPDATE events SET {set_clause} WHERE id = %s",
                    list(fields.values()) + [event_id],
                )
                return self.find_by_id(event_id)

    def delete(self, event_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM receipts WHERE event_id = %s", (event_id,)
                )
                if cur.fetchone()["total"] > 0:
                    raise ValueError("El evento tiene tickets asociados. No se puede eliminar.")
                cur.execute("DELETE FROM event_foodtrucks WHERE event_id = %s", (event_id,))
                cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
