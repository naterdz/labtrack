import { api } from "./api.js";

const $ = (id) => document.getElementById(id);
let mode = "login";
let authBusy = false;

function notify(id, text) {
  $(id).textContent = text;
  $(id).hidden = !text;
}

function setMode(nextMode, focus = true) {
  mode = nextMode;
  const registration = mode === "register";
  $("login-mode").setAttribute("aria-pressed", String(!registration));
  $("register-mode").setAttribute("aria-pressed", String(registration));
  $("auth-title").textContent = registration ? "Tu próxima idea empieza aquí." : "Qué bueno verte.";
  $("auth-description").textContent = registration ? "Crea tu cuenta y haz espacio para lo que sigue." : "Inicia sesión para continuar con tus ideas.";
  $("submit-auth").firstElementChild.textContent = registration ? "Crear mi cuenta" : "Entrar a mi espacio";
  $("password").minLength = registration ? 12 : 1;
  $("password").autocomplete = registration ? "new-password" : "current-password";
  $("password-hint").textContent = registration ? "Usa entre 12 y 128 caracteres." : "Tu contraseña distingue mayúsculas y minúsculas.";
  $("password").value = "";
  $("password").type = "password";
  $("show-password").textContent = "Mostrar";
  $("show-password").setAttribute("aria-pressed", "false");
  notify("auth-error", "");
  notify("auth-success", "");
  if (focus) $("email").focus();
}

function authView(focus = true) {
  $("loading").hidden = true;
  $("dashboard-view").hidden = true;
  $("auth-view").hidden = false;
  $("account-email").textContent = "";
  notify("workspace-message", "");
  projects = []; experiments = []; selectedId = ""; offset = 0; revision++;
  $("model-filter").value = ""; $("search-filter").value = "";
  setMode("login", focus);
  document.title = "LabTrack · Tu espacio de investigación";
}

let projects = [];
let experiments = [];
let selectedId = "";
let offset = 0;
let revision = 0;
let editorAction = null;
let deleteAction = null;
let mutationBusy = false;
const pageSize = 20;

function workspaceError(error) {
  if (error.status === 401) {
    authView();
    notify("auth-error", "Tu sesión terminó. Inicia sesión de nuevo.");
  } else notify("workspace-message", `${error.status ? `HTTP ${error.status} · ` : ""}${error.message}`);
}

function experimentPath(id = "") {
  return `/projects/${selectedId}/experiments${id ? `/${id}` : ""}`;
}

function textElement(tag, text) {
  const element = document.createElement(tag);
  element.textContent = text;
  return element;
}

async function loadExperiments() {
  const token = ++revision;
  $("experiment-rows").replaceChildren();
  $("previous-page").disabled = true;
  $("next-page").disabled = true;
  if (!selectedId) {
    const row = document.createElement("tr");
    const cell = textElement("td", "Crea o selecciona un proyecto para registrar experimentos.");
    cell.colSpan = 4; row.append(cell); $("experiment-rows").append(row);
    $("page-label").textContent = "";
    return;
  }
  const query = new URLSearchParams({ model: $("model-filter").value.trim(), q: $("search-filter").value.trim(), limit: pageSize, offset });
  const rows = await api(`${experimentPath()}?${query}`);
  if (token !== revision) return;
  experiments = rows;
  for (const experiment of rows) {
    const row = document.createElement("tr");
    const title = document.createElement("td");
    title.append(textElement("strong", experiment.name), textElement("p", experiment.dataset_name));
    const actions = document.createElement("td");
    for (const [label, action] of [["Editar", () => editExperiment(experiment)], ["Eliminar", () => confirmDelete(`¿Eliminar el experimento «${experiment.name}»?`, async () => { await api(experimentPath(experiment.id), { method: "DELETE" }); await loadProjects(); })]]) {
      const button = textElement("button", label); button.type = "button"; button.className = "text-button";
      button.setAttribute("aria-label", `${label} experimento ${experiment.name}`);
      button.addEventListener("click", action); actions.append(button);
    }
    row.append(title, textElement("td", experiment.model_name), textElement("td", experiment.metric_value === null ? "—" : `${experiment.metric_name || "Métrica"}: ${experiment.metric_value}`), actions);
    $("experiment-rows").append(row);
  }
  if (!rows.length) {
    const row = document.createElement("tr"); const cell = textElement("td", "No hay experimentos que coincidan."); cell.colSpan = 4; row.append(cell); $("experiment-rows").append(row);
  }
  $("previous-page").disabled = offset === 0;
  $("next-page").disabled = rows.length < pageSize;
  $("page-label").textContent = `Página ${Math.floor(offset / pageSize) + 1}`;
}

async function loadProjects() {
  try {
    const [list, totals] = await Promise.all([api("/projects"), api("/summary")]);
    projects = list;
    if (!projects.some(project => project.id === selectedId)) { selectedId = projects[0]?.id || ""; offset = 0; }
    $("project-select").replaceChildren();
    if (!projects.length) $("project-select").append(new Option("Aún no hay proyectos", ""));
    for (const project of projects) $("project-select").append(new Option(project.name, project.id));
    $("project-select").value = selectedId;
    $("projects-count").textContent = totals.projects_count;
    $("experiments-count").textContent = totals.experiments_count;
    const project = projects.find(item => item.id === selectedId);
    $("project-detail").hidden = !project;
    $("selected-project-name").textContent = project?.name || "";
    $("selected-project-description").textContent = project?.description || "Sin descripción";
    $("new-experiment").disabled = !project;
    await loadExperiments();
  } catch (error) { workspaceError(error); }
}

function openEditor(title, fields, values, action) {
  editorAction = action;
  $("editor-title").textContent = title;
  $("editor-fields").replaceChildren();
  notify("editor-error", "");
  for (const [name, label, required, maxLength, type] of fields) {
    const id = `edit-${name}`;
    const labelElement = textElement("label", label); labelElement.htmlFor = id;
    const input = document.createElement(type === "textarea" ? "textarea" : "input");
    input.id = id; input.name = name; input.required = required;
    if (type === "number") { input.type = "number"; input.step = "any"; }
    else input.maxLength = maxLength;
    input.value = values[name] ?? "";
    $("editor-fields").append(labelElement, input);
  }
  $("editor").showModal();
}

const projectFields = [["name", "Nombre", true, 120], ["description", "Descripción", false, 2000, "textarea"]];
const experimentFields = [["name", "Nombre", true, 120], ["dataset_name", "Dataset", true, 200], ["model_name", "Modelo", true, 120], ["metric_name", "Nombre de métrica", false, 80], ["metric_value", "Valor de métrica", false, null, "number"], ["notes", "Notas", false, 4000, "textarea"]];
function editProject(project = null) {
  const id = project?.id;
  openEditor(id ? "Editar proyecto" : "Nuevo proyecto", projectFields, project || {}, async data => {
    const saved = await api(id ? `/projects/${id}` : "/projects", { method: id ? "PATCH" : "POST", body: data });
    selectedId = saved.id; offset = 0; await loadProjects();
  });
}
function editExperiment(experiment = null) {
  const path = experimentPath(experiment?.id);
  openEditor(experiment ? "Editar experimento" : "Nuevo experimento", experimentFields, experiment || {}, async data => {
    data.metric_value = data.metric_value === null ? null : Number(data.metric_value);
    await api(path, { method: experiment ? "PATCH" : "POST", body: data });
    await loadProjects();
  });
}
function confirmDelete(message, action) {
  deleteAction = action; $("confirmation-text").textContent = message; $("confirmation").showModal();
}
$("editor-form").addEventListener("submit", async event => {
  event.preventDefault(); if (mutationBusy) return;
  mutationBusy = true; $("save-editor").disabled = true; $("cancel-editor").disabled = true;
  const data = Object.fromEntries([...new FormData(event.target)].map(([key, value]) => [key, value.trim() || null]));
  try { await editorAction(data); $("editor").close(); notify("workspace-message", "Cambios guardados."); }
  catch (error) { if (error.status === 401) { $("editor").close(); workspaceError(error); } else notify("editor-error", error.message); }
  finally { mutationBusy = false; $("save-editor").disabled = false; $("cancel-editor").disabled = false; }
});
$("cancel-editor").addEventListener("click", () => $("editor").close());
$("editor").addEventListener("cancel", event => { if (mutationBusy) event.preventDefault(); });
$("cancel-delete").addEventListener("click", () => $("confirmation").close());
$("confirmation").addEventListener("cancel", event => { if (mutationBusy) event.preventDefault(); });
$("confirm-delete").addEventListener("click", async () => {
  if (mutationBusy) return; mutationBusy = true; $("confirm-delete").disabled = true; $("cancel-delete").disabled = true;
  try { await deleteAction(); notify("workspace-message", "Registro eliminado."); }
  catch (error) { workspaceError(error); }
  finally { $("confirmation").close(); mutationBusy = false; $("confirm-delete").disabled = false; $("cancel-delete").disabled = false; }
});
$("project-select").addEventListener("change", async () => { selectedId = $("project-select").value; offset = 0; await loadProjects(); });
$("filters").addEventListener("submit", event => { event.preventDefault(); offset = 0; loadExperiments().catch(workspaceError); });
$("previous-page").addEventListener("click", () => { offset = Math.max(0, offset - pageSize); loadExperiments().catch(workspaceError); });
$("next-page").addEventListener("click", () => { offset += pageSize; loadExperiments().catch(workspaceError); });
$("edit-project").addEventListener("click", () => editProject(projects.find(item => item.id === selectedId)));
$("delete-project").addEventListener("click", () => {
  const project = projects.find(item => item.id === selectedId);
  confirmDelete(`¿Eliminar el proyecto «${project.name}»? Primero debe quedar sin experimentos.`, async () => { await api(`/projects/${project.id}`, { method: "DELETE" }); await loadProjects(); });
});
$("new-experiment").addEventListener("click", () => editExperiment());

async function dashboardView(user) {
  $("loading").hidden = true;
  $("auth-view").hidden = true;
  $("dashboard-view").hidden = false;
  $("account-email").textContent = user.email;
  $("account-email").title = user.email;
  $("account-avatar").textContent = user.email.charAt(0).toUpperCase();
  $("password").value = "";
  $("dashboard-title").focus();
  document.title = "Vista general · LabTrack";
  await loadProjects();
}

$("login-mode").addEventListener("click", () => setMode("login"));
$("register-mode").addEventListener("click", () => setMode("register"));
$("show-password").addEventListener("click", () => {
  const visible = $("password").type === "password";
  $("password").type = visible ? "text" : "password";
  $("show-password").textContent = visible ? "Ocultar" : "Mostrar";
  $("show-password").setAttribute("aria-pressed", String(visible));
});

$("auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (authBusy) return;
  authBusy = true;
  const submittedMode = mode;
  const fields = [$("submit-auth"), $("login-mode"), $("register-mode")];
  fields.forEach((element) => { element.disabled = true; });
  $("auth-form").setAttribute("aria-busy", "true");
  notify("auth-error", "");
  notify("auth-success", "");
  try {
    const user = await api(`/auth/${submittedMode}`, { method: "POST", body: {
      email: $("email").value.trim(), password: $("password").value,
    } });
    if (submittedMode === "register") {
      setMode("login", false);
      notify("auth-success", "Tu cuenta está lista. Inicia sesión para continuar.");
      $("password").focus();
    } else {
      await dashboardView(user);
    }
  } catch (error) {
    notify("auth-error", error.status === 422 ? "Revisa el correo y la longitud de tu contraseña." : error.message);
    $("password").value = "";
    $("password").focus();
  } finally {
    authBusy = false;
    fields.forEach((element) => { element.disabled = false; });
    $("auth-form").removeAttribute("aria-busy");
  }
});

$("logout").addEventListener("click", async () => {
  $("logout").disabled = true;
  try {
    await api("/auth/logout", { method: "POST" });
    authView();
    notify("auth-success", "Cerraste sesión correctamente.");
  } catch (error) {
    if (error.status === 401) authView();
    else notify("workspace-message", error.message);
  } finally {
    $("logout").disabled = false;
  }
});
$("refresh-projects").addEventListener("click", () => loadProjects());
$("new-project").addEventListener("click", () => editProject());

try {
  const user = await api("/auth/me");
  await dashboardView(user);
} catch (error) {
  authView(false);
  if (error.status !== 401) notify("auth-error", error.message);
}
