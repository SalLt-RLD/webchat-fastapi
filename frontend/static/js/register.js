document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirmPassword").value.trim();
    const errorBlock = document.getElementById("error");

    if (!username || !password || !confirmPassword) {
        errorBlock.textContent = "Пожалуйста, заполните все поля";
        return;
    }

    if (password !== confirmPassword) {
        errorBlock.textContent = "Пароли не совпадают 😬";
        return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
        const res = await fetch("auth/register", {
            method: "POST",
            body: formData,
            credentials: "include"
        });

        if (res.ok) {
            window.location.href = "/login";
        } else {
            const data = await res.json();
            errorBlock.textContent = data.detail || "Ошибка регистрации";
        }
    } catch (err) {
        errorBlock.textContent = "Сервер недоступен 😵‍💫";
    }
});
