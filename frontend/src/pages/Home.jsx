import React from "react";
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="container">
      <h1>Welcome to the Quiz App</h1>
      <div className="container-quiz">
        <Link to="/quiz/singleplayer">
          <button>Start Quiz - <b>Singleplayer</b></button>
        </Link>
      </div>
      {/* <div className="container-quiz">
        <Link to="/quiz/multyplayer">
          <button>Start Quiz - <b>Multyplayer</b></button>
        </Link> 
      </div> */}
    </div>
  );
}

export default Home;