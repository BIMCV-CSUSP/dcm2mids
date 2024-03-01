from pathlib import Path
from typing import Union


class Tagger:
    def __init__(self, protocol_table_path: Union[Path, str]):
        if type(protocol_table_path) is str:
            self.protocol_table_path = Path(protocol_table_path)
            self.table_protocols = pd.read_csv(
                protocol_table_path, sep="\t", index_col=False
            )
        else:
            self.protocol_table_path = protocol_table_path
            self.table_protocols = pd.read_csv(
                protocol_table_path, sep="\t", index_col=False
            )

    def classification_by_min_max(self, json: dict) -> list:
        pass
