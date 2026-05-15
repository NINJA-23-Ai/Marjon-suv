def parse_int_list(value: str | list[int] | tuple[int, ...] | None) -> list[int]:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [int(item) for item in value]
    cleaned = value.strip()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned.removeprefix("[").removesuffix("]")
    return [int(item.strip().strip('"').strip("'")) for item in cleaned.split(",") if item.strip()]
