# Sistema de Importaciones API

API REST desarrollada con FastAPI para gestionar autos, clientes, importaciones con costos dinámicos y URLs compartidas.

## Características

- ✅ Gestión de autos (CRUD)
- ✅ Gestión de clientes (CRUD)
- ✅ Gestión de importaciones con costos duales (reales y para cliente)
- ✅ Sistema de URLs compartidas para que los clientes vean sus importaciones
- ✅ Validación de integridad de datos (un auto solo puede tener una importación)
- ✅ Validación de eliminación (no se pueden eliminar autos/clientes con importaciones asociadas)

## Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **MongoDB**: Base de datos NoSQL
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

## Instalación

### Requisitos previos

- Python 3.8+
- MongoDB (local o remoto)

### Pasos de instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/AlfredoPA22/api-importaciones.git
cd api-importaciones
```

2. Crear un entorno virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la conexión a MongoDB:
   - Editar `config/db.py` con tu cadena de conexión de MongoDB
   - O configurar la variable de entorno `MONGODB_URL`

5. Ejecutar el servidor:
```bash
uvicorn app:app --reload
```

La API estará disponible en: `http://localhost:8000`

## Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints principales

### Autos
- `GET /cars` - Listar autos
- `POST /cars` - Crear auto
- `GET /cars/{id}` - Obtener auto por ID
- `PUT /cars/{id}` - Actualizar auto
- `DELETE /cars/{id}` - Eliminar auto

### Clientes
- `GET /clients` - Listar clientes
- `POST /clients` - Crear cliente
- `GET /clients/{id}` - Obtener cliente por ID
- `PUT /clients/{id}` - Actualizar cliente
- `DELETE /clients/{id}` - Eliminar cliente

### Importaciones
- `GET /imports` - Listar importaciones
- `POST /imports` - Crear importación
- `GET /imports/{id}` - Obtener importación por ID
- `PUT /imports/{id}` - Actualizar importación
- `DELETE /imports/{id}` - Eliminar importación
- `GET /imports/car/{car_id}` - Obtener importación por auto
- `GET /imports/client/{client_id}` - Obtener importaciones por cliente

### Compartir
- `POST /imports/{import_id}/share` - Generar URL compartida
- `GET /share/{token}` - Ver importación por token (público)
- `GET /imports/{import_id}/share` - Listar tokens de una importación
- `DELETE /imports/{import_id}/share/{token}` - Desactivar token

## Características especiales

### Costos duales
- **costos_reales**: Costos internos (solo administrador)
- **costos_cliente**: Costos visibles para el cliente

### URLs compartidas
- Los administradores pueden generar URLs únicas para cada importación
- Los clientes pueden ver sus importaciones sin autenticación mediante el token
- Los clientes solo ven `costos_cliente`, no `costos_reales`

### Validaciones
- Un auto solo puede pertenecer a una importación
- No se pueden eliminar autos/clientes con importaciones asociadas

## Estructura del proyecto

```
api-importaciones/
├── app.py                 # Aplicación principal
├── config/
│   └── db.py             # Configuración de MongoDB
├── models/               # Modelos de datos (Pydantic)
│   ├── car.py
│   ├── client.py
│   ├── importation.py
│   └── share_token.py
├── routes/               # Rutas/endpoints
│   ├── car.py
│   ├── client.py
│   ├── importation.py
│   └── share.py
├── schemas/              # Schemas de serialización
│   ├── car.py
│   ├── client.py
│   ├── importation.py
│   └── share_token.py
├── utils/                # Utilidades
│   └── statusEnum.py
└── requirements.txt      # Dependencias
```

## Variables de entorno

Puedes configurar las siguientes variables de entorno:

- `MONGODB_URL`: URL de conexión a MongoDB (opcional, por defecto usa la configurada en `config/db.py`)

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Autor

AlfredoPA22

## Contacto

Para más información, consulta la documentación en `/docs` o crea un issue en el repositorio.

