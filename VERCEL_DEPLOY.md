# Guía de Despliegue en Vercel

## Cambios Realizados para Compatibilidad con Vercel

### 1. Configuración de MongoDB
- ✅ Timeouts optimizados para serverless (3 segundos)
- ✅ Pool de conexiones más pequeño (maxPoolSize: 5)
- ✅ Manejo de errores sin bloquear el inicio de la aplicación
- ✅ Conexión lazy (solo cuando se necesita)

### 2. Manejo de Archivos Estáticos
- ✅ Detección automática del entorno (Vercel vs local)
- ✅ En Vercel: imágenes almacenadas como base64 en MongoDB
- ✅ En local: imágenes almacenadas como archivos en el sistema de archivos
- ✅ No se monta StaticFiles en Vercel (no funciona en serverless)

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
MONGODB_URL=mongodb+srv://alfredo:alfredo123@cluster0npm.eqdyu9u.mongodb.net
VERCEL=1
```

**IMPORTANTE**: Asegúrate de que `MONGODB_URL` esté configurada correctamente.

### 2. Desplegar el Proyecto

1. Conecta tu repositorio de GitHub a Vercel
2. Vercel detectará automáticamente el archivo `vercel.json`
3. El despliegue se iniciará automáticamente

### 3. Verificar el Despliegue

Una vez desplegado, verifica:
- ✅ Endpoint `/health` responde correctamente
- ✅ Endpoint `/` muestra el mensaje de bienvenida
- ✅ Endpoints de la API funcionan correctamente
- ✅ Las imágenes se almacenan como base64 en MongoDB (en Vercel)

## Notas Importantes

### Imágenes en Vercel
- Las imágenes se almacenan como **base64 en MongoDB** cuando se despliega en Vercel
- Esto es necesario porque Vercel es serverless y no tiene sistema de archivos persistente
- El frontend debe manejar imágenes base64 (data URLs) cuando esté en producción

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
- En Vercel, las imágenes están en base64 en MongoDB
- El frontend debe usar las imágenes como data URLs (`data:image/jpeg;base64,...`)
- Verifica que el campo `images` en la respuesta de la API contenga las imágenes en base64

## Mejoras Futuras

Para producción, considera:
1. **Almacenamiento de imágenes**: Usar un servicio como AWS S3, Cloudinary o Vercel Blob Storage
2. **CDN**: Servir las imágenes a través de un CDN para mejor rendimiento
3. **Optimización de imágenes**: Comprimir y redimensionar imágenes antes de almacenarlas
4. **Caché**: Implementar caché para consultas frecuentes

