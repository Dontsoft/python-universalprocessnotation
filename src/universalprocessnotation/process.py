from typing import List, Optional

from .block import Block


class Process:

    __name: str
    __blocks: List["Block"]

    def __init__(self, name: str):
        self.__name = name
        self.__blocks = []

    def name(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__name

    def __recursive_blocks(
        self, block: Optional["Block"] = None, current_list: List["Block"] = []
    ) -> List["Block"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        if block is None or block in current_list:
            return current_list
        current_list.append(block)
        for connected_block in block.connected_blocks():
            current_list = self.__recursive_blocks(connected_block, current_list)
        return current_list

    def blocks(self, include_subprocesses : bool = False) -> List["Block"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        if include_subprocesses:
            current_list = []
            for block in self.__blocks:
                current_list = self.__recursive_blocks(block, current_list)
            return current_list
        return self.__blocks

    def add_block(self, activity: str, trigger: Optional[str] = None) -> "Block":
        """_summary_

        Args:
            activity (str): _description_
            trigger (Optional[str], optional): _description_. Defaults to None.

        Returns:
            Block: _description_
        """
        return Block(self, activity, trigger)

    def _append_block(self, block: "Block"):
        """_summary_

        Args:
            block (Block): _description_

        Raises:
            Exception: _description_
        """
        if block not in self.__blocks:
            self.__blocks.append(block)
        else:
            raise Exception("Block already appended")

    def find_block(self, block_activity: str, search_subprocesses : bool = False) -> "Block":
        """_summary_

        Args:
            block_activity (str): _description_

        Raises:
            Exception: _description_

        Returns:
            Block: _description_
        """
        for block in self.blocks(search_subprocesses):
            if block.activity() == block_activity:
                return block
        raise Exception(f"Block with activity '{block_activity}' not found")
