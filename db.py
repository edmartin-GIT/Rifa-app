import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("RIFA_DB_PATH", Path(__file__).parent / "rifa.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tickera_numero INTEGER NOT NULL UNIQUE,
            ticket_inicio INTEGER NOT NULL,
            ticket_fin INTEGER NOT NULL,
            nombre_servidor TEXT NOT NULL,
            telefono_servidor TEXT NOT NULL DEFAULT '',
            fecha_transaccion TEXT NOT NULL,
            modalidad_pago TEXT NOT NULL CHECK(modalidad_pago IN ('CASH', 'SQUARE', 'ZELLE', 'POR PAGAR')),
            numero_confirmacion TEXT,
            precio_tickera REAL NOT NULL,
            monto_pagado REAL NOT NULL DEFAULT 0
        );
        """
    )

    columnas = {r["name"] for r in conn.execute("PRAGMA table_info(transacciones)")}
    if "telefono_servidor" not in columnas:
        conn.execute("ALTER TABLE transacciones ADD COLUMN telefono_servidor TEXT NOT NULL DEFAULT ''")

    esquema_actual = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'transacciones'"
    ).fetchone()
    if esquema_actual and "POR PAGAR" not in esquema_actual["sql"]:
        conn.executescript(
            """
            CREATE TABLE transacciones_nueva (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tickera_numero INTEGER NOT NULL UNIQUE,
                ticket_inicio INTEGER NOT NULL,
                ticket_fin INTEGER NOT NULL,
                nombre_servidor TEXT NOT NULL,
                telefono_servidor TEXT NOT NULL DEFAULT '',
                fecha_transaccion TEXT NOT NULL,
                modalidad_pago TEXT NOT NULL CHECK(modalidad_pago IN ('CASH', 'SQUARE', 'ZELLE', 'POR PAGAR')),
                numero_confirmacion TEXT,
                precio_tickera REAL NOT NULL,
                monto_pagado REAL NOT NULL DEFAULT 0
            );
            INSERT INTO transacciones_nueva
                (id, tickera_numero, ticket_inicio, ticket_fin, nombre_servidor, telefono_servidor,
                 fecha_transaccion, modalidad_pago, numero_confirmacion, precio_tickera, monto_pagado)
            SELECT id, tickera_numero, ticket_inicio, ticket_fin, nombre_servidor, telefono_servidor,
                   fecha_transaccion, modalidad_pago, numero_confirmacion, precio_tickera, monto_pagado
            FROM transacciones;
            DROP TABLE transacciones;
            ALTER TABLE transacciones_nueva RENAME TO transacciones;
            """
        )

    cur = conn.execute("SELECT valor FROM configuracion WHERE clave = 'precio_tickera'")
    if cur.fetchone() is None:
        conn.execute(
            "INSERT INTO configuracion (clave, valor) VALUES ('precio_tickera', ?)",
            ("100",),
        )
    conn.commit()
    conn.close()


def get_precio_tickera():
    conn = get_conn()
    row = conn.execute(
        "SELECT valor FROM configuracion WHERE clave = 'precio_tickera'"
    ).fetchone()
    conn.close()
    return float(row["valor"]) if row else 100.0


def set_precio_tickera(valor):
    conn = get_conn()
    conn.execute(
        "UPDATE configuracion SET valor = ? WHERE clave = 'precio_tickera'",
        (str(valor),),
    )
    conn.commit()
    conn.close()
