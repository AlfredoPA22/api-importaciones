"""
Utilidades para manejar imágenes en diferentes entornos (local y Vercel/serverless)
"""
import os
from pathlib import Path
import base64
from typing import Tuple, Optional

IS_VERCEL = os.getenv("VERCEL") == "1"

def get_upload_dir() -> Path:
    """Obtiene el directorio de uploads según el entorno"""
    if IS_VERCEL:
        # En Vercel, usar /tmp que es el único directorio escribible
        return Path("/tmp/uploads/imports")
    else:
        return Path("uploads/imports")

def save_image_file(file_contents: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Guarda una imagen. En Vercel, retorna base64. En local, guarda archivo.
    
    Returns:
        (success, image_url_or_base64, error_message)
    """
    if IS_VERCEL:
        # En Vercel, convertir a base64 y retornar
        try:
            image_base64 = base64.b64encode(file_contents).decode('utf-8')
            # Determinar el tipo MIME basado en la extensión
            ext = Path(filename).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            data_url = f"data:{mime_type};base64,{image_base64}"
            return True, data_url, None
        except Exception as e:
            return False, None, f"Error al procesar imagen: {str(e)}"
    else:
        # En local, guardar archivo
        try:
            upload_dir = get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / filename
            with open(file_path, "wb") as buffer:
                buffer.write(file_contents)
            image_url = f"/uploads/imports/{filename}"
            return True, image_url, None
        except Exception as e:
            return False, None, f"Error al guardar archivo: {str(e)}"

def delete_image_file(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Elimina una imagen. En Vercel, no hace nada (las imágenes están en MongoDB).
    En local, elimina el archivo.
    
    Returns:
        (success, error_message)
    """
    if IS_VERCEL:
        # En Vercel, las imágenes están en MongoDB como base64, no hay archivo que eliminar
        return True, None
    else:
        # En local, eliminar archivo
        try:
            upload_dir = get_upload_dir()
            file_path = upload_dir / filename
            if file_path.exists():
                file_path.unlink()
            return True, None
        except Exception as e:
            return False, f"Error al eliminar archivo: {str(e)}"

def get_image_response(image_data: str) -> dict:
    """
    Retorna la respuesta apropiada para una imagen según el entorno.
    En Vercel, las imágenes están en base64. En local, son URLs.
    """
    if IS_VERCEL:
        # En Vercel, la imagen ya está en base64 (data URL)
        return {
            "type": "base64",
            "data": image_data
        }
    else:
        # En local, es una URL
        return {
            "type": "url",
            "url": image_data
        }

