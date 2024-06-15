import html2text


def convert_html_to_text(html: str) -> str:
    h = html2text.HTML2Text()

    h.ignore_links = True
    h.ignore_images = True
    h.emphasis_mark = ""
    h.strong_mark = ""

    result = h.handle(html)
    return result
