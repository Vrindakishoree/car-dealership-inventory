import { useState } from "react";
import { api } from "../services/api";

function AddVehicleForm({ onVehicleAdded }) {
  const [form, setForm] = useState({
    make: "",
    model: "",
    category: "",
    price: "",
    quantity: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await api.addVehicle({
        make: form.make,
        model: form.model,
        category: form.category,
        price: parseFloat(form.price),
        quantity: parseInt(form.quantity, 10),
      });
      setForm({ make: "", model: "", category: "", price: "", quantity: "" });
      onVehicleAdded();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-5 mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">
        Add New Vehicle
      </h2>

      {error && (
        <p className="text-red-600 text-sm mb-3">{error}</p>
      )}

      <form
        onSubmit={handleSubmit}
        className="grid grid-cols-2 sm:grid-cols-5 gap-3"
      >
        <input
          name="make"
          value={form.make}
          onChange={handleChange}
          placeholder="Make"
          required
          className="border border-gray-300 rounded px-3 py-2 col-span-1"
        />
        <input
          name="model"
          value={form.model}
          onChange={handleChange}
          placeholder="Model"
          required
          className="border border-gray-300 rounded px-3 py-2 col-span-1"
        />
        <input
          name="category"
          value={form.category}
          onChange={handleChange}
          placeholder="Category"
          required
          className="border border-gray-300 rounded px-3 py-2 col-span-1"
        />
        <input
          name="price"
          value={form.price}
          onChange={handleChange}
          placeholder="Price"
          type="number"
          min="0"
          step="0.01"
          required
          className="border border-gray-300 rounded px-3 py-2 col-span-1"
        />
        <input
          name="quantity"
          value={form.quantity}
          onChange={handleChange}
          placeholder="Quantity"
          type="number"
          min="0"
          required
          className="border border-gray-300 rounded px-3 py-2 col-span-1"
        />

        <button
          type="submit"
          disabled={submitting}
          className="col-span-2 sm:col-span-5 bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? "Adding..." : "Add Vehicle"}
        </button>
      </form>
    </div>
  );
}

export default AddVehicleForm;