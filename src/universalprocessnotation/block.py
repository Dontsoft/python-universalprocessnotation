from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from process import Process

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

class Block:
    __activity: str
    __process: "Process"

    __attachment: bool = False
    __subprocess: Optional["Process"] = None
    __links: List[Link]
    __who: List[str]
    __with_what: List[str]
    __trigger: Optional[str] = None

    _from: List[Link]

    def __init__(
        self, process: "Process", activity: str, trigger: Optional[str] = None
    ):
        """_summary_

        Args:
            process (Process): _description_
            activity (str): _description_
            trigger (Optional[str], optional): _description_. Defaults to None.
        """
        if process is None:
            raise Exception("Process can not be 'None'")
        
        self.__process = process
        self.__activity = activity
        self.__process._append_block(self)
        self.__trigger = trigger
        self.__links = []
        self.__who = []
        self.__with_what = []
        self._from = []

    def __repr__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return f"Block(Activity = {self.__activity}, Trigger={self.__trigger}, Links={self.__links}, Attachment={self.__attachment}, Subprocess={self.__subprocess}, Whos={self.__who}, With What={self.__with_what})"

    def process(self) -> "Process":
        return self.__process

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

    def set_trigger(self, trigger: str):
        """_summary_

        Args:
            trigger (str): _description_
        """
        self.__trigger = trigger

    def unset_trigger(self):
        """_summary_
        """
        self.__trigger = None

    def trigger(self) -> Optional[str]:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__trigger

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

    def connected_blocks(self) -> List["Block"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        blocks = [link.to_block for link in self.__links if link.to_block is not None]
        if self.__subprocess is not None:
            blocks = blocks + self.__subprocess.blocks()
        return blocks

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
                raise Exception("Only blocks in the same process can be connected")
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
        return self.__links
    
    def from_links(self) -> List[Link]:
        return self._from.copy()

    def add_who(self, who: str):
        """_summary_

        Args:
            who (str): _description_
        """
        self.__who.append(who)

    def remove_who(self, who: str):
        """_summary_

        Args:
            who (str): _description_
        """
        self.__who.remove(who)

    def set_whos(self, whos: List[str], copy: bool = False):
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