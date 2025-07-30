let socket;
let currentUsername = null;
const roomIdInput = document.getElementById("roomId");
const messageInput = document.getElementById("messageInput");
const chatDiv = document.getElementById("chat");
const onlineUsersDiv = document.getElementById("onlineUsers");

function formatTimestamp(timestamp) {
    const now = new Date();
    const date = new Date(timestamp.endsWith("Z") ? timestamp : timestamp + "Z");

    const isToday = now.toDateString() === date.toDateString();

    if (isToday) {
        return date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}); // Только время
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


async function connect() {
    if (socket) {
        socket.close();
    }

    const roomId = roomIdInput.value;

    try {
        const response = await fetch("http://localhost:8000/auth/me", {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            alert("❌ Not authenticated. Please log in first.");
            return;
        }

        const data = await response.json();
        currentUsername = data.username;

        socket = new WebSocket(`ws://localhost:8000/ws/${roomId}`);

        socket.onopen = () => {
            console.log("✅ WebSocket connected");
            chatDiv.innerHTML = "";
            messageInput.focus();

        };

        let lastMessageDate = null;

        function formatDateLabel(date) {
            const now = new Date();
            const yesterday = new Date();
            yesterday.setDate(now.getDate() - 1);

            if (date.toDateString() === now.toDateString()) return "Сегодня";
            if (date.toDateString() === yesterday.toDateString()) return "Вчера";

            return date.toLocaleDateString("ru-RU", { day: "numeric", month: "long" }); // например, "30 июля"
        }

        function formatTimeLabel(date) {
            return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
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

                // ⛔ Если это первое сообщение ИЛИ дата изменилась — добавляем разделитель
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
    }
}

function sendMessage() {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        alert("WebSocket not connected!");
        return;
    }
    const text = messageInput.value;
    if (!text) return;

    socket.send(text);
    messageInput.value = "";
}

messageInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

window.onload = connect;
document.addEventListener("keydown", (event) => {
    // Если фокус уже на поле ввода — ничего не делаем
    if (document.activeElement === messageInput) return;

    // Пропускаем служебные клавиши, которые не должны попадать в инпут
    if (event.ctrlKey || event.altKey || event.metaKey) return;

    // Если это буква, цифра, пробел или символ — направляем в поле
    const isPrintable =
        event.key.length === 1 || event.key === "Backspace" || event.key === "Delete";

    if (isPrintable) {
        event.preventDefault(); // блокируем стандартное поведение
        messageInput.focus(); // фокусим поле
        // вставляем символ вручную (если не backspace/delete)
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
