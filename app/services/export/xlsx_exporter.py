from io import BytesIO

from openpyxl import Workbook

from app.models.entities import RegistryRecord


def export_records_to_xlsx(records: list[RegistryRecord]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Registry"
    ws.append([
        "Номер",
        "Тип",
        "Дата регистрации",
        "Тема",
        "Отправитель",
        "Получатели",
        "Статус ID",
        "Ссылка",
    ])
    for item in records:
        ws.append([
            item.registry_number,
            item.record_type.value,
            item.registered_at.isoformat() if item.registered_at else "",
            item.subject or "",
            item.from_email or "",
            item.to_emails or "",
            item.status_id,
            item.storage_url or "",
        ])

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
