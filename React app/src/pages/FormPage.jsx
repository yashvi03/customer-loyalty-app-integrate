import { useEffect, useState, useCallback, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import AddItem from "../components/AddItems";
import Margin from "../components/Margin";
import Card from "../components/Card";
import Customer from "../components/Customer";
import axiosInstance from "../services/axiosInstance";

const FormPage = () => {
  const [data, setData] = useState([]);
  const [isMarginCompleted, setIsMarginCompleted] = useState(false);
  const [isCustomerCompleted, setIsCustomerCompleted] = useState(false);
  const [isMarginLocked, setIsMarginLocked] = useState(false);
  const [isCustomerLocked, setIsCustomerLocked] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editData, setEditData] = useState(null);
  const [activeAccordion, setActiveAccordion] = useState(null);

  const addItemAccordionRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();
  const quotationId = location.state?.quotationId;

  const hasItems = data.length > 0;

  // Fetch initial data
  useEffect(() => {
    if (!quotationId) {
      setError("No quotation ID provided");
      setIsLoading(false);
      return;
    }

    localStorage.setItem("quotationId", quotationId);

    const fetchData = async () => {
      try {
        // Fetch required margin categories
        // let mcNamesResponse;
        // if (quotationId.includes("WIP_")) {
        //   mcNamesResponse = await axiosInstance.get(
        //     `get_mc_name/${quotationId}`
        //   );
        // }
        const mcNamesResponse = await axiosInstance.get(
          `get_mc_name/${quotationId}`
        );
        const requiredCategories = mcNamesResponse?.data?.mc_names || [];

        // Fetch quotation data
        let response;
        if (quotationId.includes("WIP_")) {
          response = await axiosInstance.get(
            `/preview_quotation/${quotationId}`
          );
        } else {
          response = await axiosInstance.get(
            `/preview_final_quotation/${quotationId}`
          );
        }

        console.log("response", response);
        if (!response.data?.cards)
          throw new Error("Invalid data format received");
        setData(response.data.cards);

        // Get current margins and create a lookup map
        const currentMargins = response.data.margins || [];
        const marginsMap = new Map(
          currentMargins.map((m) => [m.mc_name, m.margin])
        );

        // Check if all required categories have non-empty margins
        let allMarginsFilled = false;
        console.log("required categories", requiredCategories);
        if (requiredCategories.length > 0) {
          allMarginsFilled = requiredCategories.every((cat) => {
            const margin = marginsMap.get(cat.mc_name);
            return (
              margin != null && (typeof margin !== "string" || margin !== "")
            );
          });
        }

        setIsMarginCompleted(allMarginsFilled);
        setIsMarginLocked(allMarginsFilled);

        // Customer completion status (unchanged)
        const customerFilled =
          response.data.customer &&
          response.data.customer.name &&
          response.data.customer.billing_address &&
          response.data.customer.phone_number;
        setIsCustomerCompleted(customerFilled);
        setIsCustomerLocked(customerFilled);
      } catch (error) {
        setError(error.message || "Failed to fetch quotation data");
        console.error("Error fetching data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [quotationId]);

  // Handle item addition or edit, check for new unfilled margins, and refresh data
  const handleItemAdded = useCallback(async () => {
    try {
      // Fetch required margin categories
      const mcNamesResponse = await axiosInstance.get(
        `get_mc_name/${quotationId}`
      );
      const requiredCategories = mcNamesResponse.data.mc_names || [];

      // Fetch updated quotation data
      const response = await axiosInstance.get(
        `/preview_quotation/${quotationId}`
      );
      setData(response.data.cards);

      // Get current margins and create a lookup map
      const currentMargins = response.data.margins || [];
      const marginsMap = new Map(
        currentMargins.map((m) => [m.mc_name, m.margin])
      );

      // Check if all required categories have non-empty margins
      const allMarginsFilled = requiredCategories.every((cat) => {
        const margin = marginsMap.get(cat.mc_name);
        return margin != null && (typeof margin !== "string" || margin !== "");
      });

      setIsMarginCompleted(allMarginsFilled);
      setIsMarginLocked(allMarginsFilled);

      if (!allMarginsFilled) {
        setActiveAccordion("Margin"); // Open Margin section if incomplete
      } else {
        setActiveAccordion('Customer');
      }

      setEditData(null);
    } catch (error) {
      console.error("Error refreshing data after item addition:", error);
      setError("Failed to refresh quotation data");
    }
  }, [quotationId]);

  const handleMarginSaved = useCallback(() => {
    setIsMarginCompleted(true);
    setIsMarginLocked(true);
    setActiveAccordion('Customer');
  }, []);

  const handleCustomerSaved = useCallback(() => {
    setIsCustomerCompleted(true);
    setIsCustomerLocked(true);
    setActiveAccordion(null);
  }, []);

  const handleMarginChange = useCallback(() => {
    setIsMarginLocked(false);
    setActiveAccordion("Margin");
  }, []);

  const handleCustomerChange = useCallback(() => {
    setIsCustomerLocked(false);
    setActiveAccordion("Customer");
  }, []);

  const handlePreview = useCallback(async () => {
    if (!quotationId.startsWith("WIP_")) {
      try {
        const response = await axiosInstance.get(
          `/preview_final_quotation/${quotationId}`
        );
        const payload = {
          quotation_id: quotationId,
          customer_id: response.data.customer.customer_id,
          card_ids: data.map((card) => card.card_id),
          margin_ids: response.data.margins.map((m) => m.margin_id),
        };
        const saveResponse = await axiosInstance.post(
          "/final_quotation",
          payload
        );
        navigate("/preview", {
          state: { quotationId: saveResponse.data.quotation_id },
        });
      } catch (error) {
        setError("Failed to save final quotation");
        console.error(error);
        return;
      }
    } else {
      navigate("/preview", { state: { quotationId: quotationId } });
    }
  }, [navigate, quotationId, data]);

  const handleCardEdit = useCallback((card) => {
    setEditData({
      card_id: card.card_id,
      type: card.type,
      size: card.size,
      items: card.items,
    });
    setActiveAccordion("AddItem");
    if (addItemAccordionRef.current) {
      addItemAccordionRef.current.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, []);

  const handleCardDelete = useCallback(
    (card) => {
      const deleteCard = async () => {
        try {
          // Show a confirmation dialog before deletion
          const confirmDelete = window.confirm(
            "Are you sure you want to delete this item? This action cannot be undone."
          );

          if (!confirmDelete) return;

          // Make the DELETE request to the backend
          await axiosInstance.delete(`/delete_card/${card.card_id}`);

          // Update the state by removing the deleted card
          setData((prevData) =>
            prevData.filter((c) => c.card_id !== card.card_id)
          );

          // Optionally, refresh margin status after deletion
          const mcNamesResponse = await axiosInstance.get(
            `get_mc_name/${quotationId}`
          );
          const requiredCategories = mcNamesResponse.data.mc_names || [];

          const response = await axiosInstance.get(
            `/preview_quotation/${quotationId}`
          );
          const currentMargins = response.data.margins || [];
          const marginsMap = new Map(
            currentMargins.map((m) => [m.mc_name, m.margin])
          );

          const allMarginsFilled =requiredCategories.length > 0 && requiredCategories.every((cat) => {
            const margin = marginsMap.get(cat.mc_name);
            return (
              margin != null && (typeof margin !== "string" || margin !== "")
            );
          });

          setIsMarginCompleted(allMarginsFilled);
          setIsMarginLocked(allMarginsFilled);

          // If no items remain, reset completion states
          if (response.data.cards.length === 0) {
            setIsMarginCompleted(false);
            setIsMarginLocked(false);
          }
        } catch (error) {
          console.error("Failed to delete card:", error);
          alert("Couldn't delete the card. Please try again.");
        }
      };

      deleteCard();
    },
    [quotationId]
  ); // Dependencies include quotationId since it's used in API calls

  const toggleAccordion = (title) => {
    // If closing the Add Item accordion, reset editData
    if (activeAccordion === "AddItem" && title !== "AddItem") {
      setEditData(null);
    }
    setActiveAccordion(activeAccordion === title ? null : title);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center p-6 max-w-sm mx-auto">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-400 mx-auto mb-4"></div>
          <p className="text-lg font-medium text-gray-700">
            Loading your quotation...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full mx-4">
          <div className="text-red-500 text-center mb-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-12 w-12 mx-auto"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-center mb-2">Error</h2>
          <p className="text-gray-600 text-center">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="mt-6 w-full py-2 px-4 bg-orange-600 hover:bg-orange-700 text-white rounded-md transition-colors font-medium"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // EnhancedAccordion component definition
  const EnhancedAccordion = ({
    title,
    isOpen,
    onToggle,
    content,
    icon,
    canOpen = true,
    isLocked = false,
    onChangeClick,
    isCompleted = false,
  }) => {
    const getIconSvg = (iconName) => {
      switch (iconName) {
        case "plus":
          return (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                clipRule="evenodd"
              />
            </svg>
          );
        case "calculator":
          return (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2H6zm1 2a1 1 0 000 2h6a1 1 0 100-2H7zm6 7a1 1 0 011 1v3a1 1 0 11-2 0v-3a1 1 0 011-1zm-3 1a1 1 0 00-1 1v2a1 1 0 102 0v-2a1 1 0 00-1-1zm-3 0a1 1 0 00-1 1v2a1 1 0 102 0v-2a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          );
        case "user":
          return (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                clipRule="evenodd"
              />
            </svg>
          );
        default:
          return null;
      }
    };

    return (
      <div
        className={`bg-white rounded-lg border border-gray-300 overflow-hidden transition-all duration-300 ${
          !canOpen ? "opacity-50 cursor-not-allowed" : ""
        } ${isOpen ? "ring-2 ring-orange-200" : ""}`}
      >
        <div
          className={`px-4 py-4 sm:px-6 flex justify-between items-center ${
            isOpen ? "bg-gray-50 border-b border-gray-200" : "hover:bg-gray-50"
          }`}
          onClick={() => canOpen && !isLocked && onToggle()}
          style={{ cursor: canOpen && !isLocked ? "pointer" : "default" }}
        >
          <div className="flex items-center space-x-3">
            <div
              className={`p-2 rounded-full ${
                isOpen
                  ? "bg-orange-100 text-orange-700"
                  : "bg-gray-100 text-gray-500"
              }`}
            >
              {getIconSvg(icon)}
            </div>
            <h3
              className={`font-medium ${
                isOpen ? "text-orange-800" : "text-gray-700"
              }`}
            >
              {title}
            </h3>
            {isCompleted && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Completed
              </span>
            )}
          </div>
          {isLocked ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (canOpen) {
                  onChangeClick();
                }
              }}
              className={`px-3 py-1 text-sm font-medium ${
                canOpen
                  ? "text-orange-600 hover:text-orange-700"
                  : "text-gray-400 cursor-not-allowed"
              }`}
              disabled={!canOpen}
            >
              Change
            </button>
          ) : (
            <div
              className={`transition-transform duration-300 ${
                isOpen ? "rotate-180" : ""
              }`}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-gray-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          )}
        </div>
        {isOpen && (
          <div className="max-h-96 overflow-y-auto">
            <div className="p-4 sm:p-6 bg-white">{content}</div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-gray-50 min-h-screen pb-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6">
        <header className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2 text-center">
            Quotation Form
          </h1>
          <p className="text-gray-600 text-center">ID: {quotationId}</p>
        </header>

        {/* Cards Section */}
        <div className="mb-8 space-y-4">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center mb-4">
            <span className="bg-orange-500 w-2 h-6 rounded mr-2"></span>
            Your Items
          </h2>
          <div className="rounded-lg overflow-hidden">
            {data.length > 0 ? (
              <div className="divide-y divide-gray-100">
                {data.map((card) => (
                  <Card
                    key={card.card_id}
                    type={card.type}
                    size={card.size}
                    items={card.items}
                    onEdit={() => handleCardEdit(card)}
                    onDelete={() => handleCardDelete(card)}
                  />
                ))}
              </div>
            ) : (
              <div className="py-8 text-center">
                <p className="text-gray-500">No items added yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Use the "Add Item" section below to add your first item
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Accordions Section */}
        <div className="space-y-4">
          <div ref={addItemAccordionRef} className="scroll-mt-4">
            <EnhancedAccordion
              title="Add Item"
              isOpen={activeAccordion === "AddItem"}
              onToggle={() => toggleAccordion("AddItem")}
              content={
                <AddItem
                  edit={editData}
                  isEditMode={!!editData}
                  onItemAdded={handleItemAdded}
                />
              }
              icon="plus"
              canOpen={true}
              isLocked={false}
              isCompleted={hasItems}
            />
          </div>

          <EnhancedAccordion
            title="Margin Settings"
            isOpen={activeAccordion === "Margin"}
            onToggle={() => toggleAccordion("Margin")}
            content={<Margin onSave={handleMarginSaved} />}
            icon="calculator"
            canOpen={hasItems}
            isLocked={isMarginLocked}
            onChangeClick={handleMarginChange}
            isCompleted={isMarginCompleted}
          />

          <EnhancedAccordion
            title="Customer Information"
            isOpen={activeAccordion === "Customer"}
            onToggle={() => toggleAccordion("Customer")}
            content={<Customer onCustomerSaved={handleCustomerSaved} />}
            icon="user"
            canOpen={isMarginCompleted}
            isLocked={isCustomerLocked}
            onChangeClick={handleCustomerChange}
            isCompleted={isCustomerCompleted}
          />
        </div>

        {/* Preview Button */}
        {hasItems && isMarginCompleted && isCustomerCompleted && (
          <div className="mt-8 bg-white p-4 rounded-lg shadow-md border border-gray-200">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <div className="text-green-600 flex items-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 mr-2"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-medium">
                  All sections completed
                </span>
              </div>
              <button
                onClick={handlePreview}
                className="w-full sm:w-auto px-6 py-3 bg-orange-600 text-white font-medium rounded-md hover:bg-orange-700 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 shadow-sm"
              >
                Preview Quotation
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FormPage;