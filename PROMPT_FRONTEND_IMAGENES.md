# PROMPT PARA FRONTEND - Implementación de Imágenes en Importaciones

## 📸 NUEVA FUNCIONALIDAD: Gestión de Imágenes

Se ha agregado la funcionalidad completa para subir, ver y eliminar imágenes en las importaciones. Las imágenes se almacenan en el servidor y se pueden asociar a cualquier importación.

---

## 🔗 ENDPOINTS DE IMÁGENES

### 1. Subir Imagen a una Importación

```
POST /imports/{id}/images
Content-Type: multipart/form-data
```

**Body:**
- `file`: Archivo de imagen (form-data)

**Validaciones:**
- Extensiones permitidas: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Tamaño máximo: 10MB
- Se genera un nombre único automáticamente (UUID)

**Response (201 Created):**
```json
{
  "message": "Imagen subida correctamente",
  "image_url": "/uploads/imports/abc123-xyz.jpg",
  "filename": "abc123-xyz.jpg"
}
```

**Ejemplo de uso (JavaScript):**
```javascript
async function subirImagen(importId, archivo) {
  const formData = new FormData();
  formData.append('file', archivo);
  
  const response = await fetch(`http://localhost:8000/imports/${importId}/images`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Uso
const input = document.querySelector('input[type="file"]');
input.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file) {
    try {
      const result = await subirImagen(importId, file);
      console.log('Imagen subida:', result.image_url);
      // Recargar la importación para ver la nueva imagen
    } catch (error) {
      console.error('Error:', error.message);
    }
  }
});
```

---

### 2. Eliminar Imagen de una Importación

```
DELETE /imports/{id}/images/{filename}
```

**Parámetros:**
- `id`: ID de la importación
- `filename`: Nombre del archivo (ej: "abc123-xyz.jpg")

**Response (200 OK):**
```json
{
  "message": "Imagen eliminada correctamente"
}
```

**Ejemplo de uso:**
```javascript
async function eliminarImagen(importId, imageUrl) {
  // Extraer el filename de la URL
  const filename = imageUrl.split('/').pop(); // "abc123-xyz.jpg"
  
  const response = await fetch(
    `http://localhost:8000/imports/${importId}/images/${filename}`,
    {
      method: 'DELETE'
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}
```

---

### 3. Ver Imágenes

Las imágenes están disponibles directamente mediante su URL:

```
GET /uploads/imports/{filename}
```

**URL completa:**
```
http://localhost:8000/uploads/imports/abc123-xyz.jpg
```

**Nota:** Las imágenes se sirven como archivos estáticos, puedes usarlas directamente en tags `<img>`.

---

## 📋 ESTRUCTURA DE DATOS

### Importación con Imágenes

Cuando obtienes una importación, el campo `images` contiene un array de URLs:

```json
{
  "id": "507f1f77bcf86cd799439013",
  "car_id": "...",
  "client_id": "...",
  "images": [
    "/uploads/imports/abc123-xyz.jpg",
    "/uploads/imports/def456-uvw.png",
    "/uploads/imports/ghi789-rst.webp"
  ],
  "status": "EN_PROCESO",
  ...
}
```

**URL Base:** En producción, reemplaza `http://localhost:8000` con tu URL real.

---

## 🎨 COMPONENTES SUGERIDOS

### 1. Componente: Galería de Imágenes

**Funcionalidad:**
- Mostrar todas las imágenes de una importación
- Permitir eliminar imágenes
- Vista previa de imágenes
- Soporte para múltiples imágenes

**Ejemplo (React):**
```jsx
function GaleriaImagenes({ importacion, onImageDeleted }) {
  const baseUrl = 'http://localhost:8000'; // Cambiar en producción
  
  const handleDelete = async (imageUrl) => {
    if (!confirm('¿Estás seguro de eliminar esta imagen?')) return;
    
    try {
      const filename = imageUrl.split('/').pop();
      await fetch(
        `${baseUrl}/imports/${importacion.id}/images/${filename}`,
        { method: 'DELETE' }
      );
      
      // Notificar al componente padre para recargar
      onImageDeleted();
    } catch (error) {
      alert('Error al eliminar imagen: ' + error.message);
    }
  };
  
  if (!importacion.images || importacion.images.length === 0) {
    return <div>No hay imágenes</div>;
  }
  
  return (
    <div className="galeria-imagenes">
      <h3>Imágenes de la Importación</h3>
      <div className="grid-imagenes">
        {importacion.images.map((imageUrl, index) => (
          <div key={index} className="imagen-item">
            <img 
              src={`${baseUrl}${imageUrl}`} 
              alt={`Imagen ${index + 1}`}
              className="imagen-preview"
            />
            <button 
              onClick={() => handleDelete(imageUrl)}
              className="btn-eliminar"
            >
              Eliminar
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Estilos CSS sugeridos:**
```css
.galeria-imagenes {
  margin: 20px 0;
}

.grid-imagenes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.imagen-item {
  position: relative;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
}

.imagen-preview {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.btn-eliminar {
  width: 100%;
  padding: 8px;
  background: #e74c3c;
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-eliminar:hover {
  background: #c0392b;
}
```

---

### 2. Componente: Subir Imágenes

**Funcionalidad:**
- Input de archivo para seleccionar imágenes
- Validación de tipo y tamaño
- Preview antes de subir
- Indicador de progreso (opcional)
- Soporte para múltiples archivos

**Ejemplo (React):**
```jsx
function SubirImagen({ importId, onImageUploaded }) {
  const [subiendo, setSubiendo] = useState(false);
  const [error, setError] = useState(null);
  const baseUrl = 'http://localhost:8000';
  
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validar tipo de archivo
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Tipo de archivo no permitido. Use: JPG, PNG, GIF o WEBP');
      return;
    }
    
    // Validar tamaño (10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setError('El archivo es demasiado grande. Máximo 10MB');
      return;
    }
    
    setError(null);
    setSubiendo(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${baseUrl}/imports/${importId}/images`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al subir imagen');
      }
      
      const result = await response.json();
      console.log('Imagen subida:', result.image_url);
      
      // Notificar al componente padre
      if (onImageUploaded) {
        onImageUploaded();
      }
      
      // Limpiar input
      event.target.value = '';
      
    } catch (error) {
      setError(error.message);
    } finally {
      setSubiendo(false);
    }
  };
  
  return (
    <div className="subir-imagen">
      <label className="btn-subir">
        {subiendo ? 'Subiendo...' : 'Subir Imagen'}
        <input
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
          onChange={handleFileChange}
          disabled={subiendo}
          style={{ display: 'none' }}
        />
      </label>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}
```

**Estilos CSS:**
```css
.btn-subir {
  display: inline-block;
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-subir:hover {
  background: #2980b9;
}

.btn-subir:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-top: 10px;
  font-size: 14px;
}
```

---

### 3. Componente: Vista Previa de Imagen

**Funcionalidad:**
- Mostrar preview antes de subir
- Validación visual
- Mostrar tamaño del archivo

**Ejemplo:**
```jsx
function PreviewImagen({ file, onRemove }) {
  const [preview, setPreview] = useState(null);
  
  useEffect(() => {
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  }, [file]);
  
  if (!preview) return null;
  
  return (
    <div className="preview-imagen">
      <img src={preview} alt="Preview" />
      <div className="info-archivo">
        <p>{file.name}</p>
        <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
      </div>
      <button onClick={onRemove}>Cancelar</button>
    </div>
  );
}
```

---

### 4. Componente: Subir Múltiples Imágenes

**Funcionalidad:**
- Permitir seleccionar múltiples archivos
- Subir todos a la vez
- Mostrar progreso de cada una

**Ejemplo:**
```jsx
function SubirMultiplesImagenes({ importId, onUploadComplete }) {
  const [archivos, setArchivos] = useState([]);
  const [subiendo, setSubiendo] = useState(false);
  
  const handleFilesSelected = (event) => {
    const files = Array.from(event.target.files);
    setArchivos(files);
  };
  
  const subirTodas = async () => {
    setSubiendo(true);
    const resultados = [];
    
    for (const file of archivos) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(
          `http://localhost:8000/imports/${importId}/images`,
          {
            method: 'POST',
            body: formData
          }
        );
        
        if (response.ok) {
          const result = await response.json();
          resultados.push({ success: true, result });
        } else {
          resultados.push({ success: false, file: file.name });
        }
      } catch (error) {
        resultados.push({ success: false, file: file.name, error });
      }
    }
    
    setSubiendo(false);
    setArchivos([]);
    
    if (onUploadComplete) {
      onUploadComplete(resultados);
    }
  };
  
  return (
    <div>
      <input
        type="file"
        multiple
        accept="image/*"
        onChange={handleFilesSelected}
      />
      {archivos.length > 0 && (
        <div>
          <p>{archivos.length} archivo(s) seleccionado(s)</p>
          <button onClick={subirTodas} disabled={subiendo}>
            {subiendo ? 'Subiendo...' : 'Subir Todas'}
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## 📱 INTEGRACIÓN EN PÁGINAS

### Página: Detalle de Importación (Admin)

**Layout sugerido:**
```
┌─────────────────────────────────────┐
│ Información de Importación           │
│ [Datos básicos]                     │
├─────────────────────────────────────┤
│ Imágenes                             │
│ [Botón Subir Imagen]                │
│ [Galería de Imágenes]               │
├─────────────────────────────────────┤
│ Timeline de Estados                  │
│ [Componente Timeline]                 │
├─────────────────────────────────────┤
│ Costos y otra información...        │
└─────────────────────────────────────┘
```

**Código de ejemplo:**
```jsx
function DetalleImportacion({ importId }) {
  const [importacion, setImportacion] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const cargarImportacion = async () => {
    setLoading(true);
    const response = await fetch(`http://localhost:8000/imports/${importId}`);
    const data = await response.json();
    setImportacion(data);
    setLoading(false);
  };
  
  useEffect(() => {
    cargarImportacion();
  }, [importId]);
  
  const handleImageUploaded = () => {
    cargarImportacion(); // Recargar para ver nueva imagen
  };
  
  if (loading) return <div>Cargando...</div>;
  if (!importacion) return <div>Importación no encontrada</div>;
  
  return (
    <div className="detalle-importacion">
      <h1>Importación #{importacion.id}</h1>
      
      {/* Sección de Imágenes */}
      <section className="seccion-imagenes">
        <h2>Imágenes</h2>
        <SubirImagen 
          importId={importId} 
          onImageUploaded={handleImageUploaded}
        />
        <GaleriaImagenes 
          importacion={importacion}
          onImageDeleted={handleImageUploaded}
        />
      </section>
      
      {/* Otras secciones... */}
    </div>
  );
}
```

---

### Página: Vista de Cliente (URL Compartida)

**Layout sugerido:**
```
┌─────────────────────────────────────┐
│ Tu Importación                       │
│ Estado: EN_TRANSITO                  │
├─────────────────────────────────────┤
│ Galería de Imágenes                 │
│ [Solo lectura - sin botón eliminar]  │
├─────────────────────────────────────┤
│ Progreso                             │
│ [Timeline]                           │
├─────────────────────────────────────┤
│ Costos                               │
│ [Tabla de costos]                    │
└─────────────────────────────────────┘
```

**Código de ejemplo:**
```jsx
function VistaCliente({ token }) {
  const [importacion, setImportacion] = useState(null);
  const baseUrl = 'http://localhost:8000';
  
  useEffect(() => {
    fetch(`${baseUrl}/share/${token}`)
      .then(r => r.json())
      .then(data => setImportacion(data));
  }, [token]);
  
  if (!importacion) return <div>Cargando...</div>;
  
  return (
    <div className="vista-cliente">
      <h1>Tu Importación</h1>
      
      {/* Galería de Imágenes (solo lectura) */}
      {importacion.images && importacion.images.length > 0 && (
        <section className="galeria-cliente">
          <h2>Imágenes de tu Vehículo</h2>
          <div className="grid-imagenes">
            {importacion.images.map((imageUrl, index) => (
              <img
                key={index}
                src={`${baseUrl}${imageUrl}`}
                alt={`Imagen ${index + 1}`}
                className="imagen-cliente"
              />
            ))}
          </div>
        </section>
      )}
      
      {/* Otras secciones... */}
    </div>
  );
}
```

---

## 🔧 FUNCIONES UTILITARIAS

### Construir URL Completa de Imagen

```javascript
function getImageUrl(imagePath, baseUrl = 'http://localhost:8000') {
  // imagePath viene como "/uploads/imports/filename.jpg"
  return `${baseUrl}${imagePath}`;
}

// Uso
const fullUrl = getImageUrl(importacion.images[0]);
// Resultado: "http://localhost:8000/uploads/imports/abc123.jpg"
```

### Validar Archivo Antes de Subir

```javascript
function validarArchivo(file) {
  const errors = [];
  
  // Validar tipo
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    errors.push('Tipo de archivo no permitido. Use: JPG, PNG, GIF o WEBP');
  }
  
  // Validar tamaño (10MB)
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    errors.push('El archivo es demasiado grande. Máximo 10MB');
  }
  
  return {
    valido: errors.length === 0,
    errores: errors
  };
}

// Uso
const validacion = validarArchivo(archivo);
if (!validacion.valido) {
  alert(validacion.errores.join('\n'));
  return;
}
```

### Formatear Tamaño de Archivo

```javascript
function formatearTamaño(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Uso
console.log(formatearTamaño(1024)); // "1 KB"
console.log(formatearTamaño(1048576)); // "1 MB"
```

---

## 🎯 FLUJO COMPLETO DE TRABAJO

### 1. Al Cargar Detalle de Importación:

```javascript
// 1. Obtener importación
const importacion = await fetch(`/imports/${id}`).then(r => r.json());

// 2. Las imágenes están en importacion.images (array de URLs)
// 3. Mostrar galería con las imágenes
```

### 2. Al Subir una Imagen:

```javascript
// 1. Usuario selecciona archivo
// 2. Validar archivo (tipo, tamaño)
// 3. Crear FormData y subir
const formData = new FormData();
formData.append('file', archivo);

const response = await fetch(`/imports/${id}/images`, {
  method: 'POST',
  body: formData
});

// 4. Recargar importación para ver nueva imagen
```

### 3. Al Eliminar una Imagen:

```javascript
// 1. Extraer filename de la URL
const filename = imageUrl.split('/').pop();

// 2. Eliminar
await fetch(`/imports/${id}/images/${filename}`, {
  method: 'DELETE'
});

// 3. Recargar importación
```

---

## ⚠️ VALIDACIONES Y ERRORES

### Errores Comunes:

**400 - Tipo de archivo no permitido:**
```json
{
  "detail": "Tipo de archivo no permitido. Extensiones permitidas: .jpg, .jpeg, .png, .gif, .webp"
}
```

**400 - Archivo demasiado grande:**
```json
{
  "detail": "Archivo demasiado grande. Tamaño máximo: 10.0MB"
}
```

**404 - Importación no encontrada:**
```json
{
  "detail": "Importación no encontrada"
}
```

**404 - Imagen no encontrada:**
```json
{
  "detail": "Imagen no encontrada en esta importación"
}
```

### Manejo de Errores:

```javascript
async function subirImagenSeguro(importId, archivo) {
  try {
    // Validar antes de subir
    const validacion = validarArchivo(archivo);
    if (!validacion.valido) {
      throw new Error(validacion.errores.join(', '));
    }
    
    // Subir
    const formData = new FormData();
    formData.append('file', archivo);
    
    const response = await fetch(`/imports/${importId}/images`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al subir imagen');
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('Error al subir imagen:', error);
    // Mostrar mensaje al usuario
    alert(`Error: ${error.message}`);
    throw error;
  }
}
```

---

## 🎨 CONSIDERACIONES DE UI/UX

### 1. Indicadores Visuales:
- Mostrar spinner mientras se sube
- Mostrar progreso (opcional, con XMLHttpRequest)
- Feedback visual al completar
- Mensajes de error claros

### 2. Preview de Imágenes:
- Mostrar preview antes de subir
- Permitir cancelar antes de subir
- Mostrar tamaño del archivo

### 3. Galería:
- Grid responsivo
- Lightbox para ver imágenes en grande
- Indicador de carga para cada imagen
- Placeholder si no hay imágenes

### 4. Optimización:
- Lazy loading de imágenes
- Thumbnails para listas
- Imágenes optimizadas (considerar compresión en frontend)

---

## 📝 EJEMPLO COMPLETO (React)

```jsx
import React, { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000'; // Cambiar en producción

function GestionImagenes({ importId }) {
  const [importacion, setImportacion] = useState(null);
  const [subiendo, setSubiendo] = useState(false);
  const [error, setError] = useState(null);
  
  // Cargar importación
  useEffect(() => {
    cargarImportacion();
  }, [importId]);
  
  const cargarImportacion = async () => {
    try {
      const response = await fetch(`${API_BASE}/imports/${importId}`);
      const data = await response.json();
      setImportacion(data);
    } catch (error) {
      console.error('Error al cargar importación:', error);
    }
  };
  
  // Subir imagen
  const handleSubir = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validar
    const validacion = validarArchivo(file);
    if (!validacion.valido) {
      setError(validacion.errores.join(', '));
      return;
    }
    
    setError(null);
    setSubiendo(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE}/imports/${importId}/images`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }
      
      await cargarImportacion(); // Recargar
      event.target.value = ''; // Limpiar input
      
    } catch (error) {
      setError(error.message);
    } finally {
      setSubiendo(false);
    }
  };
  
  // Eliminar imagen
  const handleEliminar = async (imageUrl) => {
    if (!confirm('¿Eliminar esta imagen?')) return;
    
    try {
      const filename = imageUrl.split('/').pop();
      const response = await fetch(
        `${API_BASE}/imports/${importId}/images/${filename}`,
        { method: 'DELETE' }
      );
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }
      
      await cargarImportacion(); // Recargar
      
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };
  
  if (!importacion) return <div>Cargando...</div>;
  
  return (
    <div className="gestion-imagenes">
      <h2>Imágenes de la Importación</h2>
      
      {/* Subir */}
      <div className="subir-seccion">
        <label className="btn-subir">
          {subiendo ? 'Subiendo...' : 'Subir Imagen'}
          <input
            type="file"
            accept="image/*"
            onChange={handleSubir}
            disabled={subiendo}
            style={{ display: 'none' }}
          />
        </label>
        {error && <div className="error">{error}</div>}
      </div>
      
      {/* Galería */}
      {importacion.images && importacion.images.length > 0 ? (
        <div className="galeria">
          {importacion.images.map((imageUrl, index) => (
            <div key={index} className="imagen-item">
              <img 
                src={`${API_BASE}${imageUrl}`}
                alt={`Imagen ${index + 1}`}
              />
              <button onClick={() => handleEliminar(imageUrl)}>
                Eliminar
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p>No hay imágenes. Sube la primera imagen.</p>
      )}
    </div>
  );
}

function validarArchivo(file) {
  const errors = [];
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  
  if (!allowedTypes.includes(file.type)) {
    errors.push('Tipo no permitido');
  }
  
  if (file.size > 10 * 1024 * 1024) {
    errors.push('Archivo muy grande (máx 10MB)');
  }
  
  return {
    valido: errors.length === 0,
    errores: errors
  };
}

export default GestionImagenes;
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Funcionalidades Básicas:
- [ ] Componente para subir imágenes
- [ ] Componente para mostrar galería
- [ ] Componente para eliminar imágenes
- [ ] Validación de tipo y tamaño de archivo
- [ ] Manejo de errores

### UI/UX:
- [ ] Preview de imágenes antes de subir
- [ ] Indicador de carga al subir
- [ ] Mensajes de error claros
- [ ] Galería responsiva
- [ ] Lightbox para ver imágenes en grande (opcional)

### Integración:
- [ ] Integrar en página de detalle de importación (admin)
- [ ] Integrar en vista pública de cliente
- [ ] Actualizar lista de importaciones (opcional: mostrar primera imagen)
- [ ] Configurar URL base para producción

### Optimización:
- [ ] Lazy loading de imágenes
- [ ] Thumbnails para listas
- [ ] Compresión de imágenes antes de subir (opcional)

---

## 🔗 URL BASE PARA PRODUCCIÓN

**Importante:** Configura la URL base como variable de entorno:

```javascript
// config.js
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Uso
const imageUrl = `${API_BASE_URL}${importacion.images[0]}`;
```

---

## 📝 NOTAS IMPORTANTES

1. **URLs de imágenes:** Las URLs son relativas (`/uploads/imports/...`), necesitas agregar la URL base del servidor.

2. **CORS:** Ya está configurado en el backend para permitir subida de archivos.

3. **Tamaño máximo:** 10MB por imagen. Considera comprimir imágenes grandes en el frontend antes de subir.

4. **Múltiples imágenes:** Puedes subir múltiples imágenes, pero una a la vez. Para subir varias, haz múltiples requests o implementa un componente de subida múltiple.

5. **Eliminación:** Al eliminar una imagen, se elimina tanto del servidor como de la base de datos.

6. **Disponibilidad:** Las imágenes están disponibles para clientes en URLs compartidas.

---

## 🚀 PRÓXIMOS PASOS

1. Implementar componente de subida
2. Implementar galería de imágenes
3. Integrar en páginas de detalle
4. Agregar validaciones y manejo de errores
5. Optimizar carga de imágenes
6. Probar con diferentes tipos y tamaños de archivo

---

**¿Preguntas?** Revisa la documentación en `/docs` o consulta con el equipo de backend.

