function setModelCookie(model) {
    const days = 30;
    const expires = new Date(Date.now() + days * 86400 * 1000).toUTCString();
    document.cookie = `selected_model=${model}; path=/; max-age=${60 * 60 * 24 * 30}; expires=${expires}`;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

async function loadModels() {
    const modelSelect = document.getElementById("model");
    try {
        const response = await fetch("/models");
        const models = await response.json();

        // Clear and populate
        modelSelect.innerHTML = "";

        const cookieModel = getCookie("selected_model");
        const defaultModel = document.body.getAttribute("data-default-model");

        models.forEach(model => {
            const option = document.createElement("option");
            option.value = model;
            option.text = model;
            modelSelect.appendChild(option);
        });

        if (cookieModel && models.includes(cookieModel)) {
            modelSelect.value = cookieModel;
        } else if (defaultModel && models.includes(defaultModel)) {
            modelSelect.value = defaultModel;
        }

        modelSelect.addEventListener("change", () => {
            setModelCookie(modelSelect.value);
        });
    } catch (error) {
        console.error("Failed to load models:", error);
    }
}

window.onload = loadModels;
