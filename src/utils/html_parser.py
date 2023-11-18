from html.parser import HTMLParser


class HTMLTagsRemover(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.reset()
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def handle_entityref(self, name):
        self.fed.append(f'&{name};')

    def handle_charref(self, name):
        self.fed.append(f'&#{name};')

    def get_data(self):
        return "".join(self.fed)


def remove_html_tags(value: str) -> str:
    remover = HTMLTagsRemover()

    remover.feed(value)
    remover.close()
    return remover.get_data()
