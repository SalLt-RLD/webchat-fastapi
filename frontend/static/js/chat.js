let socket = null;
let currentUsername = null;
let currentRoomId = null;
const roomList = document.getElementById("roomList");
const messageInput = document.getElementById("messageInput");
const chatDiv = document.getElementById("chat");
const onlineUsersDiv = document.getElementById("onlineUsers");
const createRoomBtn = document.getElementById("createRoomBtn");
const createRoomModal = document.getElementById("createRoomModal");
const newRoomName = document.getElementById("newRoomName");
const newRoomDescription = document.getElementById("newRoomDescription");
const confirmCreateRoom = document.getElementById("confirmCreateRoom");
const cancelCreateRoom = document.getElementById("cancelCreateRoom");
const burgerMenu = document.getElementById("burgerMenu");
const sidebar = document.querySelector(".sidebar");
const chatMain = document.querySelector(".chat-main");
const connectionSpinner = document.getElementById("connectionSpinner");
const currentRoomName = document.getElementById("currentRoomName");

function formatTimestamp(timestamp) {
    const now = new Date();
    const date = new Date(timestamp.endsWith("Z") ? timestamp : timestamp + "Z");

    const isToday = now.toDateString() === date.toDateString();

    if (isToday) {
        return date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
    }

    const yesterday = new Date();
    yesterday.setDate(now.getDate() - 1);

    if (yesterday.toDateString() === date.toDateString()) {
        return `вчера, ${date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`;
    }

    return date.toLocaleDateString("ru-RU", {
        day: "numeric",
        month: "long"
    }) + ", " + date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
}

async function fetchRooms() {
    try {
        const errorBlock = document.getElementById("error");
        const response = await fetch("rooms", {
            method: "GET",
            credentials: "include",
        });
        if (!response.ok) {
            errorBlock.textContent = "Не удалось загрузить комнаты";
        }
        const rooms = await response.json();
        rooms.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        roomList.innerHTML = "";
        rooms.forEach(room => {
            const roomItem = document.createElement("div");
            roomItem.classList.add("room-item");
            roomItem.dataset.roomId = room.id;
            roomItem.innerHTML = `
                <h3>${room.name}</h3>
                <p>${room.description || "Без описания"}</p>
            `;
            roomItem.addEventListener("click", () => connectToRoom(room.id, room.name));
            roomList.appendChild(roomItem);
        });
    } catch (err) {
        console.error("Ошибка загрузки комнат:", err);
        alert("⚠ Ошибка загрузки комнат: " + err.message);
    }
}

async function createRoom() {
    const name = newRoomName.value.trim();
    const description = newRoomDescription.value.trim();
    const errorBlock = document.getElementById("error");

    if (!name) {
        alert("Название комнаты обязательно!");
        return;
    }
    const formData = new FormData();
    formData.append("name", name);
    formData.append("description", description);
    try {
        const response = await fetch("rooms", {
            method: "POST",
            credentials: "include",
            body: formData,
        });
        if (!response.ok) {
            const data = await response.json();
            errorBlock.textContent = data.detail || "Ошибка создания комнаты";
        }
        const newRoom = await response.json();
        createRoomModal.classList.add("hidden");
        newRoomName.value = "";
        newRoomDescription.value = "";
        await fetchRooms();
        connectToRoom(newRoom.id, newRoom.name);
    } catch (err) {
        console.error("Ошибка создания комнаты:", err);
        alert("⚠ Ошибка создания комнаты: " + err.message);
    }
}

async function connectToRoom(roomId, roomName) {
    if (socket) {
        socket.close();
    }
    currentRoomId = roomId;
    currentRoomName.textContent = roomName;
    chatMain.classList.remove("hidden");
    connectionSpinner.classList.remove("hidden");
    chatDiv.innerHTML = "";

    try {
        const response = await fetch("auth/me", {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            console.warn("⚠️ Не авторизован. Перенаправляем на логин...");
            window.location.href = "/login";
            return;
        }

        const data = await response.json();
        currentUsername = data.username;

        socket = new WebSocket(`ws://localhost:8000/ws/${roomId}`);

        socket.onopen = () => {
            console.log("✅ WebSocket connected");
            chatDiv.innerHTML = "";
            messageInput.focus();
            connectionSpinner.classList.add("hidden");
            document.querySelectorAll(".room-item").forEach(item => {
                item.classList.toggle("active", item.dataset.roomId === roomId);
            });
            if (window.innerWidth <= 700) {
                sidebar.classList.remove("active");
            }
        };

        let lastMessageDate = null;

        function formatDateLabel(date) {
            const now = new Date();
            const yesterday = new Date();
            yesterday.setDate(now.getDate() - 1);

            if (date.toDateString() === now.toDateString()) return "Сегодня";
            if (date.toDateString() === yesterday.toDateString()) return "Вчера";

            return date.toLocaleDateString("ru-RU", {day: "numeric", month: "long"});
        }

        function formatTimeLabel(date) {
            return date.toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
        }

        function addDateSeparator(date) {
            const label = formatDateLabel(date);
            const separator = document.createElement("div");
            separator.classList.add("date-separator");
            separator.textContent = label;
            chatDiv.appendChild(separator);
        }

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === "users_online") {
                    onlineUsersDiv.textContent = `👥 Online: ${data.users.length ? data.users.join(", ") : "(никого нет 😢)"}`;
                    return;
                }

                if (data.type === "system") {
                    const sysMsg = document.createElement("div");
                    sysMsg.classList.add("message", "system-message");
                    sysMsg.textContent = data.content;
                    chatDiv.appendChild(sysMsg);
                    chatDiv.scrollTop = chatDiv.scrollHeight;
                    return;
                }

                const dateObj = new Date(data.timestamp.endsWith("Z") ? data.timestamp : data.timestamp + "Z");

                if (!lastMessageDate || lastMessageDate.toDateString() !== dateObj.toDateString()) {
                    addDateSeparator(dateObj);
                    lastMessageDate = dateObj;
                }

                const messageEl = document.createElement("div");
                messageEl.classList.add("message");

                const timeSpan = document.createElement("div");
                timeSpan.classList.add("timestamp");
                timeSpan.textContent = formatTimeLabel(dateObj);

                const contentSpan = document.createElement("div");
                contentSpan.classList.add("content");

                if (data.username === currentUsername) {
                    messageEl.classList.add("own-message");
                    contentSpan.textContent = data.content;
                } else {
                    messageEl.classList.add("other-message");
                    const usernameSpan = document.createElement("div");
                    usernameSpan.classList.add("username");
                    usernameSpan.textContent = data.username;
                    messageEl.appendChild(usernameSpan);
                    contentSpan.textContent = data.content;
                }

                messageEl.appendChild(contentSpan);
                messageEl.appendChild(timeSpan);
                chatDiv.appendChild(messageEl);
                chatDiv.scrollTop = chatDiv.scrollHeight;

            } catch (err) {
                console.error("Ошибка парсинга:", err);
            }
        };

    } catch (err) {
        alert("⚠ Ошибка подключения: " + err.message);
        connectionSpinner.classList.add("hidden");
    }
}

function sendMessage() {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        alert("WebSocket не подключён!");
        return;
    }
    const text = messageInput.value;
    if (!text) return;

    socket.send(text);
    messageInput.value = "";
}

createRoomBtn.addEventListener("click", () => {
    createRoomModal.classList.remove("hidden");
    newRoomName.focus();
});

cancelCreateRoom.addEventListener("click", () => {
    createRoomModal.classList.add("hidden");
    newRoomName.value = "";
    newRoomDescription.value = "";
});

confirmCreateRoom.addEventListener("click", createRoom);

burgerMenu.addEventListener("click", () => {
    sidebar.classList.toggle("active");
});

messageInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

document.addEventListener("keydown", (event) => {
    if (!createRoomModal.classList.contains("hidden")) return;
    if (event.key === "Escape" && currentRoomId !== null) {
        chatMain.classList.add("hidden");
        if (socket) {
            socket.close();
            socket = null;
        }
        currentRoomId = null;
        currentRoomName.textContent = "Выберите чат";
        document.querySelectorAll(".room-item").forEach(item => {
            item.classList.remove("active");
        });
        return;
    }

    if (document.activeElement === messageInput) return;
    if (event.ctrlKey || event.altKey || event.metaKey) return;

    const isPrintable =
        event.key.length === 1 || event.key === "Backspace" || event.key === "Delete";

    if (isPrintable) {
        event.preventDefault();
        messageInput.focus();
        if (event.key.length === 1) {
            const cursorPos = messageInput.selectionStart;
            const text = messageInput.value;
            messageInput.value =
                text.slice(0, cursorPos) + event.key + text.slice(cursorPos);
            messageInput.selectionStart = messageInput.selectionEnd = cursorPos + 1;
        }
        if (event.key === "Backspace") {
            const cursorPos = messageInput.selectionStart;
            const text = messageInput.value;
            if (cursorPos > 0) {
                messageInput.value =
                    text.slice(0, cursorPos - 1) + text.slice(cursorPos);
                messageInput.selectionStart = messageInput.selectionEnd = cursorPos - 1;
            }
        }
        if (event.key === "Delete") {
            const cursorPos = messageInput.selectionStart;
            const text = messageInput.value;
            messageInput.value =
                text.slice(0, cursorPos) + text.slice(cursorPos + 1);
            messageInput.selectionStart = messageInput.selectionEnd = cursorPos;
        }
    }
});

window.onload = async () => {
    await fetchRooms();
};