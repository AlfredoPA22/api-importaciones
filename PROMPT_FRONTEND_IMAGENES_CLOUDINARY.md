# PROMPT PARA FRONTEND – IMÁGENES CON CLOUDINARY

## 🎯 Contexto General
- El backend ya maneja todo el pipeline: recibe el archivo (multipart/form-data), lo sube a Cloudinary (folder `Home/Importaciones`) y guarda en MongoDB **la `secure_url`** que Cloudinary devuelve.
- El frontend solo necesita mandar el archivo correcto y usar la URL que llega en la respuesta o en el objeto de la importación.
- No hay archivos estáticos locales ni base64: **todo es una URL HTTPS lista para usar en `<img>`**.

---

## 🔗 Endpoints Clave

### 1. Subir imagen
```
POST /imports/{import_id}/images
Content-Type: multipart/form-data
Body: file=<archivo>
```

**Validaciones Backend**
- Extensiones: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Tamaño máx: 10 MB

**Respuesta 201**
```json
{
  "message": "Imagen subida correctamente",
  "image_url": "https://res.cloudinary.com/....jpg"
}
```

> El backend retorna la URL final de Cloudinary. Guardarla localmente si hace falta mostrar feedback inmediato, pero recuerda recargar la importación para obtener la lista actualizada desde el backend.

### 2. Eliminar imagen
```
DELETE /imports/{import_id}/images/{image_index}
```

- `image_index` = posición dentro del arreglo `images` que entrega el backend (ej. `0`, `1`, `2`…).
- El backend elimina la imagen en Cloudinary y actualiza la lista en MongoDB.

**Respuesta 200**
```json
{ "message": "Imagen eliminada correctamente" }
```

---

## 🧩 Cómo consumir los datos

### Modelo de importación (fragmento)
```json
{
  "id": "65ac...",
  "images": [
    "https://res.cloudinary.com/dyyd4no6j/image/upload/v123/Home/Importaciones/auto_1.jpg",
    "https://res.cloudinary.com/dyyd4no6j/image/upload/v124/Home/Importaciones/auto_2.png"
  ],
  ...
}
```

- Usa los valores tal cual para `<img src="...">`.
- Para borrar, toma el **índice** en este array (`0`, `1`, etc.) y pásalo en la URL del DELETE.

---

## ⚙️ Snippet de integración (React)

```jsx
const API_BASE = import.meta.env.VITE_API_URL ?? "https://api-importaciones.vercel.app";

async function uploadImage(importId, file) {
  const allowed = ["image/jpeg","image/jpg","image/png","image/gif","image/webp"];
  if (!allowed.includes(file.type)) throw new Error("Formato no permitido");
  if (file.size > 10 * 1024 * 1024) throw new Error("Máximo 10MB");

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/imports/${importId}/images`, {
    method: "POST",
    body: formData
  });

  if (!res.ok) throw new Error((await res.json()).detail || "Error al subir");
  return res.json(); // { message, image_url }
}

async function deleteImage(importId, index) {
  const res = await fetch(`${API_BASE}/imports/${importId}/images/${index}`, {
    method: "DELETE"
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Error al eliminar");
}
```

---

## ✅ Checklist para FE
- [ ] Input `type="file"` con `accept="image/*"`.
- [ ] Validar tamaño ≤ 10 MB y tipo permitido **antes** de llamar al backend.
- [ ] Usar `FormData` y enviar el campo `file`.
- [ ] Al recibir la respuesta, actualizar la UI mostrando la URL segura.
- [ ] Para eliminar, usar el índice actual del arreglo `images`.
- [ ] Configurar la URL base del backend vía variable de entorno (`REACT_APP_API_URL`, etc.).

---

## 📝 Mensaje sugerido para el equipo FE
> “El backend ya sube las imágenes a Cloudinary. Solo necesitamos que el FE mande un `FormData` con el campo `file` al endpoint `POST /imports/{id}/images`. La respuesta trae `image_url` (URL HTTPS de Cloudinary). Para eliminar, usen `DELETE /imports/{id}/images/{index}` pasando el índice del array `images`. Así mostramos las imágenes directamente con ese URL sin procesamientos adicionales.”


