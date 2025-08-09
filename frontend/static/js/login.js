document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    const res = await fetch("auth/login", {
        method: "POST",
        body: formData,
        credentials: "include"
    });

    if (res.ok) {
        window.location.href = "/";
    } else {
        document.getElementById("error").textContent = "Неверный логин или пароль 😢";
    }
});