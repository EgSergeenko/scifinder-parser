from dataclasses import dataclass


@dataclass
class Reference(object):
    title: str
    authors: str
    bibliography: str

    def to_csv(self, delimiter):
        return delimiter.join(
            [
                self.title,
                self.authors,
                self.bibliography,
            ],
        )
