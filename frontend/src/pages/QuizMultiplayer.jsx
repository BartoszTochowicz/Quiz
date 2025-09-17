import { use, useContext, useEffect, useState } from "react";
import socketService from "../utils/socketService";
import AuthContext from "../utils/authProvider";
import QuizCard from "../components/QuizCard"
import { toast } from "react-toastify";
import { useParams } from "react-router-dom";

function QuizMultiplayer(){
    const {lobbyId} = useParams();
    const [question, setQuestion] = useState(""); 
    const [questionIndex, setQuestionIndex] = useState(0);
    const [choices,setChoices] = useState([]);
    const category = localStorage.getItem('category');

    const {username} = useContext(AuthContext);
    const {isAuthenticated,authToken,triggerAuthCheck} = useContext(AuthContext);
    

    useEffect(() => {
        socketService.updateCallbacks({
            onQuizStarted: (data) => {
                console.log("Quiz started: ",data);
                setQuestionIndex(0);
                setQuestion(data.quiz_data.questions[0].question);
                setChoices(data.quiz_data.questions[0].choices);
            },
            onNextQuestion: (data)=> {
                setQuestionIndex(data.question_index);
                setQuestion(data.question);
                setChoices(data.choices);
                console.log("Next question data:", data);
            },
            onAnswerSubmited: (data)=> {
                console.log('Answer submited, ',data);
                toast.success(`${data.username} answered. Score: ${data.score}`);
            },
            onQuizEnded: (data) => {
                toast.info('Quiz ended!');
                console.log("Final scores: ",data.scores);
            },
            onError: (data) => {
                toast.error(`❌ ${data.message}`)
            }
        })
    },[questionIndex]);

    useEffect(() =>{
        socketService.emit('next_question',{lobby_id:lobbyId, current_question_index:questionIndex});
    },[]);

    function handleAnswerSubmit(userAnswer){
        console.log("User answer:", userAnswer);
        socketService.emit('submit_answer',{
            username:username,
            lobby_id :lobbyId,
            answer: userAnswer
        });
    }


    return (
        <div>
            {(!question && !choices) && <p>Loading quiz. Please wait</p>}
            {(question && choices) && (
                <div className="Quiz_container">
                    <h2>{category} Quiz</h2>
                    <div className="quiz=questions">
                        <QuizCard
                            key={questionIndex}
                            question={question}
                            choices={choices}
                            onAnswer={handleAnswerSubmit}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}
export default QuizMultiplayer