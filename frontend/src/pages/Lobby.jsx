
import { useState, useEffect, useContext} from "react";
import socketService from "../utils/socketService";
import { useParams } from "react-router-dom";
import AuthContext from "../utils/authProvider";

function Lobby() {
    const [players, setPlayers] = useState([]);
    const {lobbyId} = useParams();
    const {username} = useContext(AuthContext);
    const {hostUsername, setHostUsername} = useState("");
    const {maxPlayers, setMaxPlayers} = useState(0);
    const {currentPlayers, setCurrentPlayers} = useState(0);
    const {isAuthenticated, authToken, triggerAuthCheck} = useContext(AuthContext);
    const {lobbyName, setLobbyName} = useState("");
    useEffect(() => {
        socketService.emit('get_lobby_details', {lobby_id: lobbyId}, (response) => {
            console.log("Lobby details response:", response);
            if (response.status === 'ok'){
                setHostUsername(response.host_username);
                setPlayers(response.players);
                setMaxPlayers(response.max_players);
                setCurrentPlayers(response.current_players);
                setLobbyName(response.lobby_name);
            }else{
                alert("Failed to get lobby details");
                window.location.href = '/lobbies';
            }
        });

        socketService.updateCallbacks({
            onLobbyUsersUpdate: (updatedPlayers) => {
                setPlayers(updatedPlayers);
            },
            onLobbyDeleted: () => {
                alert("Lobby has been deleted");
                window.location.href = '/lobbies';
            },
            onQuizStarted: () => {
                alert("Quiz is starting!");
                window.location.href = `/quiz/${lobbyId}`;
            }
        });

        return () => {
            socketService.emit('leave_lobby', { lobby_id: lobbyId });
        };
    },[lobbyId]);

    const handleDeleteLobby = () => {
        socketService.emit('delete_lobby',{lobby_id : lobbyId});
    }

    const handleStartQuiz = () => {
        socketService.emit('start_quiz', {lobby_id : lobbyId});
    }
    return (
        <div>
            <h2>Lobby {lobbyName}</h2>
            <h2>Players in Lobby:</h2>
            <ul>
                <li>Host: <b>{hostUsername}</b> {hostUsername===username}</li>
                <li>Players: {currentPlayers} / {maxPlayers}</li>
            </ul>
            <ul>
                {players.map((player,index) => (
                    <li key={index}>{player}</li>
                ))}
            </ul>
                {username === hostUsername && (
                    <div>
                        <button onClick={handleDeleteLobby}>Delete Lobby</button>
                        <button on onClick={handleStartQuiz}>Start Quiz</button>
                    </div>
                )}
        </div>
    );
}
export default Lobby;