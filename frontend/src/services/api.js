// frontend/src/services/api.js
const BASE_URL = "http://localhost:8000";

/**
 * Analyze a clinical note (text)
 * POST /analyze
 */
export async function analyzeNote(clinicalNote, goal = "full analysis") {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ clinical_note: clinicalNote, goal }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }
  return response.json(); // AgentResponse
}

/**
 * Analyze a PDF file
 * POST /analyze/pdf  (multipart/form-data)
 */
export async function analyzePdf(file, goal = "full analysis") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("goal", goal);

  const response = await fetch(`${BASE_URL}/analyze/pdf`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }
  return response.json(); // AgentResponse
}

/**
 * Get a prompt by name
 * GET /prompts/{name}
 */
export async function getPrompt(name) {
  const response = await fetch(`${BASE_URL}/prompts/${name}`);
  if (!response.ok) throw new Error(`Prompt '${name}' not found`);
  return response.json();
}

/**
 * Update a prompt at runtime
 * PUT /prompts/{name}
 */
export async function updatePrompt(name, content) {
  const response = await fetch(`${BASE_URL}/prompts/${name}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Update failed");
  }
  return response.json();
}

