import Logo from "../assets/logo2.png";
import PuranmalSons from "../assets/name3.png";

const Layout = () => {
  return (
    <div>
      {/* Header */}
      <header className="w-full shadow-sm">
        <nav className="flex items-center justify-between px-6 py-4">
          {/* Logo and Title Section */}
          <div className="flex items-center space-x-4">
            <a
              href="https://pspla-pro.herokuapp.com"
              className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
            >
              <img src={Logo} alt="Puranmal Sons Logo" className="h-10 w-10" />
              <div className="flex flex-col">
                <img src={PuranmalSons} alt="Puranmal Sons" className="h-5" />
              </div>
            </a>
          </div>

          {/* Right Side - Home Button */}
          <div className="flex items-center">
            <a
              href="https://pspla-pro.herokuapp.com"
              className="flex items-center bg-gray-100 text-gray-400 p-2 rounded-lg"
            >
              <svg
                width={18}
                height={18}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9,22 9,12 15,12 15,22" />
              </svg>
              <span className="hidden sm:inline">Home</span>
            </a>
          </div>
        </nav>
      </header>
    </div>
  );
};

export default Layout;
