"""Visible HTML text for AI classification, without regex extraction rules."""

from html.parser import HTMLParser


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._hidden: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "template"}:
            self._hidden.append(tag)
        if not self._hidden:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if self._hidden and tag == self._hidden[-1]:
            self._hidden.pop()
        if not self._hidden:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._hidden:
            self.parts.append(data)


def html_to_text(raw_html: str) -> str:
    parser = _TextParser()
    parser.feed(raw_html)
    parser.close()
    return " ".join("".join(parser.parts).split())
