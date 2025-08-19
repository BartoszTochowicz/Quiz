import { Form } from "react-router-dom";
import React, { useState } from "react";

function QuizForm({onSubmit}) {
    const [category,setCategory] = useState("9");
    const [amount,setAmount] = useState(1);
    const [difficulty, setDifficulty] = useState("easy");
    const [typeOfQuestions, setTypeOfQuestions] = useState("multiple");

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({ 
            category,
            amount,
            difficulty,
            type_of_questions:typeOfQuestions})
    };

    return (
        <form onSubmit={handleSubmit} className="quiz-form">
            <h2>Select Quiz Requirements</h2>
            <label>Select category</label>
            <select value={category} onChange={e => setCategory(e.target.value)}>
                <option value="9">General Knowledge</option>
                <option value="10">Entertainment: Books</option>
                <option value="11">Entertainment: Film</option>
                <option value="12">Entertainment: Music</option>
                <option value="13">Entertainment: Musicals & Theatres</option>
                <option value="14">Entertainment: Television</option>
                <option value="15">Entertainment: Video Games</option>
                <option value="16">Entertainment: Board Games</option>
                <option value="17">Science & Nature</option>
                <option value="18">Science: Computers</option>
                <option value="19">Science: Mathematics</option>
                <option value="20">Mythology</option>
                <option value="21">Sports</option>
                <option value="22">Geography</option>
                <option value="23">History</option>
                <option value="24">Politics</option>
                <option value="25">Art</option>
                <option value="26">Celebrities</option>
                <option value="27">Animals</option>
                <option value="28">Vehicles</option>
                <option value="29">Entertainment: Comics</option>
                <option value="30">Science: Gadgets</option>
                <option value="31">Entertainment: Japanese Anime & Manga</option>
                <option value="32">Entertainment: Cartoon & Animations</option>
            </select>
            <br/>
            <label>Number of questions</label>
            <input
                type="number"
                min={1} 
                max={50} 
                value={amount}
                onChange={e => setAmount(e.target.value)}
            />
            <br/>
            <label>Select difficulty</label>
            <select value={difficulty} onChange={e => setDifficulty(e.target.value)}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
            </select>
            <br/>
            <label>Type of questions</label>
            <select value={typeOfQuestions} onChange={e => setTypeOfQuestions(e.target.value)}>
                <option value="multiple">Multiple Choice</option>
                <option value="boolean">True/False</option>
            </select>
            <br/>
            <button type="submit">Start Quiz</button>
        </form>
    );
}
export default QuizForm