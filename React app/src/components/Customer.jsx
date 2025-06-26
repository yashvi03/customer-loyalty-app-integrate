import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import axiosInstance from "../services/axiosInstance";

const Customer = ({ onCustomerSaved }) => {
  const [title, setTitle] = useState("");
  const [name, setName] = useState("");
  const [projectName, setProjectName] = useState("");
  const [billingAddress, setBillingAddress] = useState("");
  const [shippingAddress, setShippingAddress] = useState("");
  const [sameAsBilling, setSameAsBilling] = useState(false);
  const [sameAsName, setSameAsName] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [whatsappNumber, setWhatsappNumber] = useState("");
  const [sameAsPhone, setSameAsPhone] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const location = useLocation();
  const quotationId = location.state?.quotationId;

  // Helper function to strip +91 prefix from phone numbers
  const stripPrefix = (number) => {
    if (number && number.startsWith("+91")) {
      return number.substring(3); // Remove +91 prefix
    }
    return number;
  };

  useEffect(() => {
    if (!quotationId) {
      setError("Error: Quotation ID is missing.");
      setLoading(false);
      return;
    }

    async function getExistingCustomers() {
      try {
        setLoading(true);
        const response = await axiosInstance.get("/get_customer");
        const customerData = response.data.map((d) => ({
          customer_id: d.customer_id,
          title: d.title,
          name: d.name,
          project_name: d.project_name,
          billing_address: d.billing_address,
          shipping_address: d.shipping_address,
          phone_number: d.phone_number,
          whatsapp_number: d.whatsapp_number,
          // Store formatted numbers for display
          formatted_phone: stripPrefix(d.phone_number),
          formatted_whatsapp: stripPrefix(d.whatsapp_number),
        }));

        const previewResponse = await axiosInstance.get(
          `preview_quotation/${quotationId}`
        );
        if (previewResponse.data.customer) {
          const customer = previewResponse.data.customer;
          setTitle(customer.title || "");
          setName(customer.name || "");
          setProjectName(customer.project_name || "");
          setBillingAddress(customer.billing_address || "");
          setShippingAddress(customer.shipping_address || "");
          setPhoneNumber(stripPrefix(customer.phone_number) || "");
          setWhatsappNumber(stripPrefix(customer.whatsapp_number) || "");
          setSameAsName(customer.name === customer.project_name);
          setSameAsBilling(
            customer.billing_address === customer.shipping_address
          );
          setSameAsPhone(customer.phone_number === customer.whatsapp_number);
        }
        setCustomers(customerData);
        setLoading(false);
      } catch (error) {
        console.log(error);
        setError("Failed to load customer data. Please try again.");
        setLoading(false);
      }
    }
    getExistingCustomers();
  }, [quotationId]);

  const handlePhoneChange = (e) => {
    setPhoneNumber(e.target.value);
    if (sameAsPhone) setWhatsappNumber(e.target.value);
  };

  const handleWhatsappChange = (e) => setWhatsappNumber(e.target.value);

  const handleSameAsPhone = () => {
    const newValue = !sameAsPhone;
    setSameAsPhone(newValue);
    if (newValue) setWhatsappNumber(phoneNumber);
  };

  const handleSameAsName = () => {
    const newValue = !sameAsName;
    setSameAsName(newValue);
    if (newValue) setProjectName(name);
  };

  const handleSameAsBilling = () => {
    const newValue = !sameAsBilling;
    setSameAsBilling(newValue);
    if (newValue) setShippingAddress(billingAddress);
  };

  const handleBillingAddressChange = (e) => {
    setBillingAddress(e.target.value);
    if (sameAsBilling) setShippingAddress(e.target.value);
  };

  const handleNameChange = (e) => {
    setName(e.target.value);
    if (sameAsName) setProjectName(e.target.value);
  };

  const handleSubmit = async () => {
    try {
      const customerData = {
        title: title,
        name: name,
        project_name: projectName,
        billing_address: billingAddress,
        shipping_address: shippingAddress,
        phone_number: "+91" + phoneNumber,
        whatsapp_number: "+91" + whatsappNumber,
      };

      if (!name || !projectName || !billingAddress || !phoneNumber) {
        alert(
          "Please fill in all required fields: Name, Billing Address, and Phone Number"
        );
        return;
      }

      const response = await axiosInstance.post(
        `add_customer/${quotationId}`,
        customerData
      );
      const quotationCustomerData = {
        quotation_id: quotationId,
        customer_id: response.data.customer.customer_id,
      };
      await axiosInstance.post(
        "/add_customer_to_quotation",
        quotationCustomerData
      );
      // alert("Customer information saved successfully!");
      onCustomerSaved(); // Notify parent only on success
    } catch (error) {
      console.error("Error submitting customer:", error);
      alert("An error occurred while submitting the customer information.");
    }
  };

  const handleSelect = (e) => {
    const selectedCustomerId = e.target.value;
    if (!selectedCustomerId) return;
    const selectedCustomer = customers.find(
      (customer) => customer.customer_id === selectedCustomerId
    );
    if (selectedCustomer) {
      setTitle(selectedCustomer.title || "");
      setName(selectedCustomer.name || "");
      setProjectName(selectedCustomer.project_name || "");
      setBillingAddress(selectedCustomer.billing_address || "");
      setShippingAddress(selectedCustomer.shipping_address || "");
      setPhoneNumber(stripPrefix(selectedCustomer.phone_number) || "");
      setWhatsappNumber(stripPrefix(selectedCustomer.whatsapp_number) || "");
      setSameAsName(selectedCustomer.name === selectedCustomer.project_name);
      setSameAsBilling(
        selectedCustomer.billing_address === selectedCustomer.shipping_address
      );
      setSameAsPhone(
        selectedCustomer.phone_number === selectedCustomer.whatsapp_number
      );
    }
  };

  if (error) {
    return (
      <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg">
        {error}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-medium mb-2">
          Select from Existing Customers
        </label>
        <select
          className="appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
          name="existing_customers"
          id="existing_customers"
          onChange={handleSelect}
        >
          <option value="">-- Select a customer --</option>
          {customers.map((customer) => (
            <option key={customer.customer_id} value={customer.customer_id}>
              {customer.name} -{" "}
              {customer.shipping_address &&
                customer.shipping_address.substring(0, 20)}
              ... - {stripPrefix(customer.phone_number)}
            </option>
          ))}
        </select>
      </div>

      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-medium mb-2">
          Title
        </label>
        <div className="flex space-x-4 mb-4">
          {["Mrs.", "Mr.", "M/S"].map((value) => (
            <label key={value} className="inline-flex items-center">
              <input
                type="radio"
                name="title"
                value={value}
                checked={title === value}
                onChange={(e) => setTitle(e.target.value)}
                className="form-radio h-4 w-4 text-orange-600"
              />
              <span className="ml-2 text-gray-700">{value}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-medium mb-2">
          Name <span className="text-red-500">*</span>
        </label>
        <input
          className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
          type="text"
          placeholder="Enter customer name"
          value={name}
          onChange={handleNameChange}
          required
        />
      </div>

      <div className="mb-6">
        <div className="flex flex-col mb-2">
          <label className="block text-gray-700 text-sm font-medium mb-2">
            Project Name <span className="text-red-500">*</span>
          </label>
          <label className="inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={sameAsName}
              onChange={handleSameAsName}
              className="form-checkbox h-4 w-4 text-orange-600"
            />
            <span className="ml-2 text-sm text-gray-600">Same as Name</span>
          </label>
        </div>

        <input
          className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
          type="text"
          placeholder="Enter project name"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          required
        />
      </div>

      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-medium mb-2">
          Billing Address <span className="text-red-500">*</span>
        </label>
        <textarea
          className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
          placeholder="Enter billing address"
          value={billingAddress}
          onChange={handleBillingAddressChange}
          rows="3"
          required
        ></textarea>
      </div>

      <div className="mb-6">
        <div className="flex flex-col mb-2">
          <label className="block text-gray-700 text-sm font-medium">
            Shipping Address
          </label>
          <label className="inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={sameAsBilling}
              onChange={handleSameAsBilling}
              className="form-checkbox h-4 w-4 text-orange-600"
            />
            <span className="ml-2 text-sm text-gray-600">
              Same as Billing Address
            </span>
          </label>
        </div>
        <textarea
          className={`appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white ${
            sameAsBilling ? "bg-gray-100" : ""
          }`}
          placeholder="Enter shipping address"
          value={shippingAddress}
          onChange={(e) => setShippingAddress(e.target.value)}
          rows="3"
          disabled={sameAsBilling}
        ></textarea>
      </div>

      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-medium mb-2">
          Phone Number <span className="text-red-500">*</span>
        </label>
        <input
          className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
          type="tel"
          placeholder="Phone Number"
          maxLength={10}
          minLength={10}
          value={phoneNumber}
          onChange={handlePhoneChange}
          required
        />
      </div>

      <div className="mb-6">
        <div className="flex flex-col mb-2">
          <label className="block text-gray-700 text-sm font-medium">
            WhatsApp Number
          </label>
          <label className="inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              maxLength={10}
              minLength={10}
              checked={sameAsPhone}
              onChange={handleSameAsPhone}
              className="form-checkbox h-4 w-4 text-orange-600"
            />
            <span className="ml-2 text-sm text-gray-600">
              Same as Phone Number
            </span>
          </label>
        </div>
        <input
          className={`appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white ${
            sameAsPhone ? "bg-gray-100" : ""
          }`}
          type="tel"
          placeholder="WhatsApp Number"
          value={whatsappNumber}
          onChange={handleWhatsappChange}
          disabled={sameAsPhone}
        />
      </div>

      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={handleSubmit}
          className="bg-orange-500 hover:bg-orange-700 text-white font-medium py-2 px-6 rounded focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition duration-150 ease-in-out"
        >
          Save and Continue
        </button>
      </div>
    </div>
  );
};

export default Customer;