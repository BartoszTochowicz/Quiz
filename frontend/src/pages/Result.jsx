import React, { useEffect,useRef } from "react";
import { useLocation, Link } from "react-router-dom";
import "../assets/styles/result.css";

function Result() {
  const location = useLocation();
  const result = localStorage.getItem("quiz_score");
  const score = result ? JSON.parse(result).score : 0;
  const total = result ? JSON.parse(result).total : 0;
  const category = result ? JSON.parse(result).category : "Unknown";
  const percent = total > 0 ? Math.round((score/total)*100) : 0;
  const barRef = useRef();
  console.log("Result data:", result);
  console.log("Score:", score, "Total:", total, "Category:", category);
  console.log("Percentage:", percent);

  useEffect(() =>{
    if (barRef.current){
      barRef.current.style.width = "0%";
      setTimeout(() => {
        barRef.current.style.width = `${percent}%`;
      },100);
    }
  },[percent])
  return (
    <div className="container">
      <h2>{category} Quiz Finished!</h2>
      <div className="progress-bar-bg">
        <div 
          className="progress-bar"
          ref={barRef}
          style={{width: "0%"}}
          ></div>
      </div>
      <p>
        You scored {score} out of {total} ({percent}%)
      </p>
      <Link to="/">Go Home</Link>
    </div>
  );
}

export default Result;