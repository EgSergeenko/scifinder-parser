from dataclasses import dataclass


@dataclass
class Stage(object):
    stage_number: int
    reagents: list[str]
    catalysts: list[str]
    solvents: list[str]
    other_conditions: str

    def to_csv(self, delimiter):
        return delimiter.join(
            map(
                str,
                [
                    self.reagents,
                    self.catalysts,
                    self.solvents,
                    self.other_conditions,
                ],
            ),
        )
