import { data } from "react-router-dom";
import { io } from 'socket.io-client';


const URL = "http://localhost:5000"; 

class SocketService {
    constructor(){
        this.socket = null;
        this.isConnected = false;
        this.authToken = null;
        this.callbacks = {
            onConnect : null,
            onDisconnect : null,
            onRefresh : null,
            onFooEvent : null,
            onLobbiesListed: null,//
            onLobbyCreated : null,//
            onLobbyDeleted : null,//
            onPlayerJoined : null,//
            onPlayerLeft : null,//
            onLobbyDetails : null,//
            onLobbyUpdated : null,//
            onAuthFail : null,
            onQuizStarted : null,
            onNextQuestion : null,
            onAnswerSubmited : null,
            onQuizEnded : null,
            onError : null
        };
        console.log("SocketService constructor called");
        this.reconnectCounter = 0;        
        this.messageQueue = []; // Add message queue
        this.isProcessingQueue = false;
    }

    initialize(callbacks = {}){
        this.callbacks = {...this.callbacks,...callbacks};
    }
    connect(authToken) {
        console.log("authToken = ",authToken);
        if(this.socket && this.socket.connected){
            console.log("Socket already connected");
            return;
        }
        this.authToken = authToken;

        this.socket = io(URL, {
            // transports: ["websocket"],
            autoConnect: false,
            extraHeaders: {
                "Authorization": `Bearer ${authToken}`
            },
            auth:{
                token: authToken
            }
            // query: {token: authToken}
        });
        this.setupEventListeners();
        this.socket.connect();
        return this.socket;
    }
    setupEventListeners(){
        if (!this.socket) return;

        this.socket.on('connect',() => {
            console.log("Socket connected");
            this.isConnected = true;

            this.processMessageQueue();

            if(this.callbacks.onConnect){
                this.callbacks.onConnect();
            }
        });

        this.socket.on('disconnect', () => {
            console.log('Socket disconnected');
            this.isConnected = false;
            
            if(this.reconnectCounter < 10){
                setTimeout(() => {
                    console.log("Reconnecting...");
                    this.socket.connect();
                },5000);
            }else {
                console.error("Max reconnet attempts reached. Disconnecting socket");
                this.disconnect();
            }
            if(this.callbacks.onDisconnect){
                this.callbacks.onDisconnect();
            }
        });

        this.socket.on('connect_error', async (error) => {
            console.log("Connection error: ",error)

            if(error.message === 'auth_fail'){
                console.error("Authentication failed. Refreshing token.");
                try{
                    const newToken = await refreshAuthToken();
                    this.reconnect(newToken);
                } catch(error){
                    console.error("Failed to refresh token:",error);
                    if(this.callbacks.onAuthFail){
                        this.callbacks.onAuthFail();
                    }
                }
         
            }else{
                console.log("Unknow connection error:",error);
            }
            if(this.callbacks.onRefresh){
                this.callbacks.onRefresh();
            }
        });

        // Application events
        this.socket.on('foo',(value) => {
            if(this.callbacks.onFooEvent){
                this.callbacks.onFooEvent(value);
            }
        });

        this.socket.on('lobbies_listed', (data)=>{
            console.log('Lobbies loaded');

            if(this.callbacks.onLobbiesListed){
                this.callbacks.onLobbiesListed(data)
            }
        })

        this.socket.on('lobby_created', (data) => {
            console.log("Lobby created:",data);
            
            if(this.callbacks.onLobbyCreated){
                this.callbacks.onLobbyCreated(data);
            }
        });

        this.socket.on('lobby_deleted', (data) => {
            console.log("Lobby deleted:",data);

            if(this.callbacks.onLobbyDeleted){
                this.callbacks.onLobbyDeleted(data);
            }
        });

        this.socket.on('player_joined', (data) => {
            console.log("Player joined:",data);

            if(this.callbacks.onPlayerJoined){
                this.callbacks.onPlayerJoined(data);
            }
        });

        this.socket.on('player_left',(data) => {
            console.log("Player left:",data);

            if(this.callbacks.onPlayerLeft){
                this.callbacks.onPlayerLeft(data);
            }
        });

        this.socket.on('lobby_details', (data) => {
            console.log("Lobby details received:",data);
            if(this.callbacks.onLobbyDetails){
                this.callbacks.onLobbyDetails(data);
            }
        })

        this.socket.on('lobby_updated', (data) =>{
            console.log("Updated lobby users: ",data)

            if(this.callbacks.onLobbyUpdated){
                this.callbacks.onLobbyUpdated(data);
            }
        })

        this.socket.on('quiz_started', (data) => {
            console.log('Quiz started:',data);

            if(this.callbacks.onQuizStarted){
                this.callbacks.onQuizStarted(data);
            }
        });

        this.socket.on('answer_submited', (data) => {
            console.log('Answer submited:',data);

            if(this.callbacks.onSubmitAnswer){
                this.callbacks.onSubmitAnswer(data);
            }
        });

        this.socket.on('next_question', (data) => {
            console.log('Next question:',data);

            if(this.callbacks.onNextQuestion){
                this.callbacks.onNextQuestion(data);
            }
        });

        this.socket.on("end_quiz", (data) => {
            console.log('Quiz ended:',data);

            if(this.callbacks.onQuizEnded){
                this.callbacks.onQuizEnded(data);
            }
        });
        
        this.socket.on("error",(data) => {
            console.log('Error occurred', data);

            if(this.callbacks.onError){
                this.callbacks.onError(data);
            }
        })
    }
    // Process queued messages when connection is established
    processMessageQueue() {
        if(this.isProcessingQueue && !this.isConnected) return;

        this.isProcessingQueue = true;

        while(this.messageQueue.length > 0){
            const {event, data, resolve, reject} = this.messageQueue.shift();
            if(!this.socket){
                reject(new Error("Socket is null. Cannot emit: " + event));
                continue;
            }
            try{
                this.socket.emit(event,data, (response)=>{
                    if(response && response.error){
                        reject(new Error(response.error));
                    }else{
                        resolve(response);
                    }
                });
            }catch(error){
                reject(error);
            }
        }
        this.isProcessingQueue = false;
    }

    // Method to emit events with waiting and timeout
    emit(event, data, waitForConnection = true, timeoutMs = 20000){
        return new Promise((resolve, reject) => {

            if(this.socket && this.socket.connected) {
                try {
                    this.socket.emit(event,data,(response) => {
                        if(response && response.error){
                            reject(new Error(response.error));
                        }else{
                            resolve(response);
                        }
                    });
                }catch(error){
                    reject(error);
                }
                return;
            }
            // If not waiting for connection, reject immediately
            if(!waitForConnection){
                reject(new Error("Socket not connected. Cannot emit: "+event));
                return;
            }

            const timeoutId = setTimeout(() => {
                // Remove from queue if timeout occurs
                const index = this.messageQueue.findIndex(
                    (item) => item.event === event && item.data === data
                );
                if(index !== -1){
                    this.messageQueue.splice(index,1);
                }
                reject(new Error(`Timeout waiting for connection to emit: ${event}`));
            },timeoutMs);

            // Add to queue
            this.messageQueue.push({
                event,
                data,
                resolve: (response) => {
                    clearTimeout(timeoutId);
                    resolve(response);
                },
                reject: (error) => {
                    clearTimeout(timeoutId);
                    reject(error);
                }
            });
            console.log(`Queued message: ${event}. Waiting for connection...`);
            this.processMessageQueue();
        });
    }

    disconnect() {
        if(this.socket){
            this.messageQueue.forEach(({reject}) => {
                reject(new Error("Socket disconnected before message could be sent"));
            });
            this.messageQueue = [];

            if(this.callbacks.onDisconnect){
                this.callbacks.onDisconnect();
            }
            this.socket.removeAllListeners();
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
        this.authToken = null;
    }

    reconnect(newAuthToken) {
        if(this.reconnectCounter >= 10){
            console.error("Authorization refresh attemtps exceeded. Disconnecting socket.");
            this.disconnect();
            return;
        }
        this.disconnect();
        return this.connect(newAuthToken)
    }

    getConnectionStatus() {
        return this.isConnected;
    }

    getSocket(){
        return this.socket;
    }
    updateCallbacks(newCallbacks){
        this.callbacks = {...this.callbacks,...newCallbacks};
    }
}
const socketService = new SocketService();
export default socketService;