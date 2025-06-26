// import "../pages/HomePage.css";

const Card = ({ type, size, items, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-lg mt-2 p-5 border border-gray-100 ">
      <div className="flex justify-between items-start mb-4">
        <div>
          <span className="inline-block bg-orange-100 text-orange-800 text-xs font-medium px-2.5 py-1 rounded mr-2">
            {type}
          </span>
          <span className="inline-block bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-1 rounded">
            Size: {size}
          </span>
        </div>
      </div>

      <div className="mt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Items</h4>
        {items && items.length > 0 ? (
          <ul className="space-y-2">
            {items.map((item, index) => (
              <li
                key={index}
                className="p-2 bg-gray-50 rounded border border-gray-100 flex items-center"
              >
                <span className="inline-flex items-center justify-center bg-gray-200 text-gray-800 w-6 h-6 rounded-full mr-2 text-xs">
                  {index + 1}
                </span>
                <span className="text-gray-800">{item.article} {item.cat1} {item.cat2} {item.cat3} - ({item.quantity})</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="p-4 text-center bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <p className="text-gray-500 text-sm">No items available</p>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-100 flex justify-end space-x-2">
        <button
          onClick={onEdit}
          className="px-3 py-1.5 hover:bg-white hover:border-2 hover:border-orange-600 hover:text-orange-600 text-sm rounded text-white bg-orange-500 transition-colors"
        >
          Edit
        </button>
        <button
          onClick={onDelete}
          className="px-3 py-1.5 bg-white border border-red-600 text-red-600 text-sm rounded hover:bg-red-50 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default Card;
