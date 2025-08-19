import React from "react";

function QuestionCard({ question, onAnswer }) {
  return (
    <div className="question-card">
      <h3>{question.question}</h3>
      <ul>
        {question.answers.map((answer,index) => (
          <li key={index}>
            <button onClick={()=>onAnswer(answer,question.token)}>
              {answer}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default QuestionCard;