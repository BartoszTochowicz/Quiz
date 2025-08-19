import React, { useState, useEffect, use } from "react";
import axios from "axios";
import QuestionCard from "../components/QuestionCard";
import QuizForm from "../components/QuizForm"
import { useNavigate } from "react-router-dom";

function Quiz() {
  const [quizData, setQuizData] = useState(null);
  const handleFormSubmit = async (params) => {
    try{
      const token = localStorage.getItem("access_token");
      const resposne = await axios.get(
        "http://localhost:5000/api/v1/singleplayer/quiz/singleplayer",
        {
          params,
          headers: { Authorization:`Bearer ${token}`}
        }
      );
      setQuizData(resposne.data.data)
    }catch (error) {
    console.error("Error fetching quiz data:", error);
  }
  };
  function handleAnswerSubmit(userAnswer,questionToken) {
    const answerData ={
      token:questionToken,
      answer:userAnswer
    }
    axios.post("http://localhost:5000/api/v1/singleplayer/quiz/singleplayer/answer",answerData,{
      headers:{
        Authorization:`Bearer ${localStorage.getItem("access_token")}`
      }
    })
    }
  return (
    <div>
      {!quizData && <QuizForm onSubmit={handleFormSubmit}/>}
      {quizData && (
        <div className="Quiz-container">
          <h2>{quizData.category} Quiz</h2>
          <div className="quiz-questions">
            {quizData.questions.map((question,index) => (
              <QuestionCard
                key={question.question_id}
                question={question}
                onAnswer={handleAnswerSubmit}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
};
export default Quiz;