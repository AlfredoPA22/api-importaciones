# Guía de Despliegue en Vercel

## Cambios Realizados para Compatibilidad con Vercel

### 1. Configuración de MongoDB
- ✅ Timeouts optimizados para serverless (3 segundos)
- ✅ Pool de conexiones más pequeño (maxPoolSize: 5)
- ✅ Manejo de errores sin bloquear el inicio de la aplicación
- ✅ Conexión lazy (solo cuando se necesita)

### 2. Manejo de Imágenes
- ✅ Detección automática del entorno (Vercel vs local)
- ✅ Todas las imágenes se suben a Cloudinary (sin depender del sistema de archivos de Vercel)
- ✅ Se almacena directamente la `secure_url` en la base de datos para consumo inmediato en el frontend
- ✅ No se monta StaticFiles en Vercel (no es necesario)

### 3. Validaciones de Base de Datos
- ✅ Todas las rutas validan la conexión a MongoDB antes de usarla
- ✅ Respuestas de error claras si la base de datos no está disponible

### 4. Configuración de Vercel
- ✅ `vercel.json` configurado correctamente
- ✅ `.vercelignore` para excluir archivos innecesarios

## Pasos para Desplegar en Vercel

### 1. Configurar Variables de Entorno en Vercel

En el dashboard de Vercel, ve a tu proyecto y configura las siguientes variables de entorno:

```
MONGODB_URL=...
CLOUDINARY_URL=cloudinary://<key>:<secret>@<cloud_name>
CLOUDINARY_FOLDER=Home/Importaciones
CORS_ORIGINS=https://public-client-importaciones.vercel.app
VERCEL=1
```

**IMPORTANTE**: Asegúrate de que `MONGODB_URL` y `CLOUDINARY_URL` estén configuradas correctamente.

### 2. Desplegar el Proyecto

1. Conecta tu repositorio de GitHub a Vercel
2. Vercel detectará automáticamente el archivo `vercel.json`
3. El despliegue se iniciará automáticamente

### 3. Verificar el Despliegue

Una vez desplegado, verifica:
- ✅ Endpoint `/health` responde correctamente
- ✅ Endpoint `/` muestra el mensaje de bienvenida
- ✅ Endpoints de la API funcionan correctamente
- ✅ Las imágenes nuevas generan URLs de Cloudinary accesibles públicamente

## Notas Importantes

### Imágenes en Vercel
- Todas las imágenes se suben automáticamente a Cloudinary usando la carpeta configurada
- La respuesta de la API devuelve directamente la `secure_url`
- No se necesita un sistema de archivos local ni conversión a base64

### MongoDB
- Asegúrate de que tu cluster de MongoDB permita conexiones desde cualquier IP (0.0.0.0/0)
- O configura las IPs de Vercel en la whitelist de MongoDB Atlas

### Límites de Vercel
- Tamaño máximo de función: 50MB
- Tiempo máximo de ejecución: 10 segundos (Hobby) o 60 segundos (Pro)
- Las imágenes base64 aumentan el tamaño de los documentos en MongoDB

## Solución de Problemas

### Error: "Error de conexión a la base de datos"
- Verifica que `MONGODB_URL` esté configurada correctamente en Vercel
- Verifica que MongoDB Atlas permita conexiones desde cualquier IP
- Verifica que las credenciales sean correctas

### Error: "Function exceeded maximum duration"
- Reduce el tamaño de las imágenes
- Optimiza las consultas a MongoDB
- Considera usar índices en MongoDB

### Las imágenes no se muestran
- Verifica que `CLOUDINARY_URL` y `CLOUDINARY_FOLDER` estén configurados correctamente
- Revisa los logs de Vercel para detectar errores de subida a Cloudinary
- Asegúrate de que el frontend use directamente la URL devuelta (`https://res.cloudinary.com/...`)

## Mejoras Futuras

Para producción, considera:
1. **Optimización de imágenes**: Comprimir y redimensionar antes de subirlas para ahorrar ancho de banda
2. **CDN**: Configurar transformaciones/optimización de Cloudinary según necesidades del frontend
3. **Optimización de consultas**: Agregar índices en colecciones críticas
4. **Caché**: Implementar caché para consultas frecuentes

