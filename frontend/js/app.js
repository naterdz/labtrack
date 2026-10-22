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
  setMode("login", focus);
  document.title = "LabTrack · Tu espacio de investigación";
}

async function loadProjects(method = "GET") {
  try {
    await api("/projects", { method, ...(method === "POST" ? { body: {} } : {}) });
    notify("workspace-message", "La lista de proyectos se actualizará al habilitar la siguiente etapa.");
  } catch (error) {
    if (error.status === 401) {
      authView();
      notify("auth-error", "Tu sesión terminó. Inicia sesión de nuevo.");
      return;
    }
    notify("workspace-message", `${error.status ? `HTTP ${error.status} · ` : ""}${error.message}`);
  }
}

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
$("new-project").addEventListener("click", () => loadProjects("POST"));

try {
  const user = await api("/auth/me");
  await dashboardView(user);
} catch (error) {
  authView(false);
  if (error.status !== 401) notify("auth-error", error.message);
}
