import React, { useState, useEffect, use } from "react";
import axios from "axios";
import QuestionCard from "../components/QuestionCard";
import QuizForm from "../components/QuizForm"
import { useNavigate } from "react-router-dom";

function Quiz() {
  const [quizData, setQuizData] = useState(null);
  const [questionIndex,setQuestionIndex] = useState(0);
  const navigate = useNavigate();
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
      setQuestionIndex(0)
    }catch (error) {
    console.error("Error fetching quiz data:", error);
  }
  };
  function handleAnswerSubmit(userAnswer,questionToken) {
    console.log("User answer:", userAnswer);
    console.log("Question token:", questionToken);
    const answerData ={
      token:questionToken,
      answer:userAnswer
    }
    axios.post("http://localhost:5000/api/v1/singleplayer/quiz/singleplayer/answer",answerData,{
      headers:{
        "Content-Type": "application/json",
        Authorization:`Bearer ${localStorage.getItem("access_token")}`
      }
    }).then(res =>{
      if(quizData && questionIndex>=quizData.questions.length-1){
        const quiz_id = quizData.quiz_id;

        const response = axios.get("http://localhost:5000/api/v1/singleplayer/quiz/singleplayer/score",{
          params:{quiz_id},
          headers:{
            Authorization:`Bearer ${localStorage.getItem("access_token")}`
          }
        }).then(res => {
          const score = res.data.score;
          const category = quizData.category;
          const total = res.data.total_questions;
          localStorage.setItem("quiz_score", JSON.stringify({ score, total, category }));
          navigate("/result");
        })
        // const score = response.score
        // const category = quizData.category;
        // const total = quizData.questions.length;
        // localStorage.setItem("quiz_score", JSON.stringify({ score, total, category }));
        // navigate("/result");
      }else{
        setQuestionIndex(questionIndex+1);
      }
    }).catch(error => {
      if (error.response?.data?.errorr == "Token"){
        console.error("Token expired, redirecting to login");
        setQuizData(null);
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
            <QuestionCard
              key={quizData.questions[questionIndex].question_id} 
              question={quizData.questions[questionIndex]}
              onAnswer={handleAnswerSubmit}
            />
          </div>
          <p>Question {questionIndex+1} of {quizData.questions.length}</p>
        </div>
      )}
    </div>
  )
};
export default Quiz;