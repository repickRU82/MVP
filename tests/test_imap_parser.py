from app.services.imap.collector import EmailParser


RAW = b"""From: Test <test@example.com>\nTo: info@example.com\nSubject: =?utf-8?B?0KLQtdGB0YI=?=\nMessage-ID: <m1@example.com>\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=abc\n\n--abc\nContent-Type: text/plain; charset=utf-8\n\nbody text\n--abc\nContent-Type: text/plain\nContent-Disposition: attachment; filename=\"hello.txt\"\n\nattach\n--abc--\n"""


def test_parser_extracts_fields_and_attachments() -> None:
    parsed = EmailParser().parse(RAW)

    assert parsed.message_id == "<m1@example.com>"
    assert parsed.subject == "Тест"
    assert parsed.body_preview == "body text"
    assert len(parsed.attachments) == 1
    assert parsed.attachments[0].original_filename == "hello.txt"
