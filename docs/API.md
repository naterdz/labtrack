> La sección F2 al final describe el comportamiento actual. Los 501 descritos
> en la sección histórica de F1 solo corresponden al tag v0.1.0.

# API · F1

Mismo origen que la interfaz, prefijo `/api`. Todos los errores de aplicación
usan `{code, message, details?}`. La validación 422 omite valores de entrada,
incluidas contraseñas. OpenAPI: `/docs`.

| Método | Ruta | Respuesta F1 |
| --- | --- | --- |
| GET | `/api/health` | 200 `{status: "ok", service: "labtrack"}` |
| POST | `/api/auth/register` | 201 `{id, email}`; 409 `email_exists` |
| POST | `/api/auth/login` | 200 `{id, email}` y cookies |
| GET | `/api/auth/me` | 200 `{id, email}`; 401 sin sesión válida |
| POST | `/api/auth/logout` | 204 sin cuerpo; 401 sin sesión; 403 sin CSRF válido |

Registro/login reciben JSON `{email, password}`. El correo se recorta y pasa a
minúsculas. Registro exige contraseña de 12 a 128 caracteres; login admite de
1 a 128. Los campos adicionales se rechazan. Registrarse no inicia sesión.
Credenciales incorrectas o cuenta inexistente devuelven el mismo 401.

## Sesión y CSRF

Contraseñas con Argon2id. Sesión firmada con ItsDangerous y caducidad de 8 horas
(`SESSION_TTL_SECONDS`, entre 60 y 604800). Cada login genera un nuevo nonce.

- `labtrack_session`: HttpOnly, SameSite=Lax, Path=/, sin Domain.
- `labtrack_csrf`: legible por JavaScript, mismos Path/SameSite/TTL.
- `COOKIE_SECURE=true` activa Secure en ambas; obligatorio con APP_ENV=production.
- Mutaciones autenticadas: enviar `X-CSRF-Token` con el valor de `labtrack_csrf`.
  Se comparan cookie y header con el nonce incluido en la sesión firmada.
- Un Origin ajeno se rechaza en registro, login y mutaciones autenticadas.
- Logout elimina ambas cookies. Esta implementación usa sesiones firmadas sin
  estado: no hay revocación central de copias anteriores; vencen al expirar.
- Nunca almacenar sesión ni contraseña en localStorage.

## Contrato pendiente

| Métodos | Ruta | Respuesta F1 con sesión/CSRF válidos |
| --- | --- | --- |
| GET, POST | `/api/projects` | 501 `not_implemented` |
| GET, PATCH, DELETE | `/api/projects/{project_id}` | 501 `not_implemented` |
| GET, POST | `/api/projects/{project_id}/experiments` | 501 `not_implemented` |
| GET, PATCH, DELETE | `/api/projects/{project_id}/experiments/{experiment_id}` | 501 `not_implemented` |

IDs de ruta UUID. Las diez rutas CRUD son stubs deliberados de F1; no crean,
leen ni modifican datos. Primero exigen sesión (401) y, en mutaciones, CSRF
(403); con credenciales válidas devuelven 501. Se reemplazan por CRUD en F2.
El resumen `/api/summary` y sus conteos reales se implementan en F2; en F1
la ruta aún devuelve 404 y la UI muestra guiones, no ceros inventados.

## F2 · API funcional

Todas las rutas de proyectos y experimentos ya implementan CRUD. Crear devuelve
201, PATCH devuelve 200 y DELETE devuelve 204 sin cuerpo. Los listados son arrays.
Los campos desconocidos, nombres vacíos, PATCH vacío, null en campos obligatorios
y métricas no finitas devuelven 422. PATCH conserva campos omitidos y permite
limpiar campos opcionales mediante null. Los nombres se recortan.

GET `/api/projects/{project_id}/experiments` acepta `model` (igualdad sin distinguir
mayúsculas), `q` (subcadena literal sobre nombre, dataset, modelo o notas),
`limit=20` (1..100) y `offset=0` (>=0). Orden estable por creación e id.
Las búsquedas usan parámetros SQL y escapan comodines. GET `/api/summary` devuelve
`projects_count` y `experiments_count` exclusivamente de la cuenta autenticada.

Errores uniformes: `{code,message,details?}`. 401 sin sesión, 403 CSRF/origen
inválido, 404 recurso inexistente o ajeno, 409 proyecto con experimentos (eliminar
primero sus experimentos), 422 validación. Todas las mutaciones mantienen CSRF.
