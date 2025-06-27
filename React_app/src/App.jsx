import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AddItem from "./components/AddItems";
import Home from "./pages/Home";
import FormPage from "./pages/FormPage";
import Preview from "./pages/Preview";
import Layout from "./components/Layout"; // Import your header component
import "./App.css";

function App() {
  return (
    <Router>
      {/* Header appears on all pages */}
      <Layout title="Quotation" homeUrl="/" />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<FormPage />} />
        <Route path="/additems" element={<AddItem />} />
        <Route path="/preview" element={<Preview />} />
        <Route path="/preview/:id" element={<Preview />} />
      </Routes>
    </Router>
  );
}

export default App;
