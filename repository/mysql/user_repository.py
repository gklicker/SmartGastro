import hashlib
from db import get_db


class UserRepository:

    def create(self, login, password, full_name, role_name):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
                role = cur.fetchone()
                if not role:
                    raise ValueError(f"Rol inválido: '{role_name}'")
                try:
                    cur.execute(
                        "INSERT INTO users (login, password_hash, full_name, role_id) VALUES (%s, %s, %s, %s)",
                        (login, pw_hash, full_name, role["id"]),
                    )
                    return self.find_by_id(cur.lastrowid)
                except Exception as e:
                    if "Duplicate" in str(e):
                        raise ValueError(f"Ya existe un usuario con login '{login}'")
                    raise

    def find_by_id(self, user_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT u.id, u.login, u.password_hash, u.full_name, r.name AS role, u.active, u.created_at "
                    "FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = %s",
                    (user_id,),
                )
                return cur.fetchone()

    def find_by_login(self, login):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT u.id, u.login, u.password_hash, u.full_name, r.name AS role, u.active, u.created_at "
                    "FROM users u JOIN roles r ON u.role_id = r.id WHERE u.login = %s",
                    (login,),
                )
                return cur.fetchone()

    def list_all(self, page=1, limit=20, role=None, active=None, nombre=None):
        offset = (page - 1) * limit
        where, params = [], []
        if role:
            where.append("r.name = %s")
            params.append(role)
        if active is not None:
            where.append("u.active = %s")
            params.append(1 if active else 0)
        if nombre:
            where.append("u.full_name LIKE %s")
            params.append(f"%{nombre}%")
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) AS total FROM users u JOIN roles r ON u.role_id = r.id {clause}",
                    params,
                )
                total = cur.fetchone()["total"]
                cur.execute(
                    f"SELECT u.id, u.login, u.full_name, r.name AS role, u.active, u.created_at "
                    f"FROM users u JOIN roles r ON u.role_id = r.id {clause} "
                    f"ORDER BY u.id LIMIT %s OFFSET %s",
                    params + [limit, offset],
                )
                return cur.fetchall(), total

    def update(self, user_id, data):
        fields = {k: v for k, v in data.items() if k in ("full_name", "role")}
        if not fields:
            return self.find_by_id(user_id)
        with get_db() as conn:
            with conn.cursor() as cur:
                if "role" in fields:
                    cur.execute("SELECT id FROM roles WHERE name = %s", (fields.pop("role"),))
                    role = cur.fetchone()
                    if not role:
                        raise ValueError("Rol inválido")
                    fields["role_id"] = role["id"]
                set_clause = ", ".join(f"{k} = %s" for k in fields)
                cur.execute(
                    f"UPDATE users SET {set_clause} WHERE id = %s",
                    list(fields.values()) + [user_id],
                )
                return self.find_by_id(user_id)

    def deactivate(self, user_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET active = 0 WHERE id = %s", (user_id,))

    def delete(self, user_id):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM receipts WHERE cashier_id = %s", (user_id,)
                )
                if cur.fetchone()["total"] > 0:
                    raise ValueError(
                        f"No se puede eliminar: el usuario tiene tickets asociados. Use /desactivar."
                    )
                cur.execute("DELETE FROM user_foodtruck WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

    def check_password(self, user_dict, password):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        return user_dict["password_hash"] == pw_hash
