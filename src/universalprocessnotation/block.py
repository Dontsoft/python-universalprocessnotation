from typing import TYPE_CHECKING, List, Optional, Dict, Tuple
from enum import IntFlag, auto
if TYPE_CHECKING:
    from process import Process

GLOBAL_LINKS: Dict[int, "Link"] = dict()
GLOBAL_BLOCKS: Dict[int, "Block"] = dict()


def next_id(d: Dict[int, "Link"] | Dict[int, "Block"]) -> int:
    if not d:
        return 0
    return max(d.keys()) + 1

class Link:
    why: str
    from_block: "Block"
    to_block: Optional["Block"] = None

    def __init__(
        self, why: str, from_block: "Block", to_block: Optional["Block"] = None
    ):
        """_summary_

        Args:
            why (str): _description_
            from_block (Block): _description_
            to_block (Optional[&quot;Block&quot;], optional): _description_. Defaults to None.
        """
        self.why = why
        self.from_block = from_block
        self.to_block = to_block

    def __repr__(self):
        return f"Link({self.from_block.activity()} => {self.why} => {self.to_block.activity() if self.to_block is not None else 'End'})"
    
    def inverted(self):
        return Link(self.why, self.to_block, self.from_block)


class RASCI(IntFlag):
    RESPONSIBLE = auto()
    ACCOUNTABLE = auto()
    SUPPORT = auto()
    CONSULTED = auto()
    INFORMED = auto()


class Block:
    __id: int
    __activity: str
    __process: "Process"

    __attachment: bool = False
    __subprocess: Optional["Process"] = None
    __links: List[Link]
    __who: Dict[str, RASCI]
    __with_what: List[str]
    __triggers: Optional[List[str]] = None

    _from: List[Link]

    def __init__(
        self, process: "Process", activity: str, trigger: Optional[List[str] | str] = None
    ):
        """_summary_

        Args:
            process (Process): _description_
            activity (str): _description_
            trigger (Optional[str], optional): _description_. Defaults to None.
        """
        if process is None:
            raise Exception("Process can not be 'None'")
        self.__id = next_id(GLOBAL_BLOCKS)
        GLOBAL_BLOCKS[self.__id] = self

        self.__process = process
        self.__activity = activity
        self.__process._append_block(self)
        if trigger is None or hasattr(trigger, '__iter__'):
            self.__triggers = trigger
        elif isinstance(trigger, str):
            self.__triggers = [trigger]
        self.__triggers = trigger
        self.__links = []
        self.__who = dict()
        self.__with_what = []
        self._from = []

    def get_id(self):
        return self.__id

    def __repr__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return f"{self.__activity}"
        return f"Block(Activity = {self.__activity}, Trigger={self.__triggers}, Links={self.__links}, Attachment={self.__attachment}, Subprocess={self.__subprocess}, Whos={self.__who}, With What={self.__with_what})"

    def process(self) -> "Process":
        return self.__process

    def remove(self):
        self.__process.remove_block(self)

    def activity(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__activity

    def set_attachment(self, attachment: bool):
        """_summary_

        Args:
            attachment (bool): _description_
        """
        self.__attachment = attachment

    def has_attachment(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        return self.__attachment

    def unset_attachment(self):
        """_summary_
        """
        self.__attachment = False

    def add_trigger(self, trigger: str):
        if self.__triggers is None:
            self.__triggers = [trigger]
        else:
            self.__triggers.append(trigger)

    def set_triggers(self, triggers: List[str], copy: bool = False):
        """_summary_

        Args:
            trigger (str): _description_
        """
        self.__triggers = triggers.copy() if copy else triggers

    def unset_triggers(self):
        """_summary_
        """
        self.__triggers = None

    def triggers(self) -> Optional[List[str]]:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__triggers

    def set_subprocess(self, subprocess: "Process"):
        """_summary_

        Args:
            subprocess (Process): _description_

        Raises:
            Exception: _description_
        """
        if self in subprocess.blocks(include_subprocesses=True):
            raise Exception("Current block is part of the subprocess")
        self.__subprocess = subprocess

    def unset_subprocess(self):
        """_summary_
        """
        self.__subprocess = None

    def subprocess(self):
        return self.__subprocess

    def connected_blocks(self, include_subprocess: bool = False) -> List["Block"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        blocks = [
            link.to_block for link in self.__links if link.to_block is not None]
        blocks = blocks + \
            [link.from_block for link in self._from if link.from_block is not None]
        if self.__subprocess is not None and include_subprocess:
            blocks = blocks + self.__subprocess.blocks()
        return list(set(blocks))

    def recursive_all_connected_blocks(block: "Block", current_list: List["Block"], include_subprocess: bool = False) -> List["Block"]:
        if block is None or block in current_list:
            return current_list

        current_list.append(block)
        for to_block in block.links():
            current_list = Block.recursive_all_connected_blocks(
                to_block.to_block, current_list, include_subprocess)
        for from_block in block.from_links():
            current_list = Block.recursive_all_connected_blocks(
                from_block.from_block, current_list, include_subprocess)
        if block.subprocess() is not None and include_subprocess:
            for block in block.subprocess():
                current_list = Block.recursive_all_connected_blocks(
                    block, current_list, True)
        return current_list

    def all_connected_blocks(self, include_subprocess: bool = False) -> List["Block"]:
        return Block.recursive_all_connected_blocks(self, [], include_subprocess)
    
    def recursive_all_connected_blocks_in_link_direction(block: "Block", current_list: List["Block"]) -> List["Block"]:
        if block is None or block in current_list:
            return current_list
        current_list.append(block)
        for to_block in block.links():
            current_list = Block.recursive_all_connected_blocks_in_link_direction(
                to_block.to_block, current_list)
        return current_list
    
    def all_connected_block_in_link_direction(self) -> List["Block"]:
        return Block.recursive_all_connected_blocks_in_link_direction(self, [])
    
    def recursive_find_block_in_all_connected_blocks_in_link_direction(block : "Block", visited_blocks: Optional[List["Block"]] = None) -> bool:
        found = False
        if visited_blocks is None:
            visited_blocks = []
        if block is None or block in visited_blocks:
            return found
        for links in block.links():
            if links.to_block is block:
                return True
            visited_blocks.append(links.to_block)
            found = found | Block.recursive_find_block_in_all_connected_blocks_in_link_direction(links.to_block, visited_blocks)
        return found

    def connect_end(self, why: str):
        """_summary_

        Args:
            why (str): _description_
        """
        self.connect(why, None)

    def disconnect_end(self, why: str):
        """_summary_

        Args:
            why (str): _description_
        """
        self.disconnect(why)

    def connect_new(self, why: str, activity: str, trigger: Optional[str] = None) -> "Block":
        block = self.__process.add_block(activity, trigger)
        self.connect(why, block)
        return block

    def connect(self, why: str, block: Optional["Block"] = None):
        """_summary_

        Args:
            why (str): _description_
            block (Optional[&quot;Block&quot;], optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
        """
        if block is not None:
            if not self.__process == block.__process:
                raise Exception(
                    "Only blocks in the same process can be connected")
        link = Link(why, self, block)
        self.__links.append(link)
        if block is not None:
            block._from.append(link)

    def disconnect(self, why: str):
        """_summary_

        Args:
            why (str): _description_

        Raises:
            Exception: _description_
        """
        link = None
        for _link in self.__links:
            if _link.why == why:
                link = _link
                break
        if link is None:
            raise Exception(f"No connection found for '{why}'")
        self.__links.remove(link)
        if link.to_block is not None:
            to_block = link.to_block
            to_block._from.remove(link)

    def links(self) -> List[Link]:
        return self.__links.copy()

    def from_links(self) -> List[Link]:
        return self._from.copy()

    def links_return_to_this_block(self) -> bool:
        return Block.recursive_find_block_in_all_connected_blocks_in_link_direction(self)

    def links_with_inverted_from_links(self) -> List[Link]:
        return self.links() + [link.inverted() for link in self.from_links()]

    def add_who(self, who: str, *, responsible: bool = False, accountable: bool = False, support: bool = False, consulted: bool = False, informed: bool = False):
        """_summary_

        Args:
            who (str): _description_
        """
        rasci = 0
        if responsible:
            rasci = rasci | RASCI.RESPONSIBLE
        if accountable:
            rasci = rasci | RASCI.ACCOUNTABLE
        if support:
            rasci = rasci | RASCI.SUPPORT
        if consulted:
            rasci = rasci | RASCI.CONSULTED
        if informed:
            rasci = rasci | RASCI.INFORMED
        self.add_who_rasci(who, rasci)

    def add_who_rasci(self, who: str, rasci: RASCI):
        self.__who[who] = rasci

    def remove_who(self, who: str):
        """_summary_

        Args:
            who (str): _description_
        """
        self.__who.pop(who)

    def set_whos(self, whos: Dict[str, RASCI], copy: bool = False):
        """_summary_

        Args:
            whos (List[str]): _description_
            copy (bool, optional): _description_. Defaults to False.
        """
        self.__who = whos.copy() if copy else whos

    def clear_whos(self):
        """_summary_
        """
        self.__who.clear()

    def whos(self) -> List[str]:
        return self.__who

    def add_with_what(self, with_what: str):
        """_summary_

        Args:
            with_what (str): _description_
        """
        self.__with_what.append(with_what)

    def remove_with_what(self, with_what: str):
        """_summary_

        Args:
            with_what (str): _description_
        """
        self.__with_what.remove(with_what)

    def set_with_whats(self, with_what: List[str], copy: bool = False):
        """_summary_

        Args:
            with_what (List[str]): _description_
            copy (bool, optional): _description_. Defaults to False.
        """
        self.__with_what = with_what.copy() if copy else with_what

    def clear_with_whats(self):
        """_summary_
        """
        self.__with_what.clear()

    def with_whats(self) -> List[str]:
        return self.__with_what

    def add_system(self, system: str):
        """_summary_

        Args:
            system (str): _description_
        """
        self.add_with_what(system)

    def remove_system(self, system: str):
        """_summary_

        Args:
            system (str): _description_
        """
        self.remove_with_what(system)

    def set_systems(self, systems: List[str]):
        """_summary_

        Args:
            systems (List[str]): _description_
        """
        self.set_with_whats(systems)

    def clear_systems(self):
        """_summary_
        """
        self.clear_with_whats()

    def systems(self) -> List[str]:
        return self.with_whats()
