import { useState } from "react";

function SearchBar({ onSearch, onClear }) {
  const [filters, setFilters] = useState({
    make: "",
    model: "",
    category: "",
    min_price: "",
    max_price: "",
  });

  const handleChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Only include filters that were actually filled in
    const activeFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, value]) => value !== "")
    );
    onSearch(activeFilters);
  };

  const handleClear = () => {
    setFilters({ make: "", model: "", category: "", min_price: "", max_price: "" });
    onClear();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-lg shadow p-5 mb-6 grid grid-cols-2 sm:grid-cols-6 gap-3"
    >
      <input
        name="make"
        value={filters.make}
        onChange={handleChange}
        placeholder="Make"
        className="border border-gray-300 rounded px-3 py-2 col-span-1"
      />
      <input
        name="model"
        value={filters.model}
        onChange={handleChange}
        placeholder="Model"
        className="border border-gray-300 rounded px-3 py-2 col-span-1"
      />
      <input
        name="category"
        value={filters.category}
        onChange={handleChange}
        placeholder="Category"
        className="border border-gray-300 rounded px-3 py-2 col-span-1"
      />
      <input
        name="min_price"
        value={filters.min_price}
        onChange={handleChange}
        placeholder="Min Price"
        type="number"
        className="border border-gray-300 rounded px-3 py-2 col-span-1"
      />
      <input
        name="max_price"
        value={filters.max_price}
        onChange={handleChange}
        placeholder="Max Price"
        type="number"
        className="border border-gray-300 rounded px-3 py-2 col-span-1"
      />
      <div className="flex gap-2 col-span-2 sm:col-span-1">
        <button
          type="submit"
          className="flex-1 bg-blue-600 text-white rounded px-3 py-2 text-sm hover:bg-blue-700"
        >
          Search
        </button>
        <button
          type="button"
          onClick={handleClear}
          className="flex-1 bg-gray-200 text-gray-700 rounded px-3 py-2 text-sm hover:bg-gray-300"
        >
          Clear
        </button>
      </div>
    </form>
  );
}

export default SearchBar;