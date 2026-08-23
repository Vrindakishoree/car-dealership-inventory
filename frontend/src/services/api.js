const API_BASE_URL = "http://localhost:8000";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Something went wrong");
  }

  return response.json();
}

export const api = {
  register: (email, password) =>
    request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email, password) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getVehicles: () => request("/api/vehicles"),

  searchVehicles: (params) =>
    request(`/api/vehicles/search?${new URLSearchParams(params)}`),

  addVehicle: (vehicleData) =>
    request("/api/vehicles", {
      method: "POST",
      body: JSON.stringify(vehicleData),
    }),

  updateVehicle: (id, vehicleData) =>
    request(`/api/vehicles/${id}`, {
      method: "PUT",
      body: JSON.stringify(vehicleData),
    }),

  deleteVehicle: (id) =>
    request(`/api/vehicles/${id}`, { method: "DELETE" }),

  purchaseVehicle: (id) =>
    request(`/api/vehicles/${id}/purchase`, { method: "POST" }),

  restockVehicle: (id, amount) =>
    request(`/api/vehicles/${id}/restock?amount=${amount}`, { method: "POST" }),
};