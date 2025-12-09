// main.js - Dynamizes the index: fetch /api/health and /api/rabbit
document.addEventListener("DOMContentLoaded", () => {
    const servicesGrid = document.getElementById("services-grid");
    const rabbitStatusEl = document.getElementById("rabbit-status");
    const publishBtn = document.getElementById("publish-test");
    const publishResult = document.getElementById("publish-result");
    const modeSwitch = document.getElementById("mode-switch");

    const REFRESH_SERVICES_INTERVAL = 10000; // 10 seconds
    const REFRESH_RABBIT_INTERVAL = 15000; // 15 seconds

    // Toggle dark mode
    modeSwitch.addEventListener("click", toggleDarkMode);

    // Load services and rabbit status on initial load
    loadServices();
    loadRabbit();
    setInterval(loadServices, REFRESH_SERVICES_INTERVAL);
    setInterval(loadRabbit, REFRESH_RABBIT_INTERVAL);

    async function toggleDarkMode() {
        document.body.classList.toggle("dark-mode");
        modeSwitch.textContent = document.body.classList.contains("dark-mode") ? "Modo Claro" : "Modo Escuro";
    }

    async function loadServices() {
        try {
            const data = await fetchData("/api/health");
            renderServices(data.services || []);
        } catch (err) {
            displayError(servicesGrid, "Erro a obter serviços", err.message);
        }
    }

    async function loadRabbit() {
        try {
            const j = await fetchData("/api/rabbit");
            updateRabbitStatus(j);
        } catch (e) {
            displayError(rabbitStatusEl, "Erro ao verificar RabbitMQ", e.message);
        }
    }

    async function fetchData(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Falha ao buscar ${url}`);
        return await res.json();
    }

    function renderServices(list) {
        if (!list.length) {
            servicesGrid.innerHTML = `<div class="card"><div class="label">Nenhum serviço registado</div></div>`;
            return;
        }
        const html = list.map(renderServiceCard).join("");
        servicesGrid.innerHTML = html;
    }

    function renderServiceCard(service) {
        const status = service.status || "unknown";
        const colorDot = getStatusColor(status);
        const latency = service.latency_ms ? `${service.latency_ms} ms` : "—";
        const details = service.details && Object.keys(service.details).length ? JSON.stringify(service.details) : "";
        return `
            <div class="card service">
                <div class="dot" style="background:${colorDot}"></div>
                <div class="meta">
                    <div class="name">${escapeHtml(service.name)}</div>
                    <div class="status">Estado: ${escapeHtml(status)} • Latência: ${escapeHtml(latency)} ${details ? ' • ' + escapeHtml(details) : ''}</div>
                </div>
            </div>
        `;
    }

    function getStatusColor(status) {
        switch (status) {
            case "online": return "#10b981";
            case "degraded": return "#f59e0b";
            default: return "#ef4444";
        }
    }

    function updateRabbitStatus(j) {
        if (j.ok) {
            rabbitStatusEl.textContent = `Online • ${j.details || ""}`;
            rabbitStatusEl.style.color = "#064e3b";
        } else {
            rabbitStatusEl.textContent = `Offline • ${j.error || ""}`;
            rabbitStatusEl.style.color = "#7f1d1d";
        }
    }

    function displayError(element, title, message) {
        element.innerHTML = `<div class="card"><div class="label">${title}</div><div class="small">${escapeHtml(message)}</div></div>`;
    }

    publishBtn.addEventListener("click", async () => {
        publishResult.textContent = "publicando...";
        try {
            const j = await publishEvent();
            publishResult.textContent = j.published ? "Publicado ✔" : "Falha ao publicar";
        } catch (e) {
            publishResult.textContent = "Erro: " + e.message;
        }
        setTimeout(() => publishResult.textContent = "", 3000);
    });

    async function publishEvent() {
        const res = await fetch("/api/events/publish", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type: "test.event", timestamp: Date.now(), source: "dashboard" })
        });
        return await res.json();
    }

    function escapeHtml(s) {
        return String(s || "").replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
    }
});
