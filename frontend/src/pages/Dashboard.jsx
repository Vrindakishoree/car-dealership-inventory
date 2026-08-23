import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import VehicleCard from "../components/VehicleCard";
import AddVehicleForm from "../components/AddVehicleForm";

function Dashboard() {
  const { logout, isAdmin } = useAuth();
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const data = await api.getVehicles();
      setVehicles(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVehicles();
  }, []);

  const handlePurchase = async (id) => {
    try {
      await api.purchaseVehicle(id);
      loadVehicles();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this vehicle?")) return;
    try {
      await api.deleteVehicle(id);
      loadVehicles();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleRestock = async (id) => {
    const amount = prompt("How many units to add?");
    if (!amount) return;
    try {
      await api.restockVehicle(id, parseInt(amount, 10));
      loadVehicles();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Vehicle Inventory
        </h1>
        <button
          onClick={logout}
          className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900"
        >
          Log Out
        </button>
      </div>

      {isAdmin && <AddVehicleForm onVehicleAdded={loadVehicles} />}

      {loading && <p className="text-gray-600">Loading vehicles...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {!loading && !error && vehicles.length === 0 && (
        <p className="text-gray-600">No vehicles in inventory yet.</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {vehicles.map((vehicle) => (
          <VehicleCard
            key={vehicle.id}
            vehicle={vehicle}
            onPurchase={handlePurchase}
            isAdmin={isAdmin}
            onDelete={handleDelete}
            onRestock={handleRestock}
          />
        ))}
      </div>
    </div>
  );
}

export default Dashboard;