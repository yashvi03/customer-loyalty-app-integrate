import { useEffect, useState, useCallback, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axiosInstance from "../services/axiosInstance";
import "../App.css";
import ConfirmationModal from "../components/ConfirmationModel";
import { editFinalQuotation } from "../services/api";
import { useLocation } from "react-router-dom";

// Enhanced Android Bridge Class with WhatsApp-specific methods
class AndroidBridge {
  constructor() {
    this.isAndroid = this.checkIfAndroid();
    this.initializeBridge();
  }

  checkIfAndroid() {
    const hasAndroidObject = typeof window.Android !== "undefined";
    const hasIsAndroidApp =
      hasAndroidObject && typeof window.Android.isAndroidApp === "function";
    const isAndroidResult = hasIsAndroidApp
      ? window.Android.isAndroidApp()
      : false;

    console.log("Android Detection:", {
      hasAndroidObject,
      hasIsAndroidApp,
      isAndroidResult,
      userAgent: navigator.userAgent,
    });

    return hasAndroidObject && hasIsAndroidApp && isAndroidResult;
  }

  initializeBridge() {
    if (this.isAndroid) {
      console.log("Android WebView detected - Native features available");
      this.logAvailableAndroidMethods();
    } else {
      console.log("Running in browser - Using web fallbacks");
    }
  }

  logAvailableAndroidMethods() {
    if (typeof window.Android === "object") {
      const methods = Object.getOwnPropertyNames(window.Android);
      console.log("Available Android methods:", methods);

      // Check specific methods we need for WhatsApp sharing
      const requiredMethods = [
        "shareFile",
        "shareToWhatsApp",
        "shareToWhatsAppWithPhone",
        "downloadFile",
        "showToast",
        "isAndroidApp",
        "isWhatsAppInstalled",
      ];
      requiredMethods.forEach((method) => {
        const exists = typeof window.Android[method] === "function";
        console.log(`Android.${method}: ${exists ? "Available" : "Missing"}`);
      });
    }
  }

  // Check if WhatsApp is installed
  isWhatsAppInstalled() {
    if (
      this.isAndroid &&
      typeof window.Android.isWhatsAppInstalled === "function"
    ) {
      try {
        return window.Android.isWhatsAppInstalled();
      } catch (error) {
        console.error("Error checking WhatsApp installation:", error);
        return false;
      }
    }
    return false;
  }

  // Share directly to WhatsApp with phone number
  async shareToWhatsAppWithPhone(
    fileData,
    filename,
    phoneNumber,
    message = ""
  ) {
    console.log("shareToWhatsAppWithPhone called:", {
      filename,
      phoneNumber: phoneNumber ? `***${phoneNumber.slice(-4)}` : "none",
      message,
      dataType: typeof fileData,
      dataSize: fileData instanceof Blob ? fileData.size : "unknown",
    });

    try {
      if (!this.isAndroid) {
        throw new Error("WhatsApp sharing only available in Android app");
      }

      if (typeof window.Android.shareToWhatsAppWithPhone !== "function") {
        console.log(
          "shareToWhatsAppWithPhone not available, falling back to general share"
        );
        return this.shareToWhatsApp(fileData, filename, message);
      }

      const base64Data = await this.convertToBase64(fileData);
      console.log(
        "Base64 conversion completed for WhatsApp, length:",
        base64Data.length
      );

      const result = window.Android.shareToWhatsAppWithPhone(
        base64Data,
        filename,
        phoneNumber,
        message || `Quotation: ${filename}`
      );

      console.log("Android.shareToWhatsAppWithPhone result:", result);
      return result;
    } catch (error) {
      console.error("WhatsApp phone share failed:", error);
      throw error;
    }
  }

  // Share to WhatsApp (general)
  async shareToWhatsApp(fileData, filename, message = "") {
    console.log("shareToWhatsApp called:", {
      filename,
      message,
      dataType: typeof fileData,
      dataSize: fileData instanceof Blob ? fileData.size : "unknown",
    });

    try {
      if (!this.isAndroid) {
        throw new Error("WhatsApp sharing only available in Android app");
      }

      if (typeof window.Android.shareToWhatsApp !== "function") {
        console.log(
          "shareToWhatsApp not available, falling back to general file share"
        );
        return this.shareFile(fileData, filename, "application/pdf", message);
      }

      const base64Data = await this.convertToBase64(fileData);
      console.log(
        "Base64 conversion completed for WhatsApp, length:",
        base64Data.length
      );

      const result = window.Android.shareToWhatsApp(
        base64Data,
        filename,
        message || `Quotation: ${filename}`
      );

      console.log("Android.shareToWhatsApp result:", result);
      return result;
    } catch (error) {
      console.error("WhatsApp share failed:", error);
      throw error;
    }
  }

  // PDF Download Function with enhanced error handling
  async downloadPDF(pdfData, filename = "document.pdf") {
    console.log("downloadPDF called:", {
      isAndroid: this.isAndroid,
      filename,
      dataType: typeof pdfData,
      dataSize: pdfData instanceof Blob ? pdfData.size : "unknown",
    });

    try {
      if (this.isAndroid) {
        if (typeof window.Android.downloadFile !== "function") {
          throw new Error("Android.downloadFile method not available");
        }

        console.log("Using Android native download");
        const base64Data = await this.convertToBase64(pdfData);
        console.log("Base64 conversion completed, length:", base64Data.length);

        try {
          const result = window.Android.downloadFile(
            base64Data,
            filename,
            "application/pdf"
          );
          console.log("Android.downloadFile result:", result);
          return true;
        } catch (androidError) {
          console.error("Android.downloadFile failed:", androidError);
          throw androidError;
        }
      } else {
        console.log("Using browser fallback for download");
        return this.browserDownload(pdfData, filename, "application/pdf");
      }
    } catch (error) {
      console.error("Download failed:", error);
      return false;
    }
  }

  // Enhanced Share file with WhatsApp priority
  async shareFile(fileData, filename, mimeType, title = "Shared file") {
    console.log("shareFile called:", {
      isAndroid: this.isAndroid,
      filename,
      mimeType,
      title,
      dataType: typeof fileData,
      dataSize: fileData instanceof Blob ? fileData.size : "unknown",
    });

    try {
      if (this.isAndroid) {
        if (typeof window.Android.shareFile !== "function") {
          console.error("Android.shareFile method not available");
          throw new Error("Android.shareFile method not available");
        }

        console.log("Converting file data to base64...");
        const base64Data = await this.convertToBase64(fileData);
        console.log("Base64 conversion completed, length:", base64Data.length);

        try {
          console.log("Calling Android.shareFile with params:", {
            filename,
            mimeType,
            title,
            base64Length: base64Data.length,
          });

          const result = window.Android.shareFile(
            base64Data,
            filename,
            mimeType,
            title
          );
          console.log("Android.shareFile result:", result);
          return true;
        } catch (androidError) {
          console.error("Android.shareFile failed:", androidError);
          throw androidError;
        }
      } else {
        console.log("Using browser fallback for sharing");
        if (navigator.share && navigator.canShare) {
          const file = new File([fileData], filename, { type: mimeType });
          if (navigator.canShare({ files: [file] })) {
            await navigator.share({
              title: title,
              files: [file],
            });
            return true;
          }
        }
        return this.browserDownload(fileData, filename, mimeType);
      }
    } catch (error) {
      console.error("Share failed:", error);
      return false;
    }
  }

  // Enhanced base64 conversion with better error handling
  async convertToBase64(data) {
    console.log("Converting to base64:", {
      dataType: typeof data,
      isBlob: data instanceof Blob,
      isArrayBuffer: data instanceof ArrayBuffer,
      isString: typeof data === "string",
    });

    try {
      if (typeof data === "string" && data.startsWith("data:")) {
        console.log("Data is already base64");
        return data;
      }

      if (data instanceof Blob) {
        console.log("Converting Blob to base64, size:", data.size);
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => {
            console.log(
              "FileReader completed, result length:",
              reader.result.length
            );
            resolve(reader.result);
          };
          reader.onerror = (error) => {
            console.error("FileReader error:", error);
            reject(error);
          };
          reader.readAsDataURL(data);
        });
      }

      if (data instanceof ArrayBuffer) {
        console.log(
          "Converting ArrayBuffer to base64, byteLength:",
          data.byteLength
        );
        const blob = new Blob([data]);
        return this.convertToBase64(blob);
      }

      if (typeof data === "string") {
        console.log("Converting string to base64, length:", data.length);
        return `data:application/octet-stream;base64,${btoa(data)}`;
      }

      throw new Error(
        "Unsupported data type for base64 conversion: " + typeof data
      );
    } catch (error) {
      console.error("Base64 conversion failed:", error);
      throw error;
    }
  }

  // Browser download fallback
  browserDownload(data, filename, mimeType) {
    console.log("Browser download:", {
      filename,
      mimeType,
      dataType: typeof data,
    });

    try {
      const blob =
        data instanceof Blob ? data : new Blob([data], { type: mimeType });
      console.log("Created blob, size:", blob.size);

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      console.log("Browser download completed");
      return true;
    } catch (error) {
      console.error("Browser download failed:", error);
      return false;
    }
  }

  // Enhanced message showing with fallback
  showMessage(message) {
    console.log("showMessage called:", { message, isAndroid: this.isAndroid });

    if (this.isAndroid) {
      try {
        if (typeof window.Android.showToast === "function") {
          window.Android.showToast(message);
          console.log("Android toast shown");
        } else {
          console.warn("Android.showToast not available, using fallback");
          this.browserShowMessage(message);
        }
      } catch (error) {
        console.error("Android.showToast failed:", error);
        this.browserShowMessage(message);
      }
    } else {
      this.browserShowMessage(message);
    }
  }

  browserShowMessage(message) {
    console.log("Browser message:", message);
    alert(message);
  }

  // Test method to verify Android bridge functionality
  testAndroidBridge() {
    console.log("Testing Android Bridge...");

    if (!this.isAndroid) {
      console.log("Not running in Android, skipping bridge test");
      return false;
    }

    const tests = [
      {
        name: "showToast",
        test: () => {
          if (typeof window.Android.showToast === "function") {
            window.Android.showToast("Bridge test message");
            return true;
          }
          return false;
        },
      },
      {
        name: "isAndroidApp",
        test: () => {
          if (typeof window.Android.isAndroidApp === "function") {
            return window.Android.isAndroidApp();
          }
          return false;
        },
      },
      {
        name: "isWhatsAppInstalled",
        test: () => {
          if (typeof window.Android.isWhatsAppInstalled === "function") {
            return window.Android.isWhatsAppInstalled();
          }
          return false;
        },
      },
    ];

    const results = tests.map((test) => {
      try {
        const result = test.test();
        console.log(`Test ${test.name}: ${result ? "PASS" : "FAIL"}`);
        return { name: test.name, result, error: null };
      } catch (error) {
        console.error(`Test ${test.name}: ERROR`, error);
        return { name: test.name, result: false, error: error.message };
      }
    });

    return results;
  }
}

const Preview = () => {
  const [quotation, setQuotation] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const navigate = useNavigate();
  const [pdfBlob, setPdfBlob] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [pdfError, setPdfError] = useState(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const location = useLocation();
  const { id } = useParams();
  const pdfGeneratedRef = useRef(false);

  // Initialize Android Bridge
  const androidBridge = useRef(new AndroidBridge());

  // Scroll to top function
  const scrollToTop = useCallback(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
  }, []);

  // Scroll to top on component mount and route changes
  useEffect(() => {
    scrollToTop();
  }, [scrollToTop, id]);

  const getQuotationId = () => {
    if (id) return id;
    if (location.state?.quotationId) {
      localStorage.setItem("quotationId", location.state.quotationId);
      return location.state.quotationId;
    }
    return localStorage.getItem("quotationId");
  };

  const quotationId = getQuotationId();
  console.log("preview qid", quotationId);

  const handleGeneratePDF = useCallback(
    async (finalQuotationId) => {
      if (isGeneratingPdf) {
        console.log("PDF generation already in progress");
        return null;
      }

      if (!quotation?.cards?.length || !quotation?.customer) {
        console.error("Cannot generate PDF: Missing quotation data", {
          hasCards: !!quotation?.cards?.length,
          hasCustomer: !!quotation?.customer,
        });
        setPdfError("Cannot generate PDF: Missing quotation data");
        return null;
      }

      try {
        setIsGeneratingPdf(true);
        setPdfError(null);

        const cleanQuotationId = finalQuotationId.replace("WIP_", "");
        console.log("Sending PDF request for quotationId:", cleanQuotationId);

        const payload = {
          tableData: quotation.cards.map((card) => ({
            card_id: card.card_id,
            type: card.type,
            size: card.size,
            items: card.items.map((item) => ({
              article: item.article,
              cat1: item.cat1,
              cat2: item.cat2,
              cat3: item.cat3,
              final_price: item.final_price,
              quantity: item.quantity,
              mc_name: item.mc_name,
              image_url: item.image_url,
            })),
          })),
          customer: {
            customer_id: quotation.customer.customer_id,
            name: quotation.customer.name,
            project_name: quotation.customer.project_name,
          },
        };

        console.log("PDF payload size:", JSON.stringify(payload).length);

        const response = await axiosInstance.post(
          `/download_pdf/${cleanQuotationId}`,
          payload,
          {
            responseType: "blob",
            timeout: 30000,
          }
        );

        console.log("PDF API response received, size:", response.data?.size);
        if (!response.data || response.data.size === 0) {
          throw new Error("Received empty PDF from server");
        }

        const blob = new Blob([response.data], { type: "application/pdf" });
        console.log("PDF Blob created, size:", blob.size);

        setPdfBlob(blob);

        if (pdfUrl) {
          try {
            window.URL.revokeObjectURL(pdfUrl);
            console.log("Previous PDF URL revoked");
          } catch (err) {
            console.warn("Failed to revoke previous URL:", err);
          }
        }

        const url = window.URL.createObjectURL(blob);
        console.log("PDF URL created:", url);
        setPdfUrl(url);
        setPdfError(null);

        scrollToTop();

        return url;
      } catch (error) {
        console.error("Error in PDF generation:", error);
        setPdfError(`Error generating PDF: ${error.message}`);
        return null;
      } finally {
        setIsGeneratingPdf(false);
      }
    },
    [pdfUrl, isGeneratingPdf, quotation, scrollToTop]
  );

  useEffect(() => {
    if (!quotationId) {
      setError("No quotation ID found");
      setIsLoading(false);
      return;
    }

    const fetchQuotation = async () => {
      try {
        let response;
        if (quotationId.startsWith("WIP_")) {
          response = await axiosInstance.get(
            `/preview_quotation/${quotationId}`
          );
        } else {
          response = await axiosInstance.get(
            `/preview_final_quotation/${quotationId}`
          );
        }
        if (!response.data) throw new Error("No data received");
        console.log("Quotation data:", response.data);
        if (!response.data.cards?.length || !response.data.customer) {
          throw new Error("Invalid quotation data: Missing cards or customer");
        }
        setQuotation(response.data);
        scrollToTop();
      } catch (error) {
        setError(error.message || "Error fetching quotation");
        console.error("Error fetching quotation:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuotation();
  }, [quotationId, scrollToTop]);

  // Generate PDF automatically for all quotations
  useEffect(() => {
    if (
      quotation &&
      quotation.cards?.length &&
      quotation.customer &&
      !pdfGeneratedRef.current
    ) {
      pdfGeneratedRef.current = true;
      console.log("Triggering PDF generation for quotation:", quotationId);
      handleGeneratePDF(quotationId);
    }
  }, [quotation, quotationId, handleGeneratePDF]);

  const getMarginForItem = (mcName) => {
    if (!quotation?.margins || !mcName) return 0;
    const marginObj = quotation.margins.find(
      (margin) => margin.mc_name === mcName
    );
    return marginObj ? marginObj.margin : 0;
  };

  const calculateGrandTotal = () => {
    if (!quotation?.cards) return 0;
    return quotation.cards
      .reduce((total, card) => {
        const cardTotal = card.items.reduce((sum, item) => {
          return sum + parseFloat(item.final_price) * item.quantity;
        }, 0);
        return total + cardTotal;
      }, 0)
      .toFixed(2);
  };

  const handleSaveAndExit = useCallback(() => {
    navigate("/");
  }, [navigate]);

  const handleDownload = useCallback(async () => {
    try {
      setIsDownloading(true);

      let currentPdfBlob = pdfBlob;

      if (!pdfUrl || !currentPdfBlob) {
        console.log("PDF not available, generating PDF first...");
        await handleGeneratePDF(quotationId);
        if (!pdfBlob) {
          androidBridge.current.showMessage(
            "Failed to generate PDF. Please try again."
          );
          return;
        }
        currentPdfBlob = pdfBlob;
      }

      console.log("Starting download...");

      const filename = `quotation_${quotationId.replace("WIP_", "")}.pdf`;
      const success = await androidBridge.current.downloadPDF(
        currentPdfBlob,
        filename
      );

      if (success) {
        androidBridge.current.showMessage("PDF downloaded successfully!");
        console.log("PDF download completed successfully");
      } else {
        androidBridge.current.showMessage("Download failed. Please try again.");
      }
    } catch (err) {
      console.error("Download failed:", err);
      androidBridge.current.showMessage("Download failed. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  }, [pdfUrl, pdfBlob, quotationId, handleGeneratePDF]);

  const handleConfirmAction = useCallback(async () => {
    if (!quotation) return;

    try {
      setIsLoading(true);
      const finalQuotationId = quotationId.replace("WIP_", "");
      const wipQuotation = {
        quotation_id: finalQuotationId,
        card_ids: quotation.cards.map((card) => card.card_id),
        margin_ids: quotation.margins.map((margin) => margin.margin_id),
        customer_id: quotation.customer.customer_id,
      };

      const response = await axiosInstance.post(
        "/final_quotation",
        wipQuotation
      );
      const confirmedQuotationId =
        response.data.quotation_id || finalQuotationId;

      await axiosInstance.delete(`/delete_quotation/${quotationId}`);
      const quotationResponse = await axiosInstance.get(
        `/preview_final_quotation/${confirmedQuotationId}`
      );
      if (
        !quotationResponse.data.cards?.length ||
        !quotationResponse.data.customer
      ) {
        throw new Error("Invalid confirmed quotation data");
      }
      setQuotation(quotationResponse.data);

      pdfGeneratedRef.current = false;
      setIsModalOpen(false);
      localStorage.setItem("quotationId", confirmedQuotationId);
      navigate(`/preview/${confirmedQuotationId}`, { replace: true });

      scrollToTop();
    } catch (error) {
      setError(error.message || "Error confirming quotation");
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  }, [quotation, quotationId, navigate, scrollToTop]);

  const handleEdit = useCallback(async () => {
    if (!quotation) return;
    const payload = {
      customer_id: quotation.customer.customer_id,
      card_ids: quotation.cards.map((card) => card.card_id),
      margin_ids: quotation.margins.map((margin) => margin.margin_id),
    };
    const response = await editFinalQuotation(payload);
    navigate("/home", { state: { quotationId: response.data.quotation_id } });
    localStorage.setItem("quotationId", response.data.quotation_id);
  }, [navigate, quotation]);

  // Enhanced WhatsApp share function
  const handleShare = useCallback(async () => {
    console.log("=== handleShare started ===");
    console.log("Initial state:", {
      quotationId,
      hasQuotation: !!quotation,
      hasPdfBlob: !!pdfBlob,
      isAndroid: androidBridge.current.isAndroid,
      isWhatsAppInstalled: androidBridge.current.isWhatsAppInstalled(),
    });

    try {
      setIsSharing(true);

      // Test Android bridge first if on Android
      if (androidBridge.current.isAndroid) {
        console.log("Testing Android bridge functionality...");
        const testResults = androidBridge.current.testAndroidBridge();
        console.log("Bridge test results:", testResults);
      }

      // Generate PDF if not available
      let currentPdfBlob = pdfBlob;

      if (!quotationId || !quotation || !currentPdfBlob) {
        console.log("PDF not available, generating PDF first...", {
          hasQuotationId: !!quotationId,
          hasQuotation: !!quotation,
          hasPdfBlob: !!currentPdfBlob,
        });

        const pdfUrl = await handleGeneratePDF(quotationId);
        if (!pdfUrl || !pdfBlob) {
          console.error("PDF generation failed");
          androidBridge.current.showMessage(
            "Failed to generate PDF. Please try again."
          );
          return;
        }
        currentPdfBlob = pdfBlob;
        console.log(
          "PDF generated successfully, blob size:",
          currentPdfBlob.size
        );
      }

      const filename = `quotation_${quotationId.replace("WIP_", "")}.pdf`;
      const customerName = quotation.customer.name;
      const shareMessage = `Quotation for ${customerName} - ${filename}`;

      console.log("Share parameters:", {
        filename,
        customerName,
        shareMessage,
      });

      // Try Android native WhatsApp sharing first
      if (androidBridge.current.isAndroid) {
        console.log("Attempting Android WhatsApp share...");

        // Check if customer has WhatsApp number
        const customerPhone =
          quotation.customer.whatsapp_number || quotation.customer.phone_number;

        if (customerPhone) {
          const cleanPhone = customerPhone.replace(/\D/g, "");
          console.log("Customer phone found, attempting direct WhatsApp share");

          if (cleanPhone.length >= 10) {
            try {
              const success =
                await androidBridge.current.shareToWhatsAppWithPhone(
                  currentPdfBlob,
                  filename,
                  cleanPhone,
                  shareMessage
                );

              if (success) {
                androidBridge.current.showMessage(
                  "Quotation shared to WhatsApp successfully!"
                );
                console.log("WhatsApp direct share successful");
                return;
              }
            } catch (whatsappError) {
              console.warn(
                "Direct WhatsApp share failed, trying general WhatsApp share:",
                whatsappError
              );
            }
          }
        }

        // Fallback to general WhatsApp share
        try {
          console.log("Attempting general WhatsApp share...");
          const success = await androidBridge.current.shareToWhatsApp(
            currentPdfBlob,
            filename,
            shareMessage
          );

          if (success) {
            androidBridge.current.showMessage(
              "Quotation shared to WhatsApp successfully!"
            );
            console.log("WhatsApp general share successful");
            return;
          }
        } catch (whatsappError) {
          console.warn(
            "General WhatsApp share failed, trying system share:",
            whatsappError
          );
        }

        // Fallback to system share dialog
        try {
          console.log("Attempting system share dialog...");
          const success = await androidBridge.current.shareFile(
            currentPdfBlob,
            filename,
            "application/pdf",
            shareMessage
          );

          if (success) {
            androidBridge.current.showMessage("Quotation shared successfully!");
            console.log("System share successful");
            return;
          }
        } catch (systemShareError) {
          console.error("System share failed:", systemShareError);
        }
      }

      // Browser/Web fallback - try Web Share API or download
      console.log("Attempting web fallback...");

      if (navigator.share && navigator.canShare) {
        try {
          const file = new File([currentPdfBlob], filename, {
            type: "application/pdf",
          });
          if (navigator.canShare({ files: [file] })) {
            await navigator.share({
              title: shareMessage,
              files: [file],
            });
            androidBridge.current.showMessage("Quotation shared successfully!");
            return;
          }
        } catch (webShareError) {
          console.warn("Web Share API failed:", webShareError);
        }
      }

      // Final fallback - download the file
      console.log("All sharing methods failed, falling back to download");
      const success = androidBridge.current.browserDownload(
        currentPdfBlob,
        filename,
        "application/pdf"
      );

      if (success) {
        androidBridge.current.showMessage(
          "Quotation downloaded. You can manually share the downloaded file."
        );
      } else {
        throw new Error("All sharing methods failed");
      }
    } catch (error) {
      console.error("=== handleShare failed ===");
      console.error("Error sharing quotation:", error);

      let errorMessage = "Failed to share the quotation. ";

      if (error.message.includes("WhatsApp sharing only available")) {
        errorMessage +=
          "WhatsApp sharing is only available in the Android app.";
      } else if (error.message.includes("timeout")) {
        errorMessage +=
          "The operation timed out. Please check your internet connection.";
      } else if (error.message.includes("PDF generation")) {
        errorMessage += "Failed to generate PDF. Please try again.";
      } else {
        errorMessage += error.message;
      }

      androidBridge.current.showMessage(errorMessage);
      console.error("Final error message:", errorMessage);
    } finally {
      setIsSharing(false);
      console.log("=== handleShare cleanup completed ===");
    }
  }, [quotationId, quotation, pdfBlob, handleGeneratePDF]);

  // Add Android-specific UI indicator
  useEffect(() => {
    if (androidBridge.current.isAndroid) {
      document.body.classList.add("android-app");
      console.log(
        "Running in Android WebView - Enhanced WhatsApp features available"
      );
    }
  }, []);

  if (isLoading) {
    return (
      <div className="p-4 sm:p-6 text-gray-600 flex justify-center items-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-4 sm:p-6 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-4 sm:p-6 mx-auto bg-gray-100 min-h-screen">
      {/* Show PDF error if exists */}
      {pdfError && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <p className="font-semibold">PDF Error:</p>
          <p>{pdfError}</p>
          <button
            onClick={() => {
              setPdfError(null);
              handleGeneratePDF(quotationId);
            }}
            className="mt-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry PDF Generation
          </button>
        </div>
      )}

      <div className="mb-6 bg-white p-4 sm:p-6 rounded-lg shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold mb-6 text-orange-600 border-b pb-3">
          Quotation Preview
        </h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div className="bg-orange-50 p-4 rounded-lg border border-orange-100">
            <p className="text-sm text-orange-700 mb-1">Quotation ID</p>
            <p className="font-semibold text-gray-800">
              {quotation?.quotation_id || "N/A"}
            </p>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg border border-orange-100">
            <p className="text-sm text-orange-700 mb-1">Customer</p>
            <p className="font-semibold text-gray-800">
              {quotation?.customer?.name || "N/A"}
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6 mb-8">
        {quotation?.cards?.length > 0 ? (
          quotation.cards.map((card, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
            >
              <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                <h3 className="font-medium text-gray-700">
                  {card.type || "No Type"}{" "}
                  {card.size && (
                    <span className="text-sm font-normal text-gray-500 ml-2">
                      Size: {card.size}
                    </span>
                  )}
                </h3>
              </div>
              <div className="p-4">
                {card.items?.length > 0 ? (
                  card.items.map((item, itemIndex) => (
                    <div key={itemIndex} className="mb-4 last:mb-0">
                      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
                        <div className="flex-grow mb-4 sm:mb-0">
                          <h4 className="font-semibold text-lg text-gray-800">
                            {item.article}
                            {item.cat1 && ` - ${item.cat1}`}
                            {item.cat2 && `, ${item.cat2}`}
                            {item.cat3 && `, ${item.cat3}`}
                          </h4>
                        </div>
                        <div className="w-full sm:w-auto">
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <div className="space-y-2">
                              <div className="flex justify-between text-sm text-gray-600">
                                <span>Unit Price:</span>
                                <span>
                                  ₹{parseFloat(item.final_price).toFixed(2)}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm text-gray-600">
                                <span>Quantity:</span>
                                <span>{item.quantity}</span>
                              </div>
                              <div className="flex justify-between text-sm text-gray-600">
                                <span>Margin:</span>
                                <span>{getMarginForItem(item.mc_name)}%</span>
                              </div>
                              <div className="border-t border-gray-300 pt-2 mt-2">
                                <div className="flex justify-between font-bold text-orange-600">
                                  <span>Total:</span>
                                  <span>
                                    ₹
                                    {(item.final_price * item.quantity).toFixed(
                                      2
                                    )}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No items in this card.
                  </p>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <p className="text-gray-500">No quotation data available</p>
          </div>
        )}
      </div>

      {quotation?.cards?.length > 0 && (
        <div className="bg-white p-4 sm:p-6 border-t border-gray-200 shadow-sm mt-6 m-0">
          <div className="max-w-full mx-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-700">
                Grand Total
              </h3>
              <p className="text-xl font-bold text-orange-600">
                ₹{calculateGrandTotal()}
              </p>
            </div>
            {!quotationId.startsWith("WIP_") ? (
              <div className="mt-4 flex gap-2 justify-center">
                <button
                  onClick={handleDownload}
                  disabled={isDownloading || isGeneratingPdf}
                  className="px-3 py-1 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors inline-flex items-center justify-center text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isDownloading || isGeneratingPdf ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-1"></div>
                      {isGeneratingPdf ? "Generating..." : "Downloading..."}
                    </>
                  ) : (
                    <>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                        />
                      </svg>
                      Download
                    </>
                  )}
                </button>
                <button
                  onClick={handleEdit}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors inline-flex items-center justify-center"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  Edit
                </button>
                <button
                  onClick={handleShare}
                  disabled={isSharing || isGeneratingPdf}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors inline-flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSharing || isGeneratingPdf ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                  ) : (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5 mr-2"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.68 3 3 0 00-5.367 2.68zm0 9.316a3 3 0 105.368 2.68 3 3 0 00-5.368-2.68z"
                      />
                    </svg>
                  )}
                  {isSharing
                    ? isGeneratingPdf
                      ? "Generating..."
                      : "Sharing..."
                    : "Share"}
                </button>
              </div>
            ) : (
              <div className="flex flex-row sm:gap-4 gap-1 justify-end">
                <button
                  onClick={handleSaveAndExit}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors shadow-sm font-medium w-full"
                >
                  Save and Exit
                </button>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="px-6 py-3 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors shadow-sm font-medium w-full"
                >
                  Confirm
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      <ConfirmationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleConfirmAction}
      />
    </div>
  );
};

export default Preview;
