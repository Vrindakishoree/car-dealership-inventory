function VehicleCard({ vehicle, onPurchase, isAdmin, onDelete, onRestock }) {
  const outOfStock = vehicle.quantity === 0;

  return (
    <div className="bg-white rounded-lg shadow p-5 flex flex-col gap-2">
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold text-gray-800">
          {vehicle.make} {vehicle.model}
        </h3>
        <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
          {vehicle.category}
        </span>
      </div>

      <p className="text-2xl font-bold text-blue-600">
        ${vehicle.price.toLocaleString()}
      </p>

      <p className={`text-sm ${outOfStock ? "text-red-600" : "text-gray-600"}`}>
        {outOfStock ? "Out of stock" : `${vehicle.quantity} in stock`}
      </p>

      <button
        onClick={() => onPurchase(vehicle.id)}
        disabled={outOfStock}
        className="mt-2 bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {outOfStock ? "Unavailable" : "Purchase"}
      </button>

      {isAdmin && (
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => onRestock(vehicle.id)}
            className="flex-1 bg-green-600 text-white py-1.5 rounded text-sm hover:bg-green-700"
          >
            Restock
          </button>
          <button
            onClick={() => onDelete(vehicle.id)}
            className="flex-1 bg-red-600 text-white py-1.5 rounded text-sm hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
}

export default VehicleCard;