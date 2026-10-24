import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const NODE_TYPE = "MARWorkflowLoop";
const promptStates = new Map();

api.addEventListener("executed", ({ detail }) => {
    const nodeId = Number(detail?.node);
    if (!Number.isFinite(nodeId)) return;

    const node = app.graph?.getNodeById(nodeId);
    if (node?.type !== NODE_TYPE) return;

    const promptId = detail?.prompt_id;
    const repeatOutput = detail?.output?.repeat;
    const repeat = Array.isArray(repeatOutput) ? repeatOutput[0] : repeatOutput;
    if (promptId == null || typeof repeat !== "boolean") return;

    const key = String(promptId);
    promptStates.set(key, { repeat });
});

api.addEventListener("execution_success", async ({ detail }) => {
    const promptId = detail?.prompt_id;
    if (promptId == null) return;

    const key = String(promptId);
    const state = promptStates.get(key);
    promptStates.delete(key);

    if (!state?.repeat) return;

    try {
        await app.queuePrompt(0, 1);
    } catch (error) {
        console.error("Martinodes workflow loop could not queue the next run.", error);
    }
});

api.addEventListener("execution_error", ({ detail }) => {
    if (detail?.prompt_id != null) {
        promptStates.delete(String(detail.prompt_id));
    }
});
