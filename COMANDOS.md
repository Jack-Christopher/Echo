# Echo — comandos de voz (frases exactas)

Mantén **Win+Espacio** (o el círculo azul) **pulsado**, di la frase, suelta. Mira la **ventana de terminal** donde lanzaste Echo.

## Arrancar Echo

```powershell
cd C:\Users\User\OneDrive\Desktop\Echo
.\run_echo.bat
```

## Qué verás en la terminal

Ejemplo al decir *quiero ver matrix*:

```
[Echo] Escuchando... (mantén pulsado y habla)
[Echo] Procesando audio...
[Echo] Transcribiendo: C:\Users\...\tmpXXXX.wav
[Echo] Texto entendido: "quiero ver matrix"
[Echo] Comando normalizado: "quiero ver matrix"
[Echo] Intent: search_web
[Echo] Ruta: Pelicula/Serie (OK.ru) -> https://www.google.com/search?q=matrix+site%3Am.ok.ru
[Echo] Resultado: Pelicula/Serie (OK.ru): matrix (ok)
```

- **Texto entendido** = lo que Whisper oyó (sin editar).
- **Comando normalizado** = texto tras quitar acentos/rellenos.
- Si no coincide con ningún patrón: `Intent: unknown` y `No entendi`.

---

## Comandos por defecto

Echo viene con **tres frases de búsqueda** y los **controles del dispositivo**. Sin más rutas ni sitios precargados (puedes añadir los que quieras en Configuración).

### 1. Películas y series — `quiero ver ...`

| Di | Acción |
|-----|--------|
| `quiero ver matrix` | Google `matrix site:m.ok.ru` |
| `quiero ver serie breaking bad` | Google `serie breaking bad site:m.ok.ru` |
| `quiero ver pelicula avatar` | Google `pelicula avatar site:m.ok.ru` |

Usa el buscador (Google por defecto) con el operador `site:m.ok.ru` para encontrar el contenido en OK.ru.

**Alternativa Cuevana:** edita la ruta `quiero_ver` en `%LOCALAPPDATA%\Echo\config.json` o en Configuración → Búsquedas:

```json
{
  "id": "quiero_ver",
  "resolve_mode": "template",
  "template": "https://cuevanapro.org/search?s={query}",
  "terms": ["quiero ver"],
  "match": "leading",
  "priority": 200,
  "strip_terms": true
}
```

### 2. Tutoriales y cursos — `quiero aprender ...`

| Di | Acción |
|-----|--------|
| `quiero aprender python` | YouTube: `python` |
| `quiero aprender a soldar` | YouTube: `a soldar` |
| `quiero aprender ingles` | YouTube: `ingles` |

URL: `https://www.youtube.com/results?search_query={query}`

### 3. Música — `quiero escuchar ...`

| Di | Acción |
|-----|--------|
| `quiero escuchar bad bunny` | YouTube Music: `bad bunny` |
| `quiero escuchar rock clasico` | YouTube Music: `rock clasico` |
| `quiero escuchar bohemian rhapsody` | YouTube Music: `bohemian rhapsody` |

URL: `https://music.youtube.com/search?q={query}`

### 4. Búsqueda general — `busca ...`

Si no quieres usar los tres anteriores, queda el comodín:

| Di | Acción |
|-----|--------|
| `busca recetas de pollo` | Google: `recetas de pollo` |
| `busca clima madrid` | Google: `clima madrid` |

---

## Control del dispositivo

### Volumen y brillo (pasos de 25)

| Di | Acción |
|----|--------|
| `sube volumen` / `subir volumen` / `aumenta volumen` | +25 % volumen |
| `baja volumen` / `reduce volumen` | -25 % volumen |
| `sube brillo` | +25 % brillo |
| `baja brillo` | -25 % brillo |
| `volumen` | Sube volumen (sin verbo = sube) |
| `brillo` | Sube brillo |

### Reproductor (teclas multimedia)

| Di | Acción |
|----|--------|
| `pausa` | Pausar |
| `reproducir` | Reproducir |
| `siguiente` / `siguiente video` | Siguiente |
| `anterior` | Anterior |
| `silencio` | Silenciar |
| `desilenciar` | Quitar silencio |

### Carpetas

| Di | Acción |
|----|--------|
| `abre descargas` | Abre Descargas |
| `abre documentos` | Abre Documentos |

### Dictado

| Di | Acción |
|----|--------|
| `iniciar dictado` / `empezar dictado` / `activar dictado` | Modo dictado ON |
| `terminar dictado` / `finalizar dictado` / `parar dictado` | Modo dictado OFF |

Con dictado activo, cualquier otra frase se escribe como texto.

---

## Navegador

En **Configuracion** (bandeja o clic derecho en el círculo azul) elige:

| Opción | Ejecutable típico |
|--------|-------------------|
| Brave | `brave.exe` |
| Google Chrome | `chrome.exe` |
| Microsoft Edge | `msedge.exe` |
| Mozilla Firefox | `firefox.exe` |
| Opera | `opera.exe` |
| Opera GX | `opera.exe` (carpeta Opera GX) |

Campo **Ruta al .exe**: solo si no se detecta solo.

### Cómo Echo abre pestañas

1. **Nueva pestaña por CLI** (Chromium: `--new-tab`, Firefox: `-new-tab`).
2. Si falla, **Ctrl+T** + escribe URL + Enter.
3. Log de cada lanzamiento: `%LOCALAPPDATA%\Echo\logs\browser-last.log`.

---

## Varios comandos seguidos

Separa con **y**, **luego** o **entonces**:

| Di | Acción |
|----|--------|
| `sube volumen y abre descargas` | Dos pasos en orden |
| `quiero escuchar jazz y baja brillo` | Música + bajar brillo |

Si una parte no se entiende, falla toda la cadena.

---

## Personalizar

Configuración → pestaña **Búsquedas** para añadir más rutas (custom sites o templates). Pestaña **Sitios** para `abre <alias>` (vacío por defecto). Los cambios se guardan en `%LOCALAPPDATA%\Echo\config.json`.

---

## Precision del reconocimiento de voz

En **Configuracion → Voz**:

| Opcion | Recomendacion |
|--------|----------------|
| **Modelo Whisper** | **Small** (precision); **Base** si la PC va lenta |
| **Beam size** | **8** (mas precision) o **1-3** (mas rapido) |
| **Pista de comandos** | **Si** — sesga Whisper hacia `quiero ver`, `quiero aprender`, etc. |

### Consejos al hablar

1. **1–2 segundos** mínimo, cerca del micro, sin música fuerte de fondo.
2. Mira **Texto entendido** en la terminal; si falla, repite más despacio.
3. Umbral fuzzy **85**: frases parecidas a las de la tabla aún pueden ejecutarse.

---

## Salir de Echo

- Clic derecho en el **círculo azul** → **Salir**
- O bandeja del sistema → **Salir**
