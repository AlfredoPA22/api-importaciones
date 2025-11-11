# Prompt para Integración Frontend - Sistema de Importaciones API

## Contexto
Necesito que integres este sistema de importaciones con el frontend. La API está desarrollada en FastAPI y utiliza MongoDB. El sistema permite gestionar autos, clientes, importaciones con costos duales (reales y para cliente), y URLs compartidas para que los clientes vean sus importaciones.

## URL Base
```
http://localhost:8000
```
(En producción cambiar a la URL correspondiente)

## Documentación Interactiva
La API incluye documentación automática de Swagger/OpenAPI en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints Disponibles

### 1. AUTOS (`/cars`)

#### Listar todos los autos
```
GET /cars
```
**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "model": "Camry",
    "brand": "Toyota",
    "year": 2023,
    "sale_price": 30000,
    "color": "Blanco",
    "vin": "123456789",
    "description": "Auto de lujo"
  }
]
```

#### Crear auto
```
POST /cars
```
**Body:**
```json
{
  "model": "Camry",
  "brand": "Toyota",
  "year": 2023,
  "sale_price": 30000,
  "color": "Blanco",
  "vin": "123456789",
  "description": "Auto de lujo"
}
```
**Response:** Auto creado (mismo formato que listar)

#### Obtener auto por ID
```
GET /cars/{id}
```
**Response:** Objeto de auto individual

#### Editar auto
```
PUT /cars/{id}
```
**Body:** (todos los campos son opcionales)
```json
{
  "model": "Camry Updated",
  "sale_price": 32000
}
```
**Response:** Auto actualizado

#### Eliminar auto
```
DELETE /cars/{id}
```
**Response:** 204 No Content

---

### 2. CLIENTES (`/clients`)

#### Listar todos los clientes
```
GET /clients
```
**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "+1234567890",
    "address": "Calle 123",
    "company": "Empresa XYZ",
    "notes": "Cliente VIP",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Crear cliente
```
POST /clients
```
**Body:**
```json
{
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "phone": "+1234567890",
  "address": "Calle 123",
  "company": "Empresa XYZ",
  "notes": "Cliente VIP"
}
```
**Nota:** Todos los campos excepto `name` son opcionales.

#### Obtener cliente por ID
```
GET /clients/{id}
```
**Response:** Objeto de cliente individual

#### Editar cliente
```
PUT /clients/{id}
```
**Body:** (todos los campos son opcionales)
```json
{
  "email": "nuevo@example.com",
  "phone": "+9876543210"
}
```

#### Eliminar cliente
```
DELETE /clients/{id}
```
**Response:** 204 No Content

---

### 3. IMPORTACIONES (`/imports`)

#### Listar todas las importaciones
```
GET /imports
```
**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439013",
    "car_id": "507f1f77bcf86cd799439011",
    "client_id": "507f1f77bcf86cd799439012",
    "costos_reales": {
      "flete_real": 1500.50,
      "seguro_real": 800.00
    },
    "costos_cliente": {
      "flete": 1800.00,
      "seguro": 1000.00
    },
    "notes": "Importación desde Japón",
    "status": "EN_PROCESO",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Crear importación
```
POST /imports
```
**Body:**
```json
{
  "car_id": "507f1f77bcf86cd799439011",
  "client_id": "507f1f77bcf86cd799439012",
  "costos_reales": {
    "flete_real": 1500.50,
    "seguro_real": 800.00,
    "aduana_real": 2500.75
  },
  "costos_cliente": {
    "flete": 1800.00,
    "seguro": 1000.00,
    "aduana": 3000.00,
    "transporte_local": 300.00
  },
  "notes": "Importación desde Japón",
  "status": "EN_PROCESO"
}
```
**Nota:** 
- `car_id` y `client_id` son obligatorios
- `costos_reales` y `costos_cliente` son diccionarios dinámicos (puedes agregar cualquier campo)
- `status` puede ser: `EN_PROCESO`, `EN_TRANSITO`, `EN_TALLER`, `EN_ADUANA`, `ENTREGADO`

**Response:** Importación creada con información del auto y cliente incluida

#### Obtener importación por ID
```
GET /imports/{id}
```
**Response:** Importación con información del auto y cliente incluida

#### Editar importación
```
PUT /imports/{id}
```
**Body:** (todos los campos son opcionales)
```json
{
  "costos_reales": {
    "impuestos_real": 1200.00
  },
  "costos_cliente": {
    "impuestos": 1500.00,
    "almacenamiento": 150.00
  },
  "notes": "Notas actualizadas",
  "status": "EN_TRANSITO"
}
```
**Nota:** Los costos se fusionan con los existentes (no se reemplazan). Puedes agregar nuevos campos o actualizar existentes.

#### Eliminar importación
```
DELETE /imports/{id}
```
**Response:** 204 No Content

#### Obtener importaciones por auto
```
GET /imports/car/{car_id}
```
**Response:** Lista de importaciones para ese auto

#### Obtener importaciones por cliente
```
GET /imports/client/{client_id}
```
**Response:** Lista de importaciones para ese cliente

---

### 4. COMPARTIR IMPORTACIONES (`/imports/{import_id}/share` y `/share/{token}`)

#### Generar URL compartida
```
POST /imports/{import_id}/share
```
**Body (opcional):**
```json
{
  "days_valid": 365
}
```
O sin body (usa 365 días por defecto):
```
POST /imports/{import_id}/share
```

**Response:**
```json
{
  "token": "abc123xyz...",
  "share_url": "http://localhost:8000/share/abc123xyz...",
  "expires_at": "2025-12-31T23:59:59",
  "is_active": true,
  "import_id": "507f1f77bcf86cd799439013"
}
```

**Nota:** Si ya existe un token activo, se desactiva automáticamente y se crea uno nuevo.

#### Ver importación por token (PÚBLICO - Para clientes)
```
GET /share/{token}
```
**Response:**
```json
{
  "id": "507f1f77bcf86cd799439013",
  "car_id": "507f1f77bcf86cd799439011",
  "client_id": "507f1f77bcf86cd799439012",
  "costos_cliente": {
    "flete": 1800.00,
    "seguro": 1000.00,
    "aduana": 3000.00
  },
  "notes": "Importación desde Japón",
  "status": "EN_PROCESO",
  "car": {
    "id": "507f1f77bcf86cd799439011",
    "model": "Camry",
    "brand": "Toyota",
    "year": 2023,
    "sale_price": 30000
  },
  "client": {
    "id": "507f1f77bcf86cd799439012",
    "name": "Juan Pérez",
    "company": "Empresa XYZ"
  }
}
```
**IMPORTANTE:** Este endpoint NO muestra `costos_reales`, solo `costos_cliente`. Es el endpoint que deben usar los clientes.

#### Listar tokens de una importación
```
GET /imports/{import_id}/share
```
**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439014",
    "import_id": "507f1f77bcf86cd799439013",
    "token": "abc123xyz...",
    "share_url": "http://localhost:8000/share/abc123xyz...",
    "expires_at": "2025-12-31T23:59:59",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### Desactivar token
```
DELETE /imports/{import_id}/share/{token}
```
**Response:**
```json
{
  "message": "Token desactivado correctamente"
}
```

---

## Estados de Importación (Status)
Los estados disponibles son:
- `EN_PROCESO`: En proceso
- `EN_TRANSITO`: En tránsito
- `EN_TALLER`: En taller
- `EN_ADUANA`: En aduana
- `ENTREGADO`: Entregado

## Manejo de Errores

### Errores Comunes:
- **400 Bad Request**: ID inválido o datos incorrectos
- **404 Not Found**: Recurso no encontrado
- **403 Forbidden**: Token desactivado o expirado

### Formato de Error:
```json
{
  "detail": "Mensaje de error descriptivo"
}
```

## Características Importantes

### 1. Costos Duales
- **costos_reales**: Solo visibles para administradores (no se muestran en URLs compartidas)
- **costos_cliente**: Visibles para clientes a través de URLs compartidas
- Ambos son diccionarios dinámicos: puedes agregar cualquier campo y valor numérico

### 2. URLs Compartidas
- Cada importación puede tener una URL única generada por el administrador
- Los clientes acceden a través de `/share/{token}` sin autenticación
- Solo ven `costos_cliente`, no `costos_reales`
- Los tokens pueden expirar y desactivarse

### 3. Actualización de Costos
- Los costos se fusionan (merge), no se reemplazan
- Puedes agregar nuevos campos o actualizar existentes
- Ejemplo: Si existe `{"flete": 1000}` y envías `{"flete": 1500, "seguro": 800}`, el resultado será `{"flete": 1500, "seguro": 800}`

## Flujo de Trabajo Sugerido

### Para Administradores:
1. Crear cliente: `POST /clients`
2. Crear auto: `POST /cars`
3. Crear importación: `POST /imports` (con `car_id`, `client_id`, `costos_reales`, `costos_cliente`)
4. Actualizar costos según avance: `PUT /imports/{id}` (agregar más costos)
5. Generar URL compartida: `POST /imports/{import_id}/share`
6. Compartir URL con cliente

### Para Clientes:
1. Recibir URL compartida del administrador
2. Acceder a: `GET /share/{token}`
3. Ver información de su importación, auto y costos (solo `costos_cliente`)

## Ejemplos de Integración

### Ejemplo 1: Crear importación completa
```javascript
// 1. Crear cliente
const client = await fetch('/clients', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Juan Pérez',
    email: 'juan@example.com'
  })
});

// 2. Crear auto
const car = await fetch('/cars', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'Camry',
    brand: 'Toyota',
    year: 2023,
    sale_price: 30000
  })
});

// 3. Crear importación
const importation = await fetch('/imports', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    car_id: car.id,
    client_id: client.id,
    costos_reales: {
      flete_real: 1500.50,
      seguro_real: 800.00
    },
    costos_cliente: {
      flete: 1800.00,
      seguro: 1000.00
    },
    status: 'EN_PROCESO'
  })
});

// 4. Generar URL compartida
const share = await fetch(`/imports/${importation.id}/share`, {
  method: 'POST'
});
// Compartir share.share_url con el cliente
```

### Ejemplo 2: Agregar más costos
```javascript
// Agregar más costos a una importación existente
await fetch(`/imports/${importId}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    costos_reales: {
      impuestos_real: 1200.00
    },
    costos_cliente: {
      impuestos: 1500.00,
      almacenamiento: 150.00
    }
  })
});
```

### Ejemplo 3: Vista de cliente (pública)
```javascript
// El cliente accede a su importación mediante el token
const importation = await fetch(`/share/${token}`);
// Solo verá costos_cliente, no costos_reales
```

## Consideraciones de UI/UX

### Páginas Sugeridas:

1. **Dashboard Administrador:**
   - Lista de importaciones
   - Filtros por cliente, auto, estado
   - Acciones: crear, editar, ver, compartir

2. **Gestión de Clientes:**
   - Lista de clientes
   - Formulario crear/editar cliente
   - Ver importaciones de cada cliente

3. **Gestión de Autos:**
   - Lista de autos
   - Formulario crear/editar auto
   - Ver importaciones de cada auto

4. **Detalle de Importación:**
   - Información completa (solo admin)
   - Costos reales y costos cliente
   - Botón para generar/compartir URL
   - Historial de actualizaciones

5. **Vista de Cliente (Pública):**
   - Acceso mediante URL compartida
   - Solo muestra costos_cliente
   - Información del auto
   - Estado de la importación
   - Diseño limpio y profesional

### Componentes Sugeridos:

1. **Formulario de Costos Dinámicos:**
   - Permite agregar/editar campos de costo dinámicamente
   - Separación visual entre costos_reales y costos_cliente
   - Validación de valores numéricos

2. **Selector de Estado:**
   - Dropdown con los estados disponibles
   - Cambio de color según estado
   - Badge visual del estado actual

3. **Generador de URLs Compartidas:**
   - Botón para generar URL
   - Mostrar URL generada
   - Opción de copiar al portapapeles
   - Opción de desactivar token

4. **Vista de Costos:**
   - Tabla con costos
   - Cálculo de totales
   - Formato de moneda
   - Diferencia visual entre costos reales y cliente (solo admin)

## Notas Técnicas

- Todos los IDs son strings de MongoDB ObjectId
- Las fechas están en formato ISO 8601
- Los costos son números flotantes (float)
- No hay autenticación implementada (agregar según necesidades)
- La URL base debe ser configurable (variable de entorno)
- Manejar errores de red y validación
- Implementar loading states
- Considerar paginación para listas grandes

## Testing

Puedes probar todos los endpoints usando:
- Swagger UI: `http://localhost:8000/docs`
- Postman/Insomnia
- curl
- Cualquier cliente HTTP

## Soporte

Para cualquier duda sobre la API, revisa la documentación en `/docs` o contacta al equipo de backend.

---

**IMPORTANTE:** Este prompt contiene toda la información necesaria para integrar el frontend. Asegúrate de:
1. Manejar los errores apropiadamente
2. Validar los datos antes de enviar
3. Mostrar estados de carga
4. Implementar una buena UX para el manejo de costos dinámicos
5. Crear una vista pública atractiva para los clientes

