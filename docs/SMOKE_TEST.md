# Comprobación del hito F1

La prueba automatizada `scripts/verify_browser.py` utiliza Chromium real, servidor
temporal en loopback y SQLite temporal migrada. No usa respuestas simuladas.

1. Abrir la página y acceder al enlace de salto con Tab/Enter.
2. Cambiar a crear cuenta y registrar un correo nuevo con contraseña de 12–128 caracteres.
3. Comprobar que vuelve al login y limpia la contraseña.
4. Intentar login incorrecto y comprobar mensaje visible; después usar la contraseña correcta.
5. Verificar correo de la sesión, foco en el encabezado y contadores sin datos ficticios.
6. Probar Nuevo proyecto: el cliente envía CSRF y la API responde HTTP 501 deliberado.
7. Recargar: la sesión se conserva; cerrar sesión elimina cookies y sobrevive a otra recarga.
8. Revisar login/panel a 1366px y 390px; panel también a 320px, sin desbordamiento global.

Capturas: `artifacts/auth_desktop.png`, `auth_mobile.png`, `dashboard_desktop.png`
y `dashboard_mobile.png`. Resultados: `artifacts/browser_smoke.json`.
Los artefactos son locales e ignorados por Git. Se realizó revisión visual de
las capturas de escritorio y móvil. Esta comprobación cubre F1, no CRUD de F2.

Para prueba manual, ejecutar `./iniciar.sh` y seguir los mismos pasos en
http://127.0.0.1:8765. Las pruebas de pytest verifican por separado todas las
diez rutas CRUD pendientes: 401 sin sesión, 403 sin CSRF para mutaciones y 501
con sesión y token válidos.
