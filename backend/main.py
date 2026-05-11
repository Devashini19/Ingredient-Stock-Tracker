from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()

# ========================
# APP INIT
# ========================
app = FastAPI(title="Ingredient Stock Tracker")

# ========================
# CORS
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# DB CONNECTION
# ========================

#---------- Old Connection----------
# conn = psycopg2.connect(
#     "postgresql://postgres.niivwsjnaxlifollxdhu:devashini19062005@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
# )

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)

# ========================
# CREATE TABLES
# ========================
cur = conn.cursor()

# items table
cur.execute("""
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name TEXT,
    unit TEXT,
    category TEXT,
    quantity INTEGER,
    threshold INTEGER
)
""")

# stock logs table
cur.execute("""
CREATE TABLE IF NOT EXISTS stock_logs (
    id BIGSERIAL PRIMARY KEY,

    item_id INT,
    item_name TEXT,

    action_type TEXT,

    old_quantity INT,
    new_quantity INT,

    changed_quantity INT,

    category TEXT,
    unit TEXT,

    message TEXT,

    created_at TIMESTAMP DEFAULT NOW()
)
""")

conn.commit()
cur.close()

# ========================
# MODELS
# ========================
class Item(BaseModel):
    name: str
    unit: str
    category: str
    quantity: int
    threshold: int

class StockUpdate(BaseModel):
    quantity: int

class UpdateItem(BaseModel):
    name: str | None = None
    unit: str | None = None
    category: str | None = None

# ========================
# LOW STOCK
# ========================
def is_low_stock(quantity, threshold):
    return quantity <= 10

# ========================
# DASHBOARD
# ========================
@app.get("/dashboard")
def dashboard():

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), COALESCE(SUM(quantity),0) FROM items")
    total_items, total_quantity = cur.fetchone()

    cur.execute("SELECT quantity, threshold FROM items")
    rows = cur.fetchall()

    low_stock_count = sum(
        1 for qty, th in rows if qty <= th
    )

    cur.close()

    return {
        "total_items": total_items,
        "total_quantity": total_quantity,
        "low_stock_count": low_stock_count
    }

# ========================
# HOME
# ========================
@app.get("/", response_class=HTMLResponse)
def home():
    return "<h2>Supabase Connected 🚀</h2>"

# ========================
# GET ITEMS
# ========================
@app.get("/items")
def get_items():

    cur = conn.cursor()

    cur.execute("SELECT * FROM items ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()

    return {
        "items": [
            {
                "id": r[0],
                "name": r[1],
                "unit": r[2],
                "category": r[3],
                "quantity": r[4],
                "threshold": r[5],
                "low_stock": is_low_stock(r[4], r[5])
            }
            for r in rows
        ]
    }

# ========================
# GET STOCK LOGS
# ========================
@app.get("/stock-logs")
def get_stock_logs():

    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM stock_logs
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    cur.close()

    return {
        "logs": [
            {
                "id": r[0],
                "item_id": r[1],
                "item_name": r[2],
                "action_type": r[3],
                "old_quantity": r[4],
                "new_quantity": r[5],
                "changed_quantity": r[6],
                "category": r[7],
                "unit": r[8],
                "message": r[9],
                "created_at": r[10]
            }
            for r in rows
        ]
    }

# ========================
# ADD ITEM
# ========================
@app.post("/add-item")
def add_item(item: Item):

    cur = conn.cursor()

    # insert item
    cur.execute("""
        INSERT INTO items
        (name, unit, category, quantity, threshold)

        VALUES (%s, %s, %s, %s, %s)

        RETURNING id
    """,
    (
        item.name,
        item.unit,
        item.category,
        item.quantity,
        item.threshold
    ))

    item_id = cur.fetchone()[0]

    # insert log
    cur.execute("""
        INSERT INTO stock_logs (
            item_id,
            item_name,
            action_type,
            old_quantity,
            new_quantity,
            changed_quantity,
            category,
            unit,
            message
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        item_id,
        item.name,
        "ADD_ITEM",
        0,
        item.quantity,
        item.quantity,
        item.category,
        item.unit,
        "New item added"
    ))

    conn.commit()
    cur.close()

    return {"message": "Item added"}

# ========================
# UPDATE ITEM
# ========================
@app.put("/update-item/{item_id}")
def update_item(item_id: int, data: UpdateItem):

    cur = conn.cursor()

    cur.execute("SELECT * FROM items WHERE id=%s", (item_id,))
    row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Item not found")

    new_name = data.name if data.name else row[1]
    new_unit = data.unit if data.unit else row[2]
    new_category = data.category if data.category else row[3]

    cur.execute("""
        UPDATE items
        SET name=%s, unit=%s, category=%s
        WHERE id=%s
    """, (new_name, new_unit, new_category, item_id))

    # log update
    cur.execute("""
        INSERT INTO stock_logs (
            item_id,
            item_name,
            action_type,
            old_quantity,
            new_quantity,
            changed_quantity,
            category,
            unit,
            message
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        item_id,
        new_name,
        "UPDATE_ITEM",
        row[4],
        row[4],
        0,
        new_category,
        new_unit,
        "Item details updated"
    ))

    conn.commit()
    cur.close()

    return {"message": "Updated"}

# ========================
# STOCK IN
# ========================
@app.post("/stock-in/{item_id}")
def stock_in(item_id: int, data: StockUpdate):

    cur = conn.cursor()

    cur.execute("""
        SELECT name, category, unit, quantity
        FROM items
        WHERE id=%s
    """, (item_id,))

    row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Item not found")

    old_qty = row[3]
    new_qty = old_qty + data.quantity

    cur.execute("""
        UPDATE items
        SET quantity=%s
        WHERE id=%s
    """, (new_qty, item_id))

    # log
    cur.execute("""
        INSERT INTO stock_logs (
            item_id,
            item_name,
            action_type,
            old_quantity,
            new_quantity,
            changed_quantity,
            category,
            unit,
            message
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        item_id,
        row[0],
        "STOCK_IN",
        old_qty,
        new_qty,
        data.quantity,
        row[1],
        row[2],
        "Stock increased"
    ))

    conn.commit()
    cur.close()

    return {"message": "Stock increased"}

# ========================
# STOCK OUT
# ========================
@app.post("/stock-out/{item_id}")
def stock_out(item_id: int, data: StockUpdate):

    cur = conn.cursor()

    cur.execute("""
        SELECT name, category, unit, quantity, threshold
        FROM items
        WHERE id=%s
    """, (item_id,))

    row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Item not found")

    old_qty = row[3]

    if data.quantity > old_qty:
        raise HTTPException(400, "Not enough stock")

    new_qty = old_qty - data.quantity

    cur.execute("""
        UPDATE items
        SET quantity=%s
        WHERE id=%s
    """, (new_qty, item_id))

    # stock out log
    cur.execute("""
        INSERT INTO stock_logs (
            item_id,
            item_name,
            action_type,
            old_quantity,
            new_quantity,
            changed_quantity,
            category,
            unit,
            message
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        item_id,
        row[0],
        "STOCK_OUT",
        old_qty,
        new_qty,
        data.quantity,
        row[1],
        row[2],
        "Stock reduced"
    ))

    # low stock log
    if new_qty <= row[4]:

        cur.execute("""
            INSERT INTO stock_logs (
                item_id,
                item_name,
                action_type,
                old_quantity,
                new_quantity,
                changed_quantity,
                category,
                unit,
                message
            )

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            item_id,
            row[0],
            "LOW_STOCK",
            old_qty,
            new_qty,
            0,
            row[1],
            row[2],
            "Low stock alert"
        ))

    conn.commit()
    cur.close()

    return {"message": "Stock reduced"}

# ========================
# DELETE ITEM
# ========================
@app.delete("/delete-item/{item_id}")
def delete_item(item_id: int):

    cur = conn.cursor()

    cur.execute("""
        SELECT name, category, unit, quantity
        FROM items
        WHERE id=%s
    """, (item_id,))

    row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Item not found")

    # log delete
    cur.execute("""
        INSERT INTO stock_logs (
            item_id,
            item_name,
            action_type,
            old_quantity,
            new_quantity,
            changed_quantity,
            category,
            unit,
            message
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        item_id,
        row[0],
        "DELETE_ITEM",
        row[3],
        0,
        row[3],
        row[1],
        row[2],
        "Item deleted"
    ))

    cur.execute("DELETE FROM items WHERE id=%s", (item_id,))

    conn.commit()
    cur.close()

    return {"message": "Item deleted"}

# ========================
# CLEAR ALL
# ========================
@app.delete("/clear-all")
def clear_all():

    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE items RESTART IDENTITY")

    conn.commit()
    cur.close()

    return {"message": "All data cleared + ID reset to 1"}