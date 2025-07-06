import React, { useState, useEffect } from "react";
import axios from "axios";
import QuestionCard from "../components/QuestionCard";
import { useNavigate } from "react-router-dom";

function Quiz() {
  const [questions, setQuestions] = useState([]);
  const [idx, setIdx] = useState(0);
  const [score, setScore] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get("/api/quiz/")
      .then(res => setQuestions(res.data))
      .catch(() => alert("Error loading questions"));
  }, []);

  function handleAnswer(ansKey) {
    const isCorrect = questions[idx].correct_answers[`${ansKey}_correct`] === "true";
    if (isCorrect) setScore(s => s + 1);
    if (idx + 1 < questions.length) {
      setIdx(i => i + 1);
    } else {
      navigate("/result", { state: { score, total: questions.length } });
    }
  }

  if (!questions.length) return <div>Loading...</div>;

  return (
    <div className="container">
      <QuestionCard
        question={questions[idx].question}
        answers={questions[idx].answers}
        onAnswer={handleAnswer}
      />
      <p>
        Question {idx + 1} of {questions.length}
      </p>
    </div>
  );
}

export default Quiz;