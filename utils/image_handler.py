"""
Utilidades para manejar imágenes usando Cloudinary.
"""
import os
from typing import Tuple, Optional
from urllib.parse import urlparse

import cloudinary
from cloudinary import uploader

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "cloudinary://198651442368157:sXFZBgdC_Sap5KANgWOD7fRzWTs@dyyd4no6j")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "Importaciones")

if CLOUDINARY_URL:
    cloudinary.config(
    cloud_name="dyyd4no6j",
    api_key="198651442368157",
    api_secret="sXFZBgdC_Sap5KANgWOD7fRzWTs"
)
else:
    print("Advertencia: CLOUDINARY_URL no está configurada. Las operaciones de imagen fallarán.")


def save_image_file(file_contents: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Guarda una imagen en Cloudinary y retorna la URL segura.

    Returns:
        (success, secure_url, error_message)
    """
    if not CLOUDINARY_URL:
        return False, None, "CLOUDINARY_URL no configurada en el servidor."

    try:
        result = uploader.upload(
            file_contents,
            folder=CLOUDINARY_FOLDER,
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
        secure_url = result.get("secure_url")
        if not secure_url:
            return False, None, "Cloudinary no retornó una URL segura."
        return True, secure_url, None
    except Exception as e:
        return False, None, f"Error al subir a Cloudinary: {str(e)}"


def delete_image_file(image_url: str) -> Tuple[bool, Optional[str]]:
    """
    Elimina una imagen de Cloudinary usando la URL almacenada en la base de datos.

    Returns:
        (success, error_message)
    """
    if not CLOUDINARY_URL:
        return False, "CLOUDINARY_URL no configurada en el servidor."

    public_id = _extract_public_id(image_url)
    if not public_id:
        return False, "No se pudo extraer el public_id de la URL proporcionada."

    try:
        result = uploader.destroy(public_id, invalidate=True, resource_type="image")
        if result.get("result") not in {"ok", "not found"}:
            return False, f"No se pudo eliminar la imagen en Cloudinary: {result}"
        return True, None
    except Exception as e:
        return False, f"Error al eliminar imagen en Cloudinary: {str(e)}"


def _extract_public_id(image_url: str) -> Optional[str]:
    """
    Extrae el public_id de una URL de Cloudinary.
    """
    try:
        path = urlparse(image_url).path  # /<cloud_name>/image/upload/v1234567890/folder/file.jpg
        segments = [segment for segment in path.split("/") if segment]
        if "upload" not in segments:
            return None

        upload_index = segments.index("upload")
        identifier_parts = segments[upload_index + 1 :]
        if not identifier_parts:
            return None

        # El primer elemento suele ser la versión (v1234567890)
        if identifier_parts[0].startswith("v") and identifier_parts[0][1:].isdigit():
            identifier_parts = identifier_parts[1:]

        identifier_with_ext = "/".join(identifier_parts)
        if "." not in identifier_with_ext:
            return identifier_with_ext

        public_id = identifier_with_ext.rsplit(".", 1)[0]
        return public_id
    except Exception as e:
        print(f"Advertencia: no se pudo extraer public_id de '{image_url}': {e}")
        return None

