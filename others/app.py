import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Stock Tracker")

st.title("🍽 Ingredient Stock Dashboard")

# =======================
# MENU (PROPER ORDER)
# =======================
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard Analytics",
        "View Items",
        "Search Item",
        "Filter By Category",
        "Low Stock",
        "Stock In",
        "Stock Out",
        "Add Item",
        "Update Item",
        "Delete Item"
    ]
)

# =======================
# DASHBOARD
# =======================
if menu == "Dashboard Analytics":

    st.subheader("📊 Dashboard")

    r = requests.get(f"{API}/dashboard")
    data = r.json()

    st.metric("Total Items", data["total_items"])
    st.metric("Total Quantity", data["total_quantity"])
    st.metric("Low Stock Count", data["low_stock_count"])

# =======================
# VIEW ITEMS
# =======================
elif menu == "View Items":

    res = requests.get(f"{API}/items")
    data = res.json()

    st.subheader("📦 All Items")

    for item in data["items"]:
        st.write(item)

# =======================
# SEARCH ITEM
# =======================
elif menu == "Search Item":

    st.subheader("🔍 Search Item")

    search_name = st.text_input("Enter Item Name")

    if st.button("Search"):

        r = requests.get(f"{API}/search?name={search_name}")
        data = r.json()

        for item in data["items"]:
            st.write(item)

# =======================
# FILTER BY CATEGORY
# =======================
elif menu == "Filter By Category":

    st.subheader("📂 Filter By Category")

    category = st.selectbox(
        "Select Category",
        [
            "General",
            "Grains",
            "Dairy",
            "Meat",
            "Oil",
            "Spices",
            "Vegetables",
            "Fruits"
        ]
    )

    if st.button("Filter"):

        r = requests.get(
            f"{API}/filter-by-category?category={category}"
        )

        data = r.json()

        for item in data["items"]:
            st.write(item)

# =======================
# LOW STOCK
# =======================
elif menu == "Low Stock":

    st.subheader("⚠️ Low Stock Items")

    r = requests.get(f"{API}/low-stock")
    data = r.json()

    for item in data["low_stock_items"]:
        st.write(item)

# =======================
# STOCK IN
# =======================
elif menu == "Stock In":

    st.subheader("📈 Increase Stock")

    item_id = st.number_input("Item ID", min_value=1)
    qty = st.number_input("Quantity", min_value=1)

    if st.button("Stock In"):

        r = requests.post(
            f"{API}/stock-in/{item_id}",
            json={"quantity": int(qty)}
        )

        st.success(r.json())

# =======================
# STOCK OUT
# =======================
elif menu == "Stock Out":

    st.subheader("📉 Reduce Stock")

    item_id = st.number_input("Item ID", min_value=1)
    qty = st.number_input("Quantity", min_value=1)

    if st.button("Stock Out"):

        r = requests.post(
            f"{API}/stock-out/{item_id}",
            json={"quantity": int(qty)}
        )

        st.success(r.json())

# =======================
# ADD ITEM
# =======================
elif menu == "Add Item":

    st.subheader("➕ Add New Item")

    name = st.text_input("Name")

    unit = st.selectbox(
        "Unit",
        ["kg", "g", "ml", "litre"]
    )

    category = st.selectbox(
        "Category",
        ["General", "Grains", "Dairy", "Meat", "Oil", "Spices", "Vegetables", "Fruits"]
    )

    quantity = st.number_input("Quantity", min_value=0)
    threshold = st.number_input("Threshold", min_value=0)

    if st.button("Add"):

        r = requests.post(
            f"{API}/add-item",
            json={
                "name": name,
                "unit": unit,
                "category": category,
                "quantity": int(quantity),
                "threshold": int(threshold)
            }
        )

        st.success(r.json())

# =======================
# UPDATE ITEM
# =======================
elif menu == "Update Item":

    st.subheader("✏️ Update Item")

    item_id = st.number_input("Item ID", min_value=1)

    new_name = st.text_input("New Name (optional)")

    new_unit = st.selectbox(
        "New Unit (optional)",
        ["", "kg", "g", "ml", "litre"]
    )

    new_category = st.selectbox(
        "New Category (optional)",
        ["", "General", "Grains", "Dairy", "Meat", "Oil", "Spices", "Vegetables", "Fruits"]
    )

    if st.button("Update"):

        payload = {}

        if new_name:
            payload["name"] = new_name
        if new_unit:
            payload["unit"] = new_unit
        if new_category:
            payload["category"] = new_category

        r = requests.put(
            f"{API}/update-item/{item_id}",
            json=payload
        )

        st.success(r.json())

# =======================
# DELETE ITEM
# =======================
elif menu == "Delete Item":

    st.subheader("🗑️ Delete Item")

    item_id = st.number_input("Item ID", min_value=1)

    if st.button("Delete"):

        r = requests.delete(f"{API}/delete-item/{item_id}")

        st.success(r.json())