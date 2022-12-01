from dataclasses import dataclass

from models.reference import Reference
from models.stage import Stage


@dataclass
class Reaction(object):
    reaction_id: str
    reactants: list[str]
    products: list[str]
    stages: list[Stage]
    stages_number: int
    yield_value: str
    reference: Reference

    def to_csv(self, delimiter):
        stages = [stage.to_csv(delimiter) for stage in self.stages]
        return delimiter.join(
            map(
                str,
                [
                    self.reaction_id,
                    self.reactants,
                    self.products,
                    self.stages_number,
                    self.yield_value,
                    self.reference.to_csv(delimiter),
                    *stages,
                ],
            ),
        )
