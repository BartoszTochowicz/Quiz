import React from "react";
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="container">
      <h1>Welcome to the Quiz App</h1>
      <Link to="/quiz">
        <button>Start Quiz</button>
      </Link>
    </div>
  );
}

export default Home;