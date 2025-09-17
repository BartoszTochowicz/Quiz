import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import QuizSingleplayer from "./pages/QuizSingleplayer";
import Result from "./pages/Result";
import Login from "./pages/Login";
import { AuthProvider } from "./utils/authProvider";
import Account from "./pages/Account";
import Lobbies from "./pages/Lobbies";
import LobbyCreator from "./pages/LobbyCreator";
import Lobby from "./pages/Lobby";
import { ToastContainer } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <AuthProvider>
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/quiz/singleplayer" element={<QuizSingleplayer />} />
        <Route path="/lobby" element={<Lobbies/>}/>
        <Route path="/result" element={<Result />} />
        <Route path="/login" element={<Login />} />
        <Route path="/account" element={<Account/>}/>
        <Route path="/lobby/create" element={<LobbyCreator/>}/>
        <Route path="/lobby/:lobbyId" element={<Lobby/>}/>
      </Routes>
      <ToastContainer position="top-right" autoClose={3000} />
    </Router>
    </AuthProvider>
  );
}

export default App;