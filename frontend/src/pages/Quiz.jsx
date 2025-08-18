import React, { useState, useEffect, use } from "react";
import axios from "axios";
import QuestionCard from "../components/QuestionCard";
import QuizForm from "../components/QuizForm"
import { useNavigate } from "react-router-dom";

function Quiz() {
  const [quizData, setQuizData] = useState(null);
  const handleFormSubmit = async (params) => {
    try{
      const token = localStorage.getItem("token");
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
  return (
    <div>
      <QuizForm onSubmit={handleFormSubmit}/>
      {quizData && (
        <div>
          
        </div>
      )}
    </div>
  )
}
export default Quiz;