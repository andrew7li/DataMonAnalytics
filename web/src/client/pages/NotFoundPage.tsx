import { Link } from "react-router";
import "./NotFoundPage.css";

export default function NotFoundPage() {
  return (
    <div className="not-found-page">
      <h1>404</h1>
      <p>This page doesn't exist.</p>
      <Link to="/" className="not-found-link">
        Back home
      </Link>
    </div>
  );
}
