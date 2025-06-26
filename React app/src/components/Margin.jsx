import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import axiosInstance from "../services/axiosInstance";

const Margin = ({ onSave }) => {  // Add onSave prop
  const [data, setData] = useState([]);
  const [margins, setMargins] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const location = useLocation();
  const quotationId = location.state?.quotationId;

  // Check if all margins are filled
  const areAllMarginsFilled = () => {
    return data.length > 0 && data.every(mc => 
      margins[mc.mc_name] && 
      margins[mc.mc_name].toString().trim() !== ""
    );
  };

  useEffect(() => {
    if (!quotationId) {
      setError("Error: Quotation ID is missing.");
      setLoading(false);
      return;
    }

    async function fetchData() {
      try {
        setLoading(true);
        const response = await axiosInstance.get(`get_mc_name/${quotationId}`);
        const mcNames = response.data.mc_names || [];
        setData(mcNames);

        const marginResponse = await axiosInstance.get(`preview_quotation/${quotationId}`);
        if (marginResponse.data.margins) {
          const existingMargins = marginResponse.data.margins.reduce((acc, item) => {
            acc[item.mc_name] = item.margin;
            return acc;
          }, {});

          const mergedMargins = mcNames.reduce((acc, mc) => {
            acc[mc.mc_name] = existingMargins[mc.mc_name] || "";
            return acc;
          }, {});

          setMargins(mergedMargins);
        }
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch data", error);
        setError("Failed to load margin data. Please try again.");
        setLoading(false);
      }
    }

    fetchData();
  }, [quotationId]);

  const handleMarginChange = (mc_name, value) => {
    if (value === "" || (!isNaN(value) && Number(value) >= 0 && Number(value) <= 100)) {
      setMargins((prevMargins) => ({
        ...prevMargins,
        [mc_name]: value,
      }));
    }
  };

  const handleSubmit = async () => {
    try {
      const emptyMargins = Object.keys(margins).filter((mc_name) => margins[mc_name] === "");
      if (emptyMargins.length > 0) {
        alert(`Please fill in all margin values for: ${emptyMargins.join(", ")}`);
        return;
      }

      const marginData = Object.keys(margins).map((mc_name) => ({
        mc_name,
        margin: margins[mc_name],
      }));

      const response = await axiosInstance.post(`add_margin/${quotationId}`, marginData);

      for (let margin of response.data.added_margins) {
        const quotationMarginData = {
          quotation_id: quotationId,
          margin_id: margin.margin_id,
        };
        await axiosInstance.post("/add_margin_to_quotation", quotationMarginData);
      }
      // alert("Margins saved successfully!");
      onSave();  // Notify parent that margins are saved
    } catch (error) {
      console.error("Error submitting margin:", error);
      alert("An error occurred while saving the margins.");
    }
  };

  if (error) {
    return <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg">{error}</div>;
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  const isButtonDisabled = !areAllMarginsFilled();

  return (
    <div className="p-4">
      {data.length === 0 ? (
        <div className="text-gray-500 italic mb-4">No margin categories found.</div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              Set margin percentages for each category. Values must be between 0-100%.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {data.map((mc, index) => (
              <div key={mc.mc_name || index} className="mb-2">
                <label htmlFor={`mc_name_${index}`} className="block text-gray-700 text-sm font-medium mb-2">
                  {mc.mc_name}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    name={`mc_name_${index}`}
                    id={`mc_name_${index}`}
                    placeholder="0"
                    autoFocus
                    onChange={(e) => handleMarginChange(mc.mc_name, e.target.value)}
                    value={margins[mc.mc_name] || ""}
                    className="appearance-none border rounded w-full py-2 pl-3 pr-8 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
                  />
                  <span className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-gray-500">%</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
      <div className="flex items-center justify-end">
        <button
          onClick={handleSubmit}
          disabled={isButtonDisabled}
          className={`font-medium py-2 px-6 rounded focus:outline-none transition duration-150 ease-in-out ${
            isButtonDisabled
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-orange-500 hover:bg-orange-700 text-white focus:ring-2 focus:ring-offset-2 focus:ring-orange-500'
          }`}
        >
          Save and Continue
        </button>
      </div>
    </div>
  );
};

export default Margin;