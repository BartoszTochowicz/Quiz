import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" style={{ color: "#fff", textDecoration: "none" }}>
        Quiz App
      </Link>
    </nav>
  );
}

export default Navbar;