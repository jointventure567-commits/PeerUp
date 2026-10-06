from pathlib import Path


FAVICON_TAG = (
    '    <link rel="icon" type="image/svg+xml" '
    'href="/static/favicon.svg">\n'
)


templates_folder = Path("templates")

updated = 0


for file_path in templates_folder.glob("*.html"):

    text = file_path.read_text(
        encoding="utf-8"
    )

    if "/static/favicon.svg" in text:
        continue

    if "</head>" not in text:
        continue

    text = text.replace(
        "</head>",
        FAVICON_TAG + "</head>",
        1
    )

    file_path.write_text(
        text,
        encoding="utf-8"
    )

    updated += 1


print(
    f"Favicon added to {updated} template files."
)