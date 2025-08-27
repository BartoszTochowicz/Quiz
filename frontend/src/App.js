import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import QuizSingleplayer from "./pages/QuizSingleplayer";
import Result from "./pages/Result";
import Login from "./pages/Login";
import { AuthProvider } from "./utils/authProvider";
import Account from "./pages/Account";


function App() {
  return (
    <AuthProvider>
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/quiz/singleplayer" element={<QuizSingleplayer />} />
        <Route path="/result" element={<Result />} />
        <Route path="/login" element={<Login />} />
        <Route path="/account" element={<Account/>}/>

      </Routes>
    </Router>
    </AuthProvider>
  );
}

export default App;