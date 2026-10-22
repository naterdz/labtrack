/* Prueba de navegador real contra el servidor temporal de verify_browser.py. */
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROMIUM_EXECUTABLE ? { executablePath: process.env.CHROMIUM_EXECUTABLE } : {}),
  });
  const artifactDir = path.resolve("artifacts");
  fs.mkdirSync(artifactDir, { recursive: true });
  const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const email = `smoke-${Date.now()}@example.com`;
  const password = crypto.randomBytes(24).toString("base64url");
  const results = [];
  const noOverflow = async (label) => {
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), label);
    results.push(label);
  };
  try {
    await page.goto(process.env.LABTRACK_TEST_URL, { waitUntil: "networkidle" });
    await page.locator("#auth-view").waitFor({ state: "visible" });
    await page.keyboard.press("Tab");
    assert.equal(await page.locator(":focus").textContent(), "Ir al contenido");
    await page.keyboard.press("Enter");
    results.push("enlace de salto accesible por teclado");
    await noOverflow("login escritorio sin desbordamiento");
    await page.screenshot({ path: path.join(artifactDir, "auth_desktop.png"), fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    await noOverflow("login móvil sin desbordamiento");
    await page.screenshot({ path: path.join(artifactDir, "auth_mobile.png"), fullPage: true });
    await page.locator("#register-mode").click();
    await page.getByLabel("Correo electrónico", { exact: true }).fill(email);
    await page.getByLabel("Contraseña", { exact: true }).fill(password);
    await page.locator("#show-password").click();
    assert.equal(await page.locator("#password").getAttribute("type"), "text");
    await page.locator("#show-password").click();
    await page.locator("#submit-auth").click();
    await page.locator("#auth-success").waitFor({ state: "visible" });
    assert.match(await page.locator("#auth-success").textContent(), /Tu cuenta está lista/);
    assert.equal(await page.locator("#password").inputValue(), "");
    results.push("registro real y transición a login sin conservar contraseña");
    await page.locator("#password").fill("incorrecta");
    await page.locator("#submit-auth").click();
    await page.locator("#auth-error").waitFor({ state: "visible" });
    assert.match(await page.locator("#auth-error").textContent(), /Correo o contraseña incorrectos/);
    results.push("error de credenciales visible");
    await page.locator("#password").fill(password);
    await page.locator("#submit-auth").click();
    await page.locator("#dashboard-view").waitFor({ state: "visible" });
    await page.waitForFunction(() => document.getElementById("workspace-message").textContent.includes("HTTP 501"));
    assert.equal(await page.locator("#account-email").textContent(), email);
    assert.equal(await page.locator(":focus").getAttribute("id"), "dashboard-title");
    assert.deepEqual(await page.locator(".stat-card > strong").allTextContents(), ["—", "—"]);
    assert.equal(await page.locator("tbody tr").count(), 1);
    assert.equal(await page.locator("#password").inputValue(), "");
    assert(!(await page.evaluate(() => document.cookie)).includes("labtrack_session="));
    results.push("login, foco, sesión HttpOnly y contadores pendientes sin datos ficticios");
    const [mutation] = await Promise.all([
      page.waitForResponse((response) => response.url().endsWith("/api/projects") && response.request().method() === "POST"),
      page.locator("#new-project").click(),
    ]);
    assert.equal(mutation.status(), 501);
    assert(mutation.request().headers()["x-csrf-token"]);
    results.push("POST pendiente devuelve 501 con CSRF enviado por el cliente");
    await noOverflow("dashboard móvil sin desbordamiento");
    await page.screenshot({ path: path.join(artifactDir, "dashboard_mobile.png"), fullPage: true });
    await page.setViewportSize({ width: 320, height: 720 });
    await noOverflow("dashboard a 320px sin desbordamiento global");
    await page.setViewportSize({ width: 1366, height: 900 });
    await noOverflow("dashboard escritorio sin desbordamiento");
    await page.screenshot({ path: path.join(artifactDir, "dashboard_desktop.png"), fullPage: true });
    await page.reload({ waitUntil: "networkidle" });
    await page.locator("#dashboard-view").waitFor({ state: "visible" });
    results.push("sesión conservada al recargar");
    await page.locator("#logout").click();
    await page.locator("#auth-view").waitFor({ state: "visible" });
    const cookies = await context.cookies();
    assert(!cookies.some((cookie) => cookie.name.startsWith("labtrack_")));
    await page.reload({ waitUntil: "networkidle" });
    await page.locator("#auth-view").waitFor({ state: "visible" });
    results.push("logout elimina cookies y mantiene salida tras recargar");
    assert.deepEqual(errors, []);
    results.push("sin excepciones JavaScript");
    const report = { result: "PASS", checks: results, screenshots: [
      "auth_desktop.png", "auth_mobile.png", "dashboard_desktop.png", "dashboard_mobile.png",
    ] };
    fs.writeFileSync(path.join(artifactDir, "browser_smoke.json"), JSON.stringify(report, null, 2) + "\n");
    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
