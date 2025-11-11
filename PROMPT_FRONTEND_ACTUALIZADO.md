# PROMPT PARA FRONTEND - ACTUALIZACIÓN: Historial de Estados y Fecha Tentativa de Entrega

## 🆕 NUEVAS FUNCIONALIDADES

Se han agregado dos funcionalidades importantes al sistema:

### 1. **Historial de Estados (Timeline)**
- Cada cambio de estado se registra automáticamente con fecha y hora
- Permite mostrar una línea de tiempo visual de los avances de la importación
- Disponible para administradores y clientes (en URLs compartidas)

### 2. **Fecha Tentativa de Entrega**
- Campo para establecer la fecha tentativa de entrega del vehículo
- Permite mostrar un contador de días restantes hasta la entrega
- Disponible en todas las vistas de importación

---

## 📋 CAMBIOS EN ENDPOINTS

### Endpoint Nuevo: Obtener Historial de Estados

```
GET /imports/{id}/history
```

**Response:**
```json
{
  "import_id": "507f1f77bcf86cd799439013",
  "current_status": "EN_TRANSITO",
  "fecha_tentativa_entrega": "2024-02-15T00:00:00Z",
  "history": [
    {
      "status": "EN_PROCESO",
      "changed_at": "2024-01-10T08:00:00Z",
      "notes": "Importación creada"
    },
    {
      "status": "EN_TRANSITO",
      "changed_at": "2024-01-15T10:30:00Z",
      "notes": "Cambio de estado de EN_PROCESO a EN_TRANSITO"
    },
    {
      "status": "EN_ADUANA",
      "changed_at": "2024-01-20T14:15:00Z",
      "notes": "Cambio de estado de EN_TRANSITO a EN_ADUANA"
    }
  ]
}
```

**Notas:**
- El historial está ordenado cronológicamente (más antiguo primero)
- Cada entrada incluye: `status`, `changed_at` (fecha/hora), `notes` (descripción)
- El historial se genera automáticamente cuando cambia el estado

---

### Endpoint Actualizado: Crear Importación

```
POST /imports
```

**Body actualizado:**
```json
{
  "car_id": "507f1f77bcf86cd799439011",
  "client_id": "507f1f77bcf86cd799439012",
  "costos_reales": {...},
  "costos_cliente": {...},
  "fecha_tentativa_entrega": "2024-02-15T00:00:00Z",  // ⬅️ NUEVO
  "status": "EN_PROCESO",
  "notes": "..."
}
```

**Response incluye:**
- `fecha_tentativa_entrega`: Fecha establecida
- `status_history`: Array con el primer registro del historial

---

### Endpoint Actualizado: Actualizar Importación

```
PUT /imports/{id}
```

**Body actualizado:**
```json
{
  "status": "EN_TRANSITO",  // ⬅️ Se registra automáticamente en historial
  "fecha_tentativa_entrega": "2024-02-20T00:00:00Z",  // ⬅️ NUEVO
  "costos_reales": {...},
  "costos_cliente": {...},
  ...
}
```

**Comportamiento:**
- Si cambias el `status`, se registra automáticamente en el historial
- Si actualizas `fecha_tentativa_entrega`, se actualiza la fecha
- El historial se genera automáticamente, no necesitas enviarlo

---

### Endpoint Actualizado: Obtener Importación

```
GET /imports/{id}
```

**Response actualizado:**
```json
{
  "id": "507f1f77bcf86cd799439013",
  "car_id": "...",
  "client_id": "...",
  "status": "EN_TRANSITO",
  "fecha_tentativa_entrega": "2024-02-15T00:00:00Z",  // ⬅️ NUEVO
  "status_history": [  // ⬅️ NUEVO
    {
      "status": "EN_PROCESO",
      "changed_at": "2024-01-10T08:00:00Z",
      "notes": "Importación creada"
    },
    {
      "status": "EN_TRANSITO",
      "changed_at": "2024-01-15T10:30:00Z",
      "notes": "Cambio de estado de EN_PROCESO a EN_TRANSITO"
    }
  ],
  "costos_reales": {...},
  "costos_cliente": {...},
  "car": {...},
  "client": {...}
}
```

---

### Endpoint Actualizado: Vista Pública (URL Compartida)

```
GET /share/{token}
```

**Response actualizado:**
```json
{
  "id": "...",
  "status": "EN_TRANSITO",
  "fecha_tentativa_entrega": "2024-02-15T00:00:00Z",  // ⬅️ NUEVO (visible para cliente)
  "status_history": [...],  // ⬅️ NUEVO (visible para cliente)
  "costos_cliente": {...},
  "car": {...},
  "client": {...}
}
```

**Nota:** Los clientes pueden ver el historial y la fecha tentativa de entrega en su vista pública.

---

## 🎨 COMPONENTES SUGERIDOS PARA EL FRONTEND

### 1. Componente: Timeline de Estados

**Funcionalidad:**
- Mostrar una línea de tiempo vertical con todos los cambios de estado
- Cada estado debe mostrar: nombre del estado, fecha/hora, y notas
- Indicar visualmente el estado actual
- Usar iconos o colores diferentes para cada estado

**Datos necesarios:**
```javascript
// Obtener historial
const response = await fetch(`/imports/${importId}/history`);
const { history, current_status, fecha_tentativa_entrega } = await response.json();

// history es un array ordenado cronológicamente
history.forEach((entry, index) => {
  // entry.status: estado
  // entry.changed_at: fecha/hora
  // entry.notes: descripción
});
```

**Ejemplo de estructura visual:**
```
┌─────────────────────────────────┐
│ ● EN_PROCESO                    │
│   10 Ene 2024, 08:00            │
│   "Importación creada"          │
├─────────────────────────────────┤
│ ● EN_TRANSITO (Actual)          │
│   15 Ene 2024, 10:30            │
│   "Cambio de estado..."          │
├─────────────────────────────────┤
│ ○ EN_ADUANA                     │
│   20 Ene 2024, 14:15            │
│   "Cambio de estado..."          │
└─────────────────────────────────┘
```

**Estados disponibles:**
- `EN_PROCESO` - En proceso
- `EN_TRANSITO` - En tránsito
- `EN_TALLER` - En taller
- `EN_ADUANA` - En aduana
- `ENTREGADO` - Entregado

---

### 2. Componente: Contador de Días hasta Entrega

**Funcionalidad:**
- Mostrar días restantes hasta la fecha tentativa de entrega
- Cambiar color según proximidad (verde: lejos, amarillo: cerca, rojo: próximo)
- Mostrar fecha completa formateada
- Manejar casos donde la fecha ya pasó (mostrar "Atrasado X días")

**Cálculo de días:**
```javascript
function calcularDiasRestantes(fechaTentativa) {
  if (!fechaTentativa) return null;
  
  const fechaEntrega = new Date(fechaTentativa);
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  fechaEntrega.setHours(0, 0, 0, 0);
  
  const diferencia = fechaEntrega - hoy;
  const dias = Math.ceil(diferencia / (1000 * 60 * 60 * 24));
  
  return dias;
}

// Uso
const diasRestantes = calcularDiasRestantes(importacion.fecha_tentativa_entrega);

if (diasRestantes === null) {
  // No hay fecha establecida
} else if (diasRestantes < 0) {
  // Atrasado: mostrar "Atrasado X días"
} else if (diasRestantes === 0) {
  // Hoy es la fecha
} else {
  // Mostrar "X días restantes"
}
```

**Ejemplo visual:**
```
┌─────────────────────────────┐
│ 📅 Fecha Tentativa          │
│ 15 Febrero 2024             │
│                             │
│ ⏰ 25 días restantes         │
│ (o "Atrasado 5 días")       │
└─────────────────────────────┘
```

**Colores sugeridos:**
- Verde: > 30 días
- Amarillo: 7-30 días
- Naranja: 1-7 días
- Rojo: 0 días o atrasado

---

### 3. Componente: Selector de Fecha Tentativa

**Funcionalidad:**
- Input de fecha para establecer/actualizar la fecha tentativa
- Validar que la fecha sea futura (o permitir fechas pasadas si es necesario)
- Mostrar calendario visual
- Actualizar automáticamente el contador al cambiar la fecha

**Ejemplo:**
```javascript
// Formulario de actualización
const actualizarFechaEntrega = async (importId, nuevaFecha) => {
  await fetch(`/imports/${importId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      fecha_tentativa_entrega: nuevaFecha.toISOString()
    })
  });
};
```

---

## 📱 PÁGINAS ACTUALIZADAS

### 1. Detalle de Importación (Admin)

**Nuevos elementos a mostrar:**
- ✅ Timeline de estados (componente completo)
- ✅ Contador de días hasta entrega
- ✅ Campo para editar fecha tentativa de entrega
- ✅ Historial completo visible

**Layout sugerido:**
```
┌─────────────────────────────────────┐
│ Información de Importación           │
│ Status: EN_TRANSITO                  │
│ Fecha Tentativa: 15 Feb 2024        │
│ ⏰ 25 días restantes                 │
├─────────────────────────────────────┤
│ Timeline de Estados                  │
│ [Componente Timeline aquí]           │
├─────────────────────────────────────┤
│ Costos y otra información...        │
└─────────────────────────────────────┘
```

---

### 2. Vista de Cliente (URL Compartida)

**Nuevos elementos a mostrar:**
- ✅ Timeline de estados (solo lectura)
- ✅ Contador de días hasta entrega
- ✅ Fecha tentativa de entrega (solo lectura)

**Layout sugerido:**
```
┌─────────────────────────────────────┐
│ Tu Importación                       │
│ Estado Actual: EN_TRANSITO           │
│ Fecha Tentativa: 15 Feb 2024        │
│ ⏰ 25 días restantes                 │
├─────────────────────────────────────┤
│ Progreso de tu Importación           │
│ [Timeline visual aquí]               │
├─────────────────────────────────────┤
│ Costos                               │
│ [Tabla de costos aquí]               │
└─────────────────────────────────────┘
```

---

### 3. Lista de Importaciones

**Nuevos elementos a mostrar:**
- ✅ Badge con días restantes (opcional, en tarjeta)
- ✅ Estado actual con indicador visual

**Ejemplo de tarjeta:**
```
┌─────────────────────────────┐
│ Importación #123             │
│ Auto: Toyota Camry           │
│ Estado: EN_TRANSITO          │
│ ⏰ 25 días restantes          │
│ [Ver detalles]               │
└─────────────────────────────┘
```

---

## 🔧 FUNCIONES UTILITARIAS SUGERIDAS

### Formatear Fecha
```javascript
function formatearFecha(fechaISO) {
  const fecha = new Date(fechaISO);
  return fecha.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}
// Resultado: "15 de febrero de 2024"
```

### Formatear Fecha y Hora
```javascript
function formatearFechaHora(fechaISO) {
  const fecha = new Date(fechaISO);
  return fecha.toLocaleString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
// Resultado: "15 feb 2024, 10:30"
```

### Obtener Nombre del Estado
```javascript
const nombresEstados = {
  'EN_PROCESO': 'En Proceso',
  'EN_TRANSITO': 'En Tránsito',
  'EN_TALLER': 'En Taller',
  'EN_ADUANA': 'En Aduana',
  'ENTREGADO': 'Entregado'
};

function obtenerNombreEstado(codigo) {
  return nombresEstados[codigo] || codigo;
}
```

### Obtener Color del Estado
```javascript
const coloresEstados = {
  'EN_PROCESO': '#3498db',    // Azul
  'EN_TRANSITO': '#f39c12',   // Naranja
  'EN_TALLER': '#9b59b6',     // Morado
  'EN_ADUANA': '#e74c3c',     // Rojo
  'ENTREGADO': '#27ae60'      // Verde
};

function obtenerColorEstado(codigo) {
  return coloresEstados[codigo] || '#95a5a6';
}
```

---

## 📊 FLUJO DE TRABAJO SUGERIDO

### Al Cargar Detalle de Importación:

1. **Obtener datos de la importación:**
   ```javascript
   const importacion = await fetch(`/imports/${id}`).then(r => r.json());
   ```

2. **Obtener historial completo:**
   ```javascript
   const historial = await fetch(`/imports/${id}/history`).then(r => r.json());
   ```

3. **Mostrar información:**
   - Estado actual
   - Fecha tentativa y contador
   - Timeline con historial

### Al Cambiar Estado:

1. **Actualizar estado:**
   ```javascript
   await fetch(`/imports/${id}`, {
     method: 'PUT',
     body: JSON.stringify({ status: 'EN_TRANSITO' })
   });
   ```

2. **El backend automáticamente:**
   - Registra el cambio en el historial
   - Actualiza el estado
   - Genera la nota descriptiva

3. **Refrescar datos:**
   - Recargar la importación
   - Recargar el historial
   - Actualizar la UI

### Al Establecer/Actualizar Fecha Tentativa:

1. **Actualizar fecha:**
   ```javascript
   await fetch(`/imports/${id}`, {
     method: 'PUT',
     body: JSON.stringify({
       fecha_tentativa_entrega: nuevaFecha.toISOString()
     })
   });
   ```

2. **Actualizar contador:**
   - Recalcular días restantes
   - Actualizar visualización
   - Cambiar color si es necesario

---

## 🎯 EJEMPLOS DE IMPLEMENTACIÓN

### Ejemplo 1: Timeline Component (React)

```jsx
function TimelineEstados({ historial, estadoActual }) {
  return (
    <div className="timeline">
      {historial.map((entry, index) => (
        <div 
          key={index} 
          className={`timeline-item ${entry.status === estadoActual ? 'active' : ''}`}
        >
          <div className="timeline-marker" style={{ 
            backgroundColor: obtenerColorEstado(entry.status) 
          }} />
          <div className="timeline-content">
            <h4>{obtenerNombreEstado(entry.status)}</h4>
            <p>{formatearFechaHora(entry.changed_at)}</p>
            <p className="notes">{entry.notes}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Ejemplo 2: Contador de Días (React)

```jsx
function ContadorEntrega({ fechaTentativa }) {
  const diasRestantes = calcularDiasRestantes(fechaTentativa);
  
  if (!fechaTentativa) {
    return <div>No hay fecha tentativa establecida</div>;
  }
  
  const getColor = () => {
    if (diasRestantes < 0) return 'red';
    if (diasRestantes === 0) return 'orange';
    if (diasRestantes <= 7) return 'orange';
    if (diasRestantes <= 30) return 'yellow';
    return 'green';
  };
  
  return (
    <div className="contador-entrega" style={{ color: getColor() }}>
      <h3>Fecha Tentativa: {formatearFecha(fechaTentativa)}</h3>
      {diasRestantes < 0 ? (
        <p>Atrasado {Math.abs(diasRestantes)} días</p>
      ) : diasRestantes === 0 ? (
        <p>Entrega programada para hoy</p>
      ) : (
        <p>{diasRestantes} días restantes</p>
      )}
    </div>
  );
}
```

### Ejemplo 3: Actualizar Fecha (JavaScript)

```javascript
async function actualizarFechaEntrega(importId, nuevaFecha) {
  try {
    const response = await fetch(`/imports/${importId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        fecha_tentativa_entrega: nuevaFecha.toISOString()
      })
    });
    
    if (response.ok) {
      const updated = await response.json();
      // Actualizar UI con nueva fecha
      actualizarContador(updated.fecha_tentativa_entrega);
    }
  } catch (error) {
    console.error('Error al actualizar fecha:', error);
  }
}
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Para Administradores:
- [ ] Mostrar timeline de estados en detalle de importación
- [ ] Mostrar contador de días hasta entrega
- [ ] Permitir editar fecha tentativa de entrega
- [ ] Mostrar historial completo al cambiar estados
- [ ] Actualizar timeline automáticamente al cambiar estado

### Para Clientes (URL Compartida):
- [ ] Mostrar timeline de estados (solo lectura)
- [ ] Mostrar contador de días hasta entrega
- [ ] Mostrar fecha tentativa formateada
- [ ] Diseño atractivo y fácil de entender

### Funcionalidades Generales:
- [ ] Formatear fechas correctamente
- [ ] Manejar casos sin fecha tentativa
- [ ] Manejar fechas pasadas (atrasadas)
- [ ] Actualizar contador en tiempo real
- [ ] Validar fechas al establecer/actualizar

---

## 📝 NOTAS IMPORTANTES

1. **El historial se genera automáticamente:** No necesitas enviar el historial al backend, se crea solo cuando cambia el estado.

2. **Orden del historial:** El historial viene ordenado cronológicamente (más antiguo primero), perfecto para mostrar en timeline.

3. **Fecha tentativa opcional:** La fecha tentativa es opcional, maneja el caso donde no esté establecida.

4. **Disponible en URLs compartidas:** Los clientes pueden ver el historial y la fecha tentativa en su vista pública.

5. **Formato de fechas:** Todas las fechas vienen en formato ISO 8601 (ej: "2024-02-15T00:00:00Z"), úsalas con `new Date()` en JavaScript.

---

## 🚀 PRÓXIMOS PASOS

1. Implementar componente de Timeline
2. Implementar componente de Contador de Días
3. Agregar campo de fecha tentativa en formularios
4. Actualizar vistas de detalle de importación
5. Actualizar vista pública de clientes
6. Probar flujo completo de cambio de estados
7. Probar establecimiento de fechas tentativas

---

**¿Preguntas?** Revisa la documentación en `/docs` o consulta con el equipo de backend.

