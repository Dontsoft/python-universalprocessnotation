from typing import TYPE_CHECKING, List, Optional, Dict
from enum import IntFlag, auto
import svg
import math
from .util import *

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
        self, process: "Process", activity: str, triggers: Optional[List[str]] = None
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
        self.__triggers = triggers
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

    def recursive_find_block_in_all_connected_blocks_in_link_direction(block: "Block", visited_blocks: Optional[List["Block"]] = None) -> bool:
        found = False
        if visited_blocks is None:
            visited_blocks = []
        if block is None or block in visited_blocks:
            return found
        for links in block.links():
            if links.to_block is block:
                return True
            visited_blocks.append(links.to_block)
            found = found | Block.recursive_find_block_in_all_connected_blocks_in_link_direction(
                links.to_block, visited_blocks)
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

    def connect_new(self, why: str, activity: str, triggers: Optional[List[str]] = None) -> "Block":
        block = self.__process.add_block(activity, triggers)
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

    def activity_height(self, width: Optional[int] = None) -> int:
        if width is None:
            width = self.calculate_width()
        inner_width = width - 2 * X_PADDING - STROKE_WIDTH
        activity_lines = fit_text_to_width(self.activity(), inner_width)

        activity_lines = max(1, len(activity_lines))
        return activity_lines * LINE_HEIGHT

    def who_height(self) -> int:
        who_count = len(self.__who)
        return min(who_count, 1) * INNER_STROKE_WIDTH + who_count * LINE_HEIGHT + min(who_count, 1) * INNER_PADDING

    def with_what_height(self) -> int:
        with_what_count = len(self.__with_what)
        return min(with_what_count, 1) * INNER_STROKE_WIDTH + with_what_count * LINE_HEIGHT + min(with_what_count, 1) * INNER_PADDING

    def calculate_height(self, width: Optional[int] = None) -> int:
        return self.activity_height(width) + self.who_height() + self.with_what_height() + 2*Y_PADDING + STROKE_WIDTH

    def calculate_width(self) -> int:
        width = MIN_WIDTH
        for system in self.__with_what:
            width = max(width, text_width(system))
        for who, rasci in self.__who.items():
            rasci_pad = 0
            if rasci & RASCI.RESPONSIBLE:
                rasci_pad = rasci_pad + 16
            if rasci & RASCI.ACCOUNTABLE:
                rasci_pad = rasci_pad + 16
            if rasci & RASCI.SUPPORT:
                rasci_pad = rasci_pad + 16
            if rasci & RASCI.CONSULTED:
                rasci_pad = rasci_pad + 16
            if rasci & RASCI.INFORMED:
                rasci_pad = rasci_pad + 16
            width = max(width, text_width(who) + rasci_pad +
                        (0 if rasci_pad == 0 else CHARWIDTH_LUT[' ']))
        for word in self.__activity.split(" "):
            width = max(width, text_width(word))
        return width + 2 * X_PADDING + STROKE_WIDTH
    
    def calculate_output_textbox_width(self) -> int:
        max_width = MIN_LINK_TEXT_WIDTH
        for text in sorted([link.why for link in self.links()], key=lambda why: text_width(why), reverse=True):
            width = text_width(text) + 2* INNER_PADDING
            if width > max_width:
                splitted_why = text.split(" ")
                if len(splitted_why) > 1:    
                    first_line = ""
                    last_line = ""
                    first_index = 0
                    last_index = len(splitted_why) - 1
                    while first_index <= last_index:
                        if text_width(first_line) <= text_width(last_line):
                            first_line = first_line + (" " if len(first_line) > 0 else "") + splitted_why[first_index]
                            first_index = first_index + 1
                        else:
                            last_line = (" " if len(last_line) > 0 else "") + splitted_why[last_index] + last_line
                            last_index = last_index - 1
                    max_width = max(text_width(first_line), text_width(last_line)) + 2 * INNER_PADDING
                else:
                    max_width = width
        return max_width
    
    def calculate_input_textbox_width(self) -> int:
        if self.triggers() is None:
            return 0
        max_width = MIN_LINK_TEXT_WIDTH
        for text in sorted(self.triggers(), key=lambda why: text_width(why), reverse=True):
            width = text_width(text) + 2 * INNER_PADDING
            if width > max_width:
                splitted_why = text.split(" ")
                if len(splitted_why) > 1:
                    first_line = ""
                    last_line = ""
                    first_index = 0
                    last_index = len(splitted_why) - 1
                    while first_index <= last_index:
                        if text_width(first_line) <= text_width(last_line):
                            first_line = first_line + \
                                (" " if len(first_line) > 0 else "") + \
                                splitted_why[first_index]
                            first_index = first_index + 1
                        else:
                            last_line = (" " if len(last_line) > 0 else "") + \
                                splitted_why[last_index] + last_line
                            last_index = last_index - 1
                    max_width = max(text_width(first_line), text_width(
                        last_line)) + 2 * INNER_PADDING
                else:
                    max_width = width
        return max_width


    def to_svg(self, width: int, height: int):
        elements = [svg.Rect(
            stroke=MAIN_COLOR,
            stroke_width=STROKE_WIDTH,
            width=width,
            height=height,
            fill="white",
            rx=RX
        )]

        corner_path = svg.Path(d=f"M0,{Y_PADDING * 2}L0,{RX}Q0 0 {RX} 0L{Y_PADDING * 2},0L0,{Y_PADDING * 2}Z",
                               stroke=MAIN_COLOR, stroke_width=STROKE_WIDTH, fill=MAIN_COLOR)

        corner_text = svg.Text(x=RX, y=RX / 2 + LINE_HEIGHT / 2, elements=[
                               str(self.get_id() + 1)], style=("fill: white" if self.__subprocess is not None else "fill: " + MAIN_COLOR), dominant_baseline="middle")

        attachment_corner = svg.G(transform=f"translate({width - ATTACHMENT_SIZE - (RX / 2)}, {RX / 2}) scale({ATTACHMENT_SIZE / 512}, {ATTACHMENT_SIZE / 512})", elements=[svg.Path(
            d="M216.08 192v143.85a40.08 40.08 0 0080.15 0l.13-188.55a67.94 67.94 0 10-135.87 0v189.82a95.51 95.51 0 10191 0V159.74", fill="none", stroke_width="32", stroke_miterlimit="10", stroke_linecap="round", stroke=ATTACHMENT_COLOR)])

        if self.__subprocess is not None:
            elements.append(corner_path)
        elements.append(corner_text)
        elements.append(attachment_corner)

        inner_width = width - X_PADDING * 2 - STROKE_WIDTH

        who_height = self.who_height()
        with_what_height = self.with_what_height()

        activity_y = Y_PADDING + STROKE_WIDTH / 2

        for activity_line in fit_text_to_width(self.activity(), inner_width):
            elements.append(svg.Text(x=width / 2, y=activity_y + LINE_HEIGHT / 2,
                            dominant_baseline="middle", text_anchor="middle", elements=[activity_line]))
            activity_y = activity_y + LINE_HEIGHT

        next_y = activity_y + Y_PADDING

        if who_height > 0:
            next_y = next_y + (INNER_STROKE_WIDTH / 2)
            elements.append(svg.Path(d=f"M{STROKE_WIDTH / 2},{next_y} L{width - STROKE_WIDTH / 2},{
                            next_y}Z", stroke=ATTACHMENT_COLOR, stroke_width=INNER_STROKE_WIDTH))
            next_y = next_y + (INNER_STROKE_WIDTH / 2) + INNER_PADDING
            for who, rasci in self.__who.items():
                elements.append(svg.Text(x=width / 2, y=next_y + LINE_HEIGHT/2,
                                dominant_baseline="middle", text_anchor="middle", elements=[who], fill=WHO_COLOR))
                next_y = next_y + LINE_HEIGHT
            next_y + INNER_PADDING

        if with_what_height > 0:
            next_y = next_y + (INNER_STROKE_WIDTH / 2)
            elements.append(svg.Path(d=f"M{STROKE_WIDTH / 2},{next_y} L{width - STROKE_WIDTH / 2},{
                            next_y}Z", stroke=ATTACHMENT_COLOR, stroke_width=INNER_STROKE_WIDTH))
            next_y = next_y + (INNER_STROKE_WIDTH / 2) + INNER_PADDING
            for with_what in self.__with_what:
                elements.append(svg.Text(x=width / 2, y=next_y + LINE_HEIGHT/2,
                                dominant_baseline="middle", text_anchor="middle", elements=[with_what], fill=WITH_WHAT_COLOR))
                next_y = next_y + LINE_HEIGHT

        return svg.G(elements=elements)
        # return svg.G(elements=)
