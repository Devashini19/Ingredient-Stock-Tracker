import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

axios.defaults.baseURL = "http://127.0.0.1:8000";

const API = "http://127.0.0.1:8000";

//axios.delete(`http://127.0.0.1:8000/delete-item/${id}`)

function App() {

  // =========================
  // STATES
  // =========================
  const [items, setItems] = useState([]);
  const [dashboard, setDashboard] = useState({});
  const [search, setSearch] = useState("");

  const [form, setForm] = useState({
    name: "",
    unit: "kg",
    category: "General",
    quantity: "",
    threshold: ""
  });

  // =========================
  // LOAD DATA
  // =========================
  useEffect(() => {
    loadItems();
    loadDashboard();
  }, []);

  const loadItems = async () => {
    const res = await axios.get(`${API}/items`);
    setItems(res.data.items);
  };

  const loadDashboard = async () => {
    const res = await axios.get(`${API}/dashboard`);
    setDashboard(res.data);
  };

  // =========================
  // ADD ITEM
  // =========================
  const addItem = async () => {

    if (
      !form.name ||
      !form.quantity ||
      !form.threshold
    ) {
      alert("Please fill all fields");
      return;
    }

    await axios.post(`${API}/add-item`, {
      name: form.name,
      unit: form.unit,
      category: form.category,
      quantity: parseInt(form.quantity),
      threshold: parseInt(form.threshold)
    });

    alert("Item Added Successfully ✅");

    setForm({
      name: "",
      unit: "kg",
      category: "General",
      quantity: "",
      threshold: ""
    });

    loadItems();
    loadDashboard();
  };

  // =========================
  // DELETE ITEM
  // =========================
  const deleteItem = async (id) => {

    const confirmDelete = window.confirm(
      "Are you sure want to delete this item?"
    );

    if (!confirmDelete) {
      return;
    }

    await axios.delete(`${API}/delete-item/${id}`);

    alert("Item Deleted Successfully ❌");

    loadItems();
    loadDashboard();
  };

  // =========================
  // STOCK IN
  // =========================
  const stockIn = async (id) => {

    const qty = prompt("Enter Quantity");

    if (!qty) return;

    await axios.post(`${API}/stock-in/${id}`, {
      quantity: parseInt(qty)
    });

    alert("Stock Increased ✅");

    loadItems();
    loadDashboard();
  };

  // =========================
  // STOCK OUT
  // =========================
  const stockOut = async (id) => {

    const qty = prompt("Enter Quantity");

    if (!qty) return;

    await axios.post(`${API}/stock-out/${id}`, {
      quantity: parseInt(qty)
    });

    alert("Stock Reduced ⚠");

    loadItems();
    loadDashboard();
  };

  // =========================
  // UPDATE ITEM
  // =========================
  const updateItem = async (item) => {

    const newName = prompt(
      "Enter New Item Name",
      item.name
    );

    const newUnit = prompt(
      "Enter New Unit",
      item.unit
    );

    const newCategory = prompt(
      "Enter New Category",
      item.category
    );

    if (!newName || !newUnit || !newCategory) {
      return;
    }

    await axios.put(
      `${API}/update-item/${item.id}`,
      {
        name: newName,
        unit: newUnit,
        category: newCategory
      }
    );

    alert("Item Updated Successfully ✅");

    loadItems();
  };

  // =========================
  // SEARCH
  // =========================
  const searchItem = async () => {

    if (search === "") {
      loadItems();
      return;
    }

    const res = await axios.get(
      `${API}/search?name=${search}`
    );

    setItems(res.data.items);
  };

  // =========================
  // FILTER CATEGORY
  // =========================
  const filterCategory = async (category) => {

    if (category === "All") {
      loadItems();
      return;
    }

    const res = await axios.get(
      `${API}/filter-by-category?category=${category}`
    );

    setItems(res.data.items);
  };

  return (

    <div className="container">

      {/* ========================= */}
      {/* HEADER */}
      {/* ========================= */}
      <div className="header">

        <h1>🍽 Ingredient Stock Tracker</h1>

        <p>
          Restaurant Inventory Management System
        </p>

      </div>

      {/* ========================= */}
      {/* DASHBOARD */}
      {/* ========================= */}
      <div className="dashboard">

        <div className="card">
          <h2>{dashboard.total_items}</h2>
          <p>Total Items</p>
        </div>

        <div className="card">
          <h2>{dashboard.total_quantity}</h2>
          <p>Total Quantity</p>
        </div>

        <div className="card danger">
          <h2>{dashboard.low_stock_count}</h2>
          <p>Low Stock</p>
        </div>

      </div>

      {/* ========================= */}
      {/* FORM */}
      {/* ========================= */}
      <div className="form-section">

        <h2>Add Ingredient</h2>

        <div className="form-grid">

          <input
            type="text"
            placeholder="Ingredient Name"
            value={form.name}
            onChange={(e) =>
              setForm({
                ...form,
                name: e.target.value
              })
            }
          />

          <select
            value={form.unit}
            onChange={(e) =>
              setForm({
                ...form,
                unit: e.target.value
              })
            }
          >
            <option>kg</option>
            <option>Gram</option>
            <option>Litre</option>
            <option>Packet</option>
            <option>Piece</option>
          </select>

          <select
            value={form.category}
            onChange={(e) =>
              setForm({
                ...form,
                category: e.target.value
              })
            }
          >
            <option>General</option>
            <option>Grains</option>
            <option>Dairy</option>
            <option>Vegetables</option>
            <option>Fruits</option>
            <option>Spices</option>
            <option>Meat</option>
            <option>Seafood</option>
            <option>Oil</option>
            <option>Beverages</option>
            <option>Frozen foods</option>
            <option>Bakery products</option>
             <option>Cleaning products</option>
          </select>

          <input
            type="number"
            placeholder="Quantity"
            value={form.quantity}
            onChange={(e) =>
              setForm({
                ...form,
                quantity: e.target.value
              })
            }
          />

          <input
            type="number"
            placeholder="Threshold"
            value={form.threshold}
            onChange={(e) =>
              setForm({
                ...form,
                threshold: e.target.value
              })
            }
          />

        </div>

        <button
          className="add-btn"
          onClick={addItem}
        >
          Add Item
        </button>

      </div>

      {/* ========================= */}
      {/* SEARCH + FILTER */}
      {/* ========================= */}
      <div className="search-box">

        <input
          type="text"
          placeholder="Search Ingredient..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <button onClick={searchItem}>
          Search
        </button>

        <select
          onChange={(e) =>
            filterCategory(e.target.value)
          }
        >
          <option>All</option>
          <option>Grains</option>
          <option>Dairy</option>
          <option>Vegetables</option>
          <option>Fruits</option>
          <option>Spices</option>
          <option>Meat</option>
          <option>Seafood</option>
          <option>Oil</option>
          <option>Beverages</option>
          <option>Frozen foods</option>
          <option>Bakery products</option>
          <option>Cleaning products</option>
        </select>

      </div>

      {/* ========================= */}
      {/* TABLE */}
      {/* ========================= */}
      <div className="table-section">

        <table>

          <thead>

            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Category</th>
              <th>Unit</th>
              <th>Quantity</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>

          </thead>

          <tbody>

            {items.map((item) => (

              <tr
                key={item.id}
                className={
                  item.low_stock ? "row-low" : ""
                }
              >

                <td>{item.id}</td>

                <td>{item.name}</td>

                <td>{item.category}</td>

                <td>{item.unit}</td>

                <td>{item.quantity}</td>

                <td>

                  {item.low_stock ? (
                    <span className="low">
                      Low Stock
                    </span>
                  ) : (
                    <span className="good">
                      In Stock
                    </span>
                  )}

                </td>

                <td>

                  <button
                    className="stockin"
                    onClick={() =>
                      stockIn(item.id)
                    }
                  >
                    +
                  </button>

                  <button
                    className="stockout"
                    onClick={() =>
                      stockOut(item.id)
                    }
                  >
                    -
                  </button>

                  <button
                    className="update"
                    onClick={() =>
                      updateItem(item)
                    }
                  >
                    Update
                  </button>

                  <button
                    className="delete"
                    onClick={() =>
                      deleteItem(item.id)
                    }
                  >
                    Delete
                  </button>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

      {/* ========================= */}
      {/* FOOTER */}
      {/* ========================= */}
      <div className="footer">

        <p>
          {/* Developed using React + FastAPI + SQLite */}
        </p>

      </div>

    </div>
  );
}

export default App;


// -------------------------------------------------------------------------------