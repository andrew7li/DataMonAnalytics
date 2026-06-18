import { Link } from "react-router";
import logo from "../../assets/logo.svg";
import "./Navbar.css";

export default function Navbar() {
  return (
    <header className="navbar">
      <Link to="/" className="navbar-brand">
        <img src={logo} alt="" className="navbar-logo" />
        <span className="navbar-wordmark">DataMon</span>
      </Link>

      <div className="navbar-search">
        <svg
          className="navbar-search-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="7" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="search"
          placeholder="Search cards, sets, expansions..."
          aria-label="Search"
        />
      </div>

      <div className="navbar-trending">
        <Link to="/trending" className="navbar-trending-button">
          <svg
            className="navbar-trending-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
          <span>Trending</span>
        </Link>
      </div>
    </header>
  );
}
