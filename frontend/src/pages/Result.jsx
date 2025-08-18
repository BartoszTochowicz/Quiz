import React from "react";
import { useLocation, Link } from "react-router-dom";

function Result() {
  const location = useLocation();
  const { score = 0, total = 0 } = location.state || {};

  return (
    <div className="container">
      <h2>Quiz Finished!</h2>
      <p>
        You scored {score} out of {total}
      </p>
      <Link to="/">Go Home</Link>
    </div>
  );
}

export default Result;