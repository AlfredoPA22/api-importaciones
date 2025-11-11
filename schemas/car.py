def carEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "model": item.get("model", ""),
        "brand": item.get("brand", ""),
        "year": item.get("year", 0),
        "sale_price": item.get("sale_price", 0.0),
        "color": item.get("color"),
        "vin": item.get("vin"),
        "description": item.get("description"),
    }

def carsEntity(entity) -> list:
    return [carEntity(item) for item in entity]