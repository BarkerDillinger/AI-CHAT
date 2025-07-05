async function loadModels() {
    const modelSelect = document.getElementById("model");
    try {
        const response = await fetch("/models");
        const models = await response.json();

        // Clear existing options
        modelSelect.innerHTML = "";

        // Get the default model value rendered from Jinja2 template
        const defaultModel = document.body.getAttribute("data-default-model");

        models.forEach(model => {
            const option = document.createElement("option");
            option.value = model;
            option.text = model;
            modelSelect.appendChild(option);
        });

        if (defaultModel && models.includes(defaultModel)) {
            modelSelect.value = defaultModel;
        }
    } catch (error) {
        console.error("Failed to load models:", error);
    }
}

window.onload = loadModels;
