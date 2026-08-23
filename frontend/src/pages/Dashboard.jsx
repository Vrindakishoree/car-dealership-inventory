import { useAuth } from "../context/AuthContext";

function Dashboard() {
  const { logout } = useAuth();

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
      <p className="text-gray-600">
        Vehicle list will go here.
      </p>
    </div>
  );
}

export default Dashboard;