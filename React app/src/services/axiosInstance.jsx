import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "https://puranmalsons-quotation-webapp-0b4c571a2cc2.herokuapp.com/api",
  headers: {
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      showAlert("Unauthorized! Redirecting to login...");
      //   window.location.href = "/";
    }

    return Promise.reject(error);
  }
);

let showAlert = () => {};

export const setShowAlert = (func) => {
  showAlert = func;
};

export default axiosInstance;
