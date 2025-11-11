def clientEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item.get("name", ""),
        "email": item.get("email"),
        "phone": item.get("phone"),
        "address": item.get("address"),
        "company": item.get("company"),
        "notes": item.get("notes"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }

def clientsEntity(entity) -> list:
    return [clientEntity(item) for item in entity]

