import React from "react";
import { Link } from "react-router-dom";

interface HeaderProps {
  title?: string;
}

const Header: React.FC<HeaderProps> = ({ title = "DevGenius" }) => {
  return (
    <header className="bg-primary-700 text-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <svg
            className="w-8 h-8 text-primary-300"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"
              clipRule="evenodd"
            />
          </svg>
          <h1 className="text-2xl font-bold">{title}</h1>
        </div>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link to="/" className="hover:text-primary-300 transition-colors">
                Home
              </Link>
            </li>
            <li>
              <Link
                to="/about"
                className="hover:text-primary-300 transition-colors"
              >
                About
              </Link>
            </li>
            <li>
              <Link
                to="/dashboard"
                className="hover:text-primary-300 transition-colors"
              >
                Dashboard
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
