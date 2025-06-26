import {
  useState,
  // useEffect
} from "react";
import { useNavigate } from "react-router-dom";
// import { finalQuotationIds, wipQuotationIds } from "../services/api";

const Home = () => {
  const navigate = useNavigate();
  // const [searchTerm, setSearchTerm] = useState("");
  // const [quotations, setQuotations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // useEffect(() => {
  //   async function fetchQuotations() {
  //     setIsLoading(true);
  //     setError(null);
  //     try {
  //       // Fetch WIP quotations
  //       const wipResponse = await wipQuotationIds();
  //       console.log("WIP Response:", wipResponse);
  //       let wipArray = wipResponse.data.quotations || [];
  //       if (!Array.isArray(wipArray)) {
  //         console.error("wipArray is not an array:", wipArray);
  //         wipArray = [];
  //       }
  //       const wipQuotations = wipArray.map((quotation) => ({
  //         quotation_id: quotation.quotation_id,
  //         name: quotation.name, // Use the name string directly from backend
  //         status: "pending",
  //       }));

  //       // Fetch finalized quotations
  //       const finalResponse = await finalQuotationIds();
  //       let finalArray = finalResponse.data.quotations || [];
  //       if (!Array.isArray(finalArray)) {
  //         console.error("finalArray is not an array:", finalArray);
  //         finalArray = [];
  //       }
  //       const finalQuotations = finalArray.map((quotation) => ({
  //         quotation_id: quotation.quotation_id,
  //         name: quotation.name, // Placeholder since finalQuotationIds doesn't provide name
  //         status: "finalized",
  //       }));
  //       console.log(finalQuotations);
  //       setQuotations([...wipQuotations, ...finalQuotations]);
  //     } catch (error) {
  //       console.error("Error fetching quotations:", error);
  //       setError("Failed to load quotations. Please try again later.");
  //       setQuotations([]);
  //     } finally {
  //       setIsLoading(false);
  //     }
  //   }
  //   fetchQuotations();
  // }, []);

  const handleQuotationIDGeneration = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(
        "https://puranmalsons-quotation-webapp-0b4c571a2cc2.herokuapp.com/api/create_quotation",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );
      if (response.ok) {
        const result = await response.json();
        localStorage.setItem("quotationId", result.quotation_id);
        navigate("/home", { state: { quotationId: result.quotation_id } });
      } else {
        setError("Failed to create a new quotation. Please try again.");
      }
    } catch (error) {
      console.error("Error:", error);
      setError("Network error. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  // const handleView = (quotation) => {
  //   if (quotation.status === "pending") {
  //     navigate("/home", { state: { quotationId: quotation.quotation_id } });
  //   } else {
  //     navigate("/preview", { state: { quotationId: quotation.quotation_id } });
  //   }
  // };

  // const filteredQuotations = quotations.filter(
  //   (q) =>
  //     q.quotation_id.toLowerCase().includes(searchTerm.toLowerCase()) || // Search by quotation ID
  //     q.name.toLowerCase().includes(searchTerm.toLowerCase())
  // );

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-md mx-auto">
        <button
          onClick={handleQuotationIDGeneration}
          className="w-full py-3 bg-orange-400 rounded-md mb-4 font-bold text-white mt-12"
          // disabled={isLoading}
        >
          + New Quotation
        </button>

        {/* <p className="my-2 font-semibold">Existing Quotations</p>

        <input
          type="text"
          placeholder="Search Quotations"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full p-3 border border-gray-200 rounded-md mb-4"
        />

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-4">
            <div className="w-6 h-6 border-2 border-yellow-200 border-t-orange-500 rounded-full animate-spin mx-auto"></div>
          </div>
        ) : quotations.length === 0 ? (
          <div className="text-center py-4 text-gray-600">
            No quotations yet
          </div>
        ) : filteredQuotations.length === 0 ? (
          <div className="text-center py-4 text-gray-600">
            No quotations found
          </div>
        ) : (
          <div className="space-y-4">
            {filteredQuotations.map((quotation, index) => (
              <div
                key={`${quotation.quotation_id}-${quotation.name}-${index}`} // Unique key
                className="bg-white p-4 rounded-md border border-gray-200"
              >
                <div>
                  <span
                    className={`inline-flex border-1 text-xs font-semibold px-2 py-1 rounded-full ${
                      quotation.status === "pending"
                        ? "bg-red-50 text-red-600"
                        : "bg-green-50 text-green-800"
                    }`}
                  >
                    {quotation.status === "pending" ? "pending" : "Complete"}
                  </span>
                </div>
                <h3 className="text-md font-semibold mt-2">
                  {quotation.quotation_id}
                </h3>
                <p className="text-sm text-gray-600 mt-1">{quotation.name}</p>{" "} */}
        {/* Display name */}
        {/* <div className="mt-2">
                  <button
                    onClick={() => handleView(quotation)}
                    className="mt-3 py-1 px-3 bg-orange-400 text-white font-semibold rounded-2xl"
                  >
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        )} */}
      </div>
    </div>
  );
};

export default Home;
