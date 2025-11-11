def shareTokenEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "import_id": item.get("import_id", ""),
        "token": item.get("token", ""),
        "expires_at": item.get("expires_at"),
        "is_active": item.get("is_active", True),
        "created_at": item.get("created_at"),
    }

def shareTokensEntity(entity) -> list:
    return [shareTokenEntity(item) for item in entity]

