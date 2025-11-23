let socket = null;
let currentUsername = null;

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/chat`;

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        // Si viene un username desde Google Login, lo usamos como prioritario
        const desiredUsername =
            (typeof INITIAL_USERNAME !== "undefined" && INITIAL_USERNAME) ||
            prompt("Escribe tu nombre de usuario (deja vacío para uno automático):") ||
            "";

        currentUsername = desiredUsername.trim();

        socket.send(
            JSON.stringify({
                type: "join",
                username: currentUsername,
            })
        );
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleServerMessage(data);
    };

    socket.onclose = () => {
        addSystemMessage("La conexión con el servidor se ha cerrado.");
    };

    socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        addSystemMessage("Ocurrió un error con la conexión WebSocket.");
    };
}

function handleServerMessage(data) {
    switch (data.type) {
        case "welcome":
            currentUsername = data.username;
            document.getElementById(
                "current-username"
            ).textContent = `Usuario: ${currentUsername}`;
            addSystemMessage(`Te uniste como ${currentUsername}`);
            break;

        case "system":
            addSystemMessage(data.text);
            break;

        case "chat":
            addChatMessage(data.username, data.text, data.timestamp);
            break;

        case "history":
            (data.messages || []).forEach((msg) => {
                addChatMessage(msg.username, msg.text, msg.timestamp);
            });
            break;

        case "user_list":
            updateUserList(data.users || []);
            break;

        default:
            console.warn("Tipo de mensaje desconocido:", data);
    }
}

function addChatMessage(username, text, timestamp) {
    const messagesContainer = document.getElementById("messages");

    const item = document.createElement("div");
    item.classList.add("message");

    const isMe = username === currentUsername;
    if (isMe) {
        item.classList.add("me");
    }

    const header = document.createElement("div");
    header.classList.add("message-header");
    header.textContent = `[${timestamp}] ${username}`;

    const body = document.createElement("div");
    body.classList.add("message-body");
    body.textContent = text;

    item.appendChild(header);
    item.appendChild(body);

    messagesContainer.appendChild(item);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addSystemMessage(text) {
    const messagesContainer = document.getElementById("messages");

    const item = document.createElement("div");
    item.classList.add("message", "system");

    item.textContent = text;
    messagesContainer.appendChild(item);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateUserList(users) {
    const list = document.getElementById("users-list");
    list.innerHTML = "";

    users.forEach((u) => {
        const li = document.createElement("li");
        li.textContent = u;
        list.appendChild(li);
    });
}

function setupFormHandler() {
    const form = document.getElementById("message-form");
    const input = document.getElementById("message-input");

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const text = input.value.trim();
        if (!text || !socket || socket.readyState !== WebSocket.OPEN) {
            return;
        }

        socket.send(
            JSON.stringify({
                type: "chat",
                text: text,
            })
        );

        input.value = "";
        input.focus();
    });
}

document.addEventListener("DOMContentLoaded", () => {
    connectWebSocket();
    setupFormHandler();
});
