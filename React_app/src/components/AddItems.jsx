import { useEffect, useState, useCallback, useRef } from "react";
import {
  addCard,
  addCardToQuotation,
  createQuotation,
  updateCard,
} from "../services/api";

const AddItems = ({ edit, isEditMode, onItemAdded }) => {
  // State for controlling the current step in the selection process
  const [nextStep, setNextStep] = useState("type");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // State for storing available options for each step
  const [options, setOptions] = useState({
    type: [],
    size: [],
    article: [],
  });

  // State for storing filter parameters for API calls
  const [filters, setFilters] = useState({});

  // State for storing selected values
  const [selectedOptions, setSelectedOptions] = useState({
    type: "",
    size: "",
    article: [],
  });

  // State for tracking the currently active article
  const [activeArticle, setActiveArticle] = useState(null);

  // State for form validation
  const [isFormValid, setIsFormValid] = useState(false);

  // Ref to track pending API fetches and prevent duplicates
  const pendingFetches = useRef(new Set());

  // Refs for each section for scrolling
  const typeSectionRef = useRef(null);
  const sizeSectionRef = useRef(null);
  const articleSectionRef = useRef(null);

  // Function to auto-select single option categories
  const autoSelectSingleOptions = useCallback(
    (articleValue, updatedArticle) => {
      let autoUpdatedArticle = { ...updatedArticle };

      // Auto-select cat1 if only one option
      if (
        autoUpdatedArticle.cat1Options.length === 1 &&
        !autoUpdatedArticle.cat1
      ) {
        autoUpdatedArticle.cat1 = autoUpdatedArticle.cat1Options[0].value;

        // Fetch cat2 options when cat1 is auto-selected
        const fetchKey = `${articleValue}-cat2-auto`;
        if (!pendingFetches.current.has(fetchKey)) {
          pendingFetches.current.add(fetchKey);
          fetchOptions({
            type: selectedOptions.type,
            size: selectedOptions.size,
            article: articleValue,
            cat1: autoUpdatedArticle.cat1,
          }).finally(() => {
            pendingFetches.current.delete(fetchKey);
          });
        }
      }

      return autoUpdatedArticle;
    },
    [selectedOptions.type, selectedOptions.size]
  );

  // Memoized function to fetch category options from the API
  const fetchOptions = useCallback(async (filters) => {
    const params = new URLSearchParams(filters);
    try {
      const response = await fetch(
        `https://puranmalsons-quotation-webapp-0b4c571a2cc2.herokuapp.com/api2/items/filter?${params}`
      );
      const data = await response.json();
      if (data.options && filters.article) {
        const filteredOptions = data.options.filter((opt) => opt.value) || [];
        setSelectedOptions((prev) => {
          const updatedArticles = prev.article.map((article) => {
            if (article.value === filters.article) {
              let updatedArticle = { ...article };

              if (filters.cat2) {
                updatedArticle.cat3Options = filteredOptions;
                // Auto-select cat3 if only one option
                if (filteredOptions.length === 1 && !updatedArticle.cat3) {
                  updatedArticle.cat3 = filteredOptions[0].value;
                }
              } else if (filters.cat1) {
                updatedArticle.cat2Options = filteredOptions;
                // Auto-select cat2 if only one option
                if (filteredOptions.length === 1 && !updatedArticle.cat2) {
                  updatedArticle.cat2 = filteredOptions[0].value;

                  // Fetch cat3 options when cat2 is auto-selected
                  const fetchKey = `${filters.article}-cat3-auto`;
                  if (!pendingFetches.current.has(fetchKey)) {
                    pendingFetches.current.add(fetchKey);
                    fetchOptions({
                      type: prev.type,
                      size: prev.size,
                      article: filters.article,
                      cat1: filters.cat1,
                      cat2: filteredOptions[0].value,
                    }).finally(() => {
                      pendingFetches.current.delete(fetchKey);
                    });
                  }
                }
              } else {
                updatedArticle.cat1Options = filteredOptions;
                // Auto-select cat1 if only one option
                if (filteredOptions.length === 1 && !updatedArticle.cat1) {
                  updatedArticle.cat1 = filteredOptions[0].value;

                  // Fetch cat2 options when cat1 is auto-selected
                  const fetchKey = `${filters.article}-cat2-auto`;
                  if (!pendingFetches.current.has(fetchKey)) {
                    pendingFetches.current.add(fetchKey);
                    fetchOptions({
                      type: prev.type,
                      size: prev.size,
                      article: filters.article,
                      cat1: filteredOptions[0].value,
                    }).finally(() => {
                      pendingFetches.current.delete(fetchKey);
                    });
                  }
                }
              }

              return updatedArticle;
            }
            return article;
          });
          return { ...prev, article: updatedArticles };
        });
      }
    } catch (error) {
      console.error("Error fetching options:", error);
    }
  }, []);

  // Initialize state when in edit mode
  useEffect(() => {
    if (isEditMode && edit) {
      const initialArticles =
        edit.items?.map((item) => ({
          value: item.article,
          qty: item.quantity,
          cat1: item.cat1 || "",
          cat2: item.cat2 || "",
          cat3: item.cat3 || "",
          item_id: item.item_id,
          cat1Options: [],
          cat2Options: [],
          cat3Options: [],
          cat1Fetched: false,
        })) || [];

      setSelectedOptions({
        type: edit.type || "",
        size: edit.size || "",
        article: initialArticles,
      });

      setFilters({
        type: edit.type || "",
        size: edit.size || "",
      });

      if (initialArticles.length > 0) {
        setActiveArticle(initialArticles[0].value);
      }
    }
  }, [isEditMode, edit]);

  // Fetch type and size options based on filters
  useEffect(() => {
    async function fetchFilters() {
      if (nextStep === "type" || nextStep === "size") {
        const params = new URLSearchParams(filters);
        try {
          const response = await fetch(
            `https://puranmalsons-quotation-webapp-0b4c571a2cc2.herokuapp.com/api2/items/filter?${params}`
          );
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          if (data.next_step) {
            setNextStep(data.next_step);
          }
          if (data.options) {
            const filteredOptions =
              data.options?.filter((opt) => opt.value) || [];
            setOptions((prev) => ({
              ...prev,
              [data.next_step]: filteredOptions,
            }));
          }
        } catch (error) {
          console.error("Error fetching filters:", error);
        }
      }
    }
    fetchFilters();
  }, [filters, nextStep]);

  // Auto-scroll based on changes in nextStep
  useEffect(() => {
    const scrollToElement = (element) => {
      if (element) {
        element.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    };

    const scrollTimeout = setTimeout(() => {
      if (
        nextStep === "size" &&
        selectedOptions.type &&
        sizeSectionRef.current
      ) {
        scrollToElement(sizeSectionRef.current);
      } else if (
        nextStep === "article" &&
        selectedOptions.size &&
        articleSectionRef.current
      ) {
        scrollToElement(articleSectionRef.current);
      }
    }, 300);

    return () => clearTimeout(scrollTimeout);
  }, [nextStep, selectedOptions.type, selectedOptions.size]);

  // Fetch initial category options (cat1) for articles
  useEffect(() => {
    selectedOptions.article.forEach((article) => {
      const fetchKey = `${article.value}-cat1`;
      if (
        article.cat1Options.length === 0 &&
        !article.cat1Fetched &&
        !pendingFetches.current.has(fetchKey)
      ) {
        pendingFetches.current.add(fetchKey);
        fetchOptions({
          type: selectedOptions.type,
          size: selectedOptions.size,
          article: article.value,
        }).finally(() => {
          pendingFetches.current.delete(fetchKey);
          setSelectedOptions((prev) => {
            const updatedArticles = prev.article.map((a) => {
              if (a.value === article.value) {
                return { ...a, cat1Fetched: true };
              }
              return a;
            });
            return { ...prev, article: updatedArticles };
          });
        });
      }
    });
  }, [
    selectedOptions.article,
    selectedOptions.type,
    selectedOptions.size,
    fetchOptions,
  ]);

  // Validate the form based on selected articles
  useEffect(() => {
    if (selectedOptions.article.length === 0) {
      setIsFormValid(false);
      return;
    }

    const allArticlesValid = selectedOptions.article.every((article) => {
      if (!article.qty || article.qty < 1) return false;
      if (article.cat1Options.length > 0 && !article.cat1) return false;
      if (article.cat1 && article.cat2Options.length > 0 && !article.cat2)
        return false;
      if (article.cat2 && article.cat3Options.length > 0 && !article.cat3)
        return false;
      return true;
    });

    setIsFormValid(allArticlesValid);
  }, [selectedOptions.article]);

  // Handle selection of type, size, or article
  const handleSelection = (value) => {
    if (nextStep === "article") {
      const existingArticleIndex = selectedOptions.article.findIndex(
        (item) => item.value === value
      );

      if (existingArticleIndex >= 0) {
        const updatedArticles = selectedOptions.article.filter(
          (item) => item.value !== value
        );

        if (activeArticle === value) {
          setActiveArticle(
            updatedArticles.length > 0 ? updatedArticles[0].value : null
          );
        }

        setSelectedOptions((prev) => ({
          ...prev,
          article: updatedArticles,
        }));
      } else {
        if (activeArticle) {
          const currentArticle = getArticleData(activeArticle);
          if (isArticleIncomplete(currentArticle)) {
            alert(
              "Please complete all fields for the current article before selecting another."
            );
            return;
          }
        }

        const updatedArticles = [
          ...selectedOptions.article,
          {
            value,
            cat1: "",
            cat2: "",
            cat3: "",
            qty: null,
            cat1Options: [],
            cat2Options: [],
            cat3Options: [],
            cat1Fetched: false,
          },
        ];

        setActiveArticle(value);

        setSelectedOptions((prev) => ({
          ...prev,
          article: updatedArticles,
        }));
      }
    } else {
      setFilters((prev) => ({
        ...prev,
        [nextStep]: value,
      }));
      setSelectedOptions((prev) => ({
        ...prev,
        [nextStep]: value,
      }));
    }
  };

  // Update article properties (e.g., qty, cat1, cat2, cat3)
  const updateArticleProperty = (articleValue, property, newValue) => {
    setSelectedOptions((prev) => {
      const updatedArticles = prev.article.map((item) => {
        if (item.value === articleValue) {
          if (property === "cat1") {
            const fetchKey = `${articleValue}-cat2`;
            if (
              newValue &&
              item.cat2Options.length === 0 &&
              !pendingFetches.current.has(fetchKey)
            ) {
              pendingFetches.current.add(fetchKey);
              fetchOptions({
                type: prev.type,
                size: prev.size,
                article: articleValue,
                cat1: newValue,
              }).finally(() => {
                pendingFetches.current.delete(fetchKey);
              });
            }
            return {
              ...item,
              cat1: newValue,
              cat2: "",
              cat3: "",
              cat2Options: [],
              cat3Options: [],
            };
          } else if (property === "cat2") {
            const fetchKey = `${articleValue}-cat3`;
            if (
              newValue &&
              item.cat3Options.length === 0 &&
              !pendingFetches.current.has(fetchKey)
            ) {
              pendingFetches.current.add(fetchKey);
              fetchOptions({
                type: prev.type,
                size: prev.size,
                article: articleValue,
                cat1: item.cat1,
                cat2: newValue,
              }).finally(() => {
                pendingFetches.current.delete(fetchKey);
              });
            }
            return {
              ...item,
              cat2: newValue,
              cat3: "",
              cat3Options: [],
            };
          }
          return { ...item, [property]: newValue };
        }
        return item;
      });
      return { ...prev, article: updatedArticles };
    });

    setActiveArticle(articleValue);
  };

  // Handle changing selections at different steps
  const handleChange = (step) => {
    if (step === "type") {
      setSelectedOptions({ type: "", size: "", article: [] });
      setFilters({});
      setNextStep("type");
      setActiveArticle(null);

      if (typeSectionRef.current) {
        typeSectionRef.current.scrollIntoView({ behavior: "smooth" });
      }
    } else if (step === "size") {
      setSelectedOptions((prev) => ({
        type: prev.type,
        size: "",
        article: [],
      }));
      setFilters((prev) => ({ type: prev.type }));
      setNextStep("size");
      setActiveArticle(null);

      if (sizeSectionRef.current) {
        sizeSectionRef.current.scrollIntoView({ behavior: "smooth" });
      }
    } else if (step === "article") {
      setSelectedOptions((prev) => ({
        type: prev.type,
        size: prev.size,
        article: [],
      }));
      setFilters((prev) => ({ type: prev.type, size: prev.size }));
      setNextStep("article");
      setActiveArticle(null);

      if (articleSectionRef.current) {
        articleSectionRef.current.scrollIntoView({ behavior: "smooth" });
      }
    }
  };

  // Check if an article is selected
  const isArticleSelected = (articleValue) => {
    return selectedOptions.article.some((item) => item.value === articleValue);
  };

  // Get data for a specific article
  const getArticleData = (articleValue) => {
    return (
      selectedOptions.article.find((item) => item.value === articleValue) || {}
    );
  };

  // Check if an article has incomplete fields
  const isArticleIncomplete = (article) => {
    if (!article.qty || article.qty < 1) return true;
    if (article.cat1Options.length > 0 && !article.cat1) return true;
    if (article.cat1 && article.cat2Options.length > 0 && !article.cat2)
      return true;
    if (article.cat2 && article.cat3Options.length > 0 && !article.cat3)
      return true;
    return false;
  };

  const handleQuotationIDGeneration = async () => {
    try {
      const response = await createQuotation();
      if (response.ok) {
        const result = await response.json();
        localStorage.setItem("quotationId", result.quotation_id);
      } else {
        console.log("Failed to create a new quotation. Please try again.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      if (!localStorage.getItem("quotationId").includes("WIP"))
        await handleQuotationIDGeneration();

      const payload = {
        quotation_id: localStorage.getItem("quotationId"),
        type: selectedOptions.type,
        size: selectedOptions.size,
        items: selectedOptions.article.map((item) => ({
          item_id: item.item_id,
          name: item.value,
          quantity: item.qty,
          cat1: item.cat1,
          cat2: item.cat2,
          cat3: item.cat3,
        })),
      };

      let response;
      if (isEditMode && edit?.card_id) {
        response = await updateCard(edit.card_id, payload);
      } else {
        response = await addCard(payload);
        const quotationData = {
          quotation_id: localStorage.getItem("quotationId"),
          card_id: response.data.card.card_id,
        };
        await addCardToQuotation(quotationData);
      }

      // Reset form state
      setSelectedOptions({ type: "", size: "", article: [] });
      setFilters({});
      setNextStep("type");
      setActiveArticle(null);

      if (onItemAdded) {
        onItemAdded();
      }
    } catch (error) {
      console.error("Error with card operation:", error);
      alert(
        `Error ${isEditMode ? "updating" : "adding"} card: ${error.message}`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8">
      {/* Type Selection */}
      <div className="mb-8" ref={typeSectionRef}>
        <div className="flex justify-between mb-4 items-center">
          <h3 className="font-semibold text-lg">Select Material</h3>
          {selectedOptions.type && !selectedOptions.size && (
            <button
              className="text-orange-400 hover:underline"
              onClick={() => handleChange("type")}
            >
              change
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {options.type.map((option) => (
            <label
              key={option.value}
              className={`flex flex-col items-center p-4 border rounded cursor-pointer transition
                ${
                  selectedOptions.type === option.value
                    ? "border-orange-400"
                    : "border-black"
                }
                ${
                  selectedOptions.type && option.value !== selectedOptions.type
                    ? "opacity-50"
                    : ""
                }
                ${!selectedOptions.type ? "hover:border-orange-400" : ""}`}
            >
              <input
                type="radio"
                name="type"
                value={option.value}
                checked={selectedOptions.type === option.value}
                onChange={() => {
                  handleSelection(option.value);
                }}
                disabled={
                  !!selectedOptions.type &&
                  selectedOptions.type !== option.value
                }
                className="hidden"
              />
              {option.image_url && (
                <img
                  src={option.image_url}
                  alt={option.value}
                  className="w-24 h-12 object-contain mb-2"
                />
              )}
              <span className="text-center">{option.value}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Size Selection */}
      <div className="mb-8" ref={sizeSectionRef}>
        <div className="flex justify-between mb-4 items-center">
          <h3
            className={`font-semibold text-lg ${
              selectedOptions.type ? "text-black" : "text-gray-400"
            }`}
          >
            Select Size
          </h3>
          {selectedOptions.size && selectedOptions.article.length === 0 && (
            <button
              className="text-orange-400 hover:underline"
              onClick={() => handleChange("size")}
            >
              change
            </button>
          )}
        </div>
        <div>
          <select
            className={`border p-4 rounded-lg w-full md:w-1/3 ${
              !selectedOptions.type || selectedOptions.article.length > 0
                ? "border-gray-300 bg-gray-100 text-gray-600"
                : "border-black"
            }`}
            disabled={
              !selectedOptions.type ||
              selectedOptions.article.length > 0 ||
              selectedOptions.size
            }
            value={selectedOptions.size}
            onChange={(e) => handleSelection(e.target.value)}
          >
            <option value="" disabled>
              Select a size...
            </option>
            {options.size.map((option) => (
              <option key={option.value} value={option.value}>
                {option.value}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Article Selection */}
      <div className="mb-8" ref={articleSectionRef}>
        <div className="flex justify-between mb-4 items-center">
          <h3
            className={`font-semibold text-lg ${
              selectedOptions.size ? "text-black" : "text-gray-400"
            }`}
          >
            Select Articles
          </h3>
          {selectedOptions.article.length > 0 && (
            <button
              className="text-orange-400 hover:underline"
              onClick={() => handleChange("article")}
            >
              change
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {options.article.map((option) => {
            const articleData = getArticleData(option.value);
            const isIncomplete =
              isArticleSelected(option.value) &&
              isArticleIncomplete(articleData);
            const isDisabled =
              activeArticle &&
              activeArticle !== option.value &&
              isArticleIncomplete(getArticleData(activeArticle));

            return (
              <div
                key={option.value}
                className={`border rounded p-4 ${
                  isArticleSelected(option.value)
                    ? isIncomplete
                      ? "border-red-400"
                      : "border-orange-400"
                    : "border-gray-300"
                } ${isDisabled ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                <div className="flex items-center mb-4">
                  <input
                    type="checkbox"
                    id={`article-${option.value}`}
                    name="article"
                    value={option.value}
                    checked={isArticleSelected(option.value)}
                    onChange={() => handleSelection(option.value)}
                    disabled={!selectedOptions.size || isDisabled}
                    className="mr-3 h-5 w-5"
                  />
                  <label
                    htmlFor={`article-${option.value}`}
                    className="font-medium text-lg flex items-center gap-4"
                  >
                    {option.image_url && (
                      <img
                        src={option.image_url}
                        alt={option.value}
                        className="w-24 h-24 object-contain mb-2"
                      />
                    )}
                    {option.value}
                  </label>
                </div>

                {isArticleSelected(option.value) && (
                  <div className="pl-8 space-y-4">
                    <div className="flex items-center">
                      <label className="mr-2 w-20">Quantity:</label>
                      <input
                        type="text"
                        value={articleData.qty || 0}
                        onChange={(e) =>
                          updateArticleProperty(
                            option.value,
                            "qty",
                            parseInt(e.target.value) || 0
                          )
                        }
                        className={`border rounded p-2 w-20 ${
                          !articleData.qty || articleData.qty < 1
                            ? "border-red-400"
                            : ""
                        }`}
                      />
                    </div>

                    {articleData.qty &&
                      articleData.qty > 0 &&
                      articleData.cat1Options.length > 0 && (
                        <div className="flex items-center">
                          <label className="mr-2 w-20">Category 1:</label>
                          <select
                            value={articleData.cat1 || ""}
                            onChange={(e) =>
                              updateArticleProperty(
                                option.value,
                                "cat1",
                                e.target.value
                              )
                            }
                            className={`border rounded p-2 flex-grow ${
                              !articleData.cat1 &&
                              articleData.cat1Options.length > 1
                                ? "border-red-400"
                                : ""
                            }`}
                            disabled={articleData.cat1Options.length === 1}
                          >
                            <option value="" disabled>
                              {articleData.cat1Options.length === 1
                                ? "Auto-selected"
                                : "Select..."}
                            </option>
                            {articleData.cat1Options.map((catOption) => (
                              <option
                                key={catOption.value}
                                value={catOption.value}
                              >
                                {catOption.value}
                              </option>
                            ))}
                          </select>
                        </div>
                      )}

                    {articleData.qty &&
                      articleData.qty > 0 && articleData.cat1 && articleData.cat2Options.length > 0 && (
                      <div className="flex items-center">
                        <label className="mr-2 w-20">Category 2:</label>
                        <select
                          value={articleData.cat2 || ""}
                          onChange={(e) =>
                            updateArticleProperty(
                              option.value,
                              "cat2",
                              e.target.value
                            )
                          }
                          className={`border rounded p-2 flex-grow ${
                            !articleData.cat2 &&
                            articleData.cat2Options.length > 1
                              ? "border-red-400"
                              : ""
                          }`}
                          disabled={
                            !articleData.cat1 ||
                            articleData.cat2Options.length === 1
                          }
                        >
                          <option value="" disabled>
                            {articleData.cat2Options.length === 1
                              ? "Auto-selected"
                              : "Select..."}
                          </option>
                          {articleData.cat2Options.map((catOption) => (
                            <option
                              key={catOption.value}
                              value={catOption.value}
                            >
                              {catOption.value}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}

                    {articleData.qty &&
                      articleData.qty > 0 && articleData.cat1 && articleData.cat3Options.length > 0 && (
                      <div className="flex items-center">
                        <label className="mr-2 w-20">Category 3:</label>
                        <select
                          value={articleData.cat3 || ""}
                          onChange={(e) =>
                            updateArticleProperty(
                              option.value,
                              "cat3",
                              e.target.value
                            )
                          }
                          className={`border rounded p-2 flex-grow ${
                            !articleData.cat3 &&
                            articleData.cat3Options.length > 1
                              ? "border-red-400"
                              : ""
                          }`}
                          disabled={
                            !articleData.cat2 ||
                            articleData.cat3Options.length === 1
                          }
                        >
                          <option value="" disabled>
                            {articleData.cat3Options.length === 1
                              ? "Auto-selected"
                              : "Select..."}
                          </option>
                          {articleData.cat3Options.map((catOption) => (
                            <option
                              key={catOption.value}
                              value={catOption.value}
                            >
                              {catOption.value}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}

                    {isIncomplete && (
                      <div className="text-red-500 text-sm">
                        Please complete all fields for this article
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary Section */}
      {selectedOptions.article.length > 0 && (
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-lg mb-2">Selected Items</h3>
          <ul className="divide-y">
            {selectedOptions.article.map((item, index) => {
              const categoryEntries = [];
              if (item.cat1 && item.cat1Options.length > 0)
                categoryEntries.push(`${item.cat1}`);
              if (item.cat2 && item.cat2Options.length > 0)
                categoryEntries.push(`${item.cat2}`);
              if (item.cat3 && item.cat3Options.length > 0)
                categoryEntries.push(`${item.cat3}`);

              return (
                <li key={index} className="py-2">
                  <div className="font-medium">
                    {item.value} {categoryEntries.join(" ")} × {item.qty}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {/* Save and Next Button */}
      <div className="mt-8">
        <button
          className={`px-6 py-2 rounded font-medium ${
            isFormValid && !isSubmitting
              ? "bg-orange-400 text-white hover:bg-orange-500"
              : "bg-gray-300 text-gray-500 cursor-not-allowed"
          }`}
          disabled={!isFormValid || isSubmitting}
          onClick={handleSubmit}
        >
          {isSubmitting
            ? isEditMode
              ? "Updating..."
              : "Saving..."
            : isEditMode
            ? "Update"
            : "Save and Next"}
        </button>

        {selectedOptions.article.length > 0 && !isFormValid && (
          <p className="text-red-500 mt-2">
            Please complete all required fields for selected articles before
            proceeding
          </p>
        )}
      </div>
    </div>
  );
};

export default AddItems;
