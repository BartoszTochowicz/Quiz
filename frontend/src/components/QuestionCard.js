import React from "react";

function QuestionCard({ question, answers, onAnswer }) {
  return (
    <div className="question-card">
      <h3 dangerouslySetInnerHTML={{ __html: question }} />
      <ul>
        {Object.entries(answers)
          .filter(([_, val]) => val)
          .map(([key, val]) => (
            <li key={key}>
              <button onClick={() => onAnswer(key)}>{val}</button>
            </li>
          ))}
      </ul>
    </div>
  );
}

export default QuestionCard;