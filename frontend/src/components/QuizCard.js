import React from "react";

function QuizCard({ question,choices, onAnswer }) {
  if (!question || !choices.length){
    return <p>Loading question...</p>
  }
  return (
    <div className="question-card">
      <h3>{question}</h3>
      <ul>
        {choices.map((answer,index) => (
          <li key={index}>
            <button onClick={()=>onAnswer(answer)}>
              {answer}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default QuizCard;