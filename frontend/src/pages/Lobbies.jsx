import { useContext, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import socketService from "../utils/socketService";
import AuthContext from "../utils/authProvider";

function Lobbies() {
    const { isAuthenticated, authToken, triggerAuthCheck, username } = useContext(AuthContext);
    const socketInitialized = useRef(false);
    const navigation = useNavigate();
    const [lobbies, setLobbies] = useState([]);
    const [isJoining, setIsJoining] = useState(false);

    useEffect(() => {
        // Reset when auth status changes
        if (!isAuthenticated || !authToken) {
            socketInitialized.current = false;
            socketService.disconnect();
            return;
        }

        // Initialize socket only once after authentication
        if (socketInitialized.current) {
            console.log("Socket already initialized");
            return;
        }

        console.log("Initializing socket connection");
        socketInitialized.current = true;

        // Initialize socket service with callbacks
        socketService.initialize({
            onLobbiesListed: (data) => {
                console.log("Received lobby list:", data);
                setLobbies(data.lobbies);
            },
            onAuthFail: () => {
                setIsJoining(false);
                triggerAuthCheck();
            },
            onPlayerJoined: (data) => {
                console.log("Joined lobby successfully:", data);
                setIsJoining(true);
                socketService.emit('list_lobbies');
                navigation(`/lobby/${data.lobby_id}`);
            },
            onPlayerLeft: (data) => {
                console.log("Player left");
                socketService.emit('list_lobbies');
            },
            onLobbyDeleted: (data) => {
                const deletedId = data.lobby_id;
                setLobbies((prev) => prev.filter((lobby) => lobby.lobby_id !== deletedId));
                console.log("Lobby deleted",data);
            },
            onLobbyCreated: (data)=> {
                console.log('Lobby created, ',data.data);
                setLobbies((prev) => [...prev,data.data]);
            }
        });

        // Connect to socket server
        socketService.connect(authToken);

        // return () => {
        //     console.log("Cleaning up socket connection");
        //     // if (!isAuthenticated) {
        //     //     socketService.disconnect();
        //     //     socketInitialized.current = false;
        //     // }
        // };
    }, [isAuthenticated, authToken, triggerAuthCheck]);

    useEffect(() => {
        if(!socketService.getConnectionStatus()){
            socketService.reconnect(authToken);            
        }
    }, [authToken]);

    useEffect(() => {
        socketService.emit('list_lobbies');
    },[])

    const joinLobby = (lobbyId) => {
        console.log("Joining lobby:", lobbyId);
        socketService.emit('join_lobby', { "lobby_id": lobbyId, 'username': username })
            
            // } else {
            //     console.error("Failed to join lobby:", response.message);
            //     alert(`Failed to join lobby: ${response.message}`);
            // }
    };

    const jumpIntoLobbyCreator = (() => {
        console.log('Navigate to lobby creator');
        navigation(`/lobby/create`);
    });

    return (
        <div>
            <div>
                <header>
                    <h1>Lobbies</h1>
                </header>

                <main>
                    <div>
                        <h2>Choose lobby to join</h2>
                        <div>
                            {lobbies.length === 0 && <p>No lobbies available. Create one!</p>}
                            {lobbies.length > 0 ? (
                                <table>
                                    <thead>
                                        <tr>
                                            <th scope="col">Lobby Name</th>
                                            <th scope="col">Hostname</th>
                                            <th scope="col">Players</th>
                                            <th scope="col">Max Players</th>
                                            <th scope="col">Join</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {lobbies.map((lobby) => (
                                            <tr key={lobby.lobby_id}>
                                                <th scope="row">{lobby.lobby_name}</th>
                                                <th scope="row">{lobby.host_username}</th>
                                                <th scope="row">{lobby.current_players}</th>
                                                <th scope="row">{lobby.max_players}</th>
                                                <th scope="row"><button onClick={() => joinLobby(lobby.lobby_id)} disabled={isJoining}>Join Lobby</button></th>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                // <ul>
                                //     {lobbies.map((lobby) => (
                                //         <li key={lobby.lobby_id}>
                                //             <li>
                                                
                                //             </li>
                                //             <b>lobby.name</b>
                                //             - {lobby.players} player{lobby.current_players !== 1 ? 's' : ''} / {lobby.max_players}
                                //             <button onClick={() => joinLobby(lobby.lobby_id)} disabled={isJoining}>
                                //                 Join
                                //             </button>
                                //         </li>
                                //     ))}
                                // </ul>
                            ) : null}
                        </div>
                        {isJoining && <p>Joining lobby...</p>}
                    </div>
                    <h3>Do you want to create your own quiz?</h3>
                    <button onClick={jumpIntoLobbyCreator}>Create Lobby</button>
                </main>
            </div>
        </div>
    );
}

export default Lobbies;