import axiosInstance from "./axiosInstance";

export const createQuotation = () => axiosInstance.post('/create_quotation')
export const getFilter = (data) => axiosInstance.get(`items/filter?${data}`);
export const addCard = (data) => axiosInstance.post("/cards", data);
export const updateCard = (card_id, data) =>
  axiosInstance.put(`/update_card/${card_id}`, data);
export const addCardToQuotation = (data) =>
  axiosInstance.post("/add_card_to_quotation", data);
export const getMcNames = (quotationId) =>
  axiosInstance.get(`get_mc_name/${quotationId}`);
export const addMargin = (quotationId, data) =>
  axiosInstance.post(`/add_margin/${quotationId}`, data);
export const addMarginToQuotation = (data) =>
  axiosInstance.post(`add_margin_to_quotation`, data);
export const addCustomer = (quotationId, data) =>
  axiosInstance.post(`add_customer/${quotationId}`, data);
export const addCustomerToQuotation = (data) =>
  axiosInstance.post("/add_customer_to_quotation", data);
export const getExistingCustomers = () => axiosInstance.get("/get_customer");
export const getQuotation = (id) =>
  axiosInstance.get(`/preview_quotation/${id}`);
export const finalQuotation = (data) =>
  axiosInstance.post("/final_quotation", data);
export const previewFinalQuotation = (id) =>
  axiosInstance.post(`/preview_final_quotation/${id}`);
export const deleteWipQuotation = (id, data) =>
  axiosInstance.delete(`/delete_quotation/${id}`, data);
export const editFinalQuotation = (data) =>
  axiosInstance.post(`/wip_quotation/`, data);
// export const downloadPDF = (data) => axiosInstance.post('download-pdf',data);
export const wipQuotationIds = () => axiosInstance.get('/get_all_quotations');
export const finalQuotationIds = () => axiosInstance.get('/get_final_quotations');