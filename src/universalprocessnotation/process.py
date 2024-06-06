from typing import List, Optional, Tuple

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
        self, block: Optional["Block"] = None, current_list: Optional[List["Block"]] = None
    ) -> List["Block"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        if current_list is None:
            current_list = []
        if block is None or block in current_list:
            return current_list
        current_list.append(block)
        for connected_block in block.connected_blocks(include_subprocess=True):
            current_list = self.__recursive_blocks(
                connected_block, current_list)
        return current_list

    def blocks(self, include_subprocesses: bool = False) -> List["Block"]:
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

    def remove_block(self, block: "Block"):
        self.__blocks.remove(block)

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

    def find_block_by_id(self, block_id: int, search_subprocesses: bool = False) -> "Block":
        for block in self.blocks(search_subprocesses):
            if block.get_id() == block_id:
                return block
        raise Exception(f"Block with id '{block_id}' not found")

    def find_block(self, block_activity: str, search_subprocesses: bool = False) -> "Block":
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

    def validate(self) -> bool:
        valid = True
        any_trigger = False
        any_end = False
        invalid_blocks = []
        graphs = []
        for block in self.blocks():
            if block.triggers() is not None and len(block.triggers()) > 0:
                any_trigger = True
            for link in block.links():
                if link.to_block is None:
                    any_end = True
            if len(block.links()) == 0 or (len(block.from_links()) == 0 and (block.triggers() is None is len(block.triggers()) == 0)):
                invalid_blocks.append(block)
            graph = sorted(block.all_connected_blocks(),
                           key=lambda x: x.get_id())
            found_in_list = False
            for g in graphs:
                if graph == g:
                    found_in_list = True
            if not found_in_list:
                graphs.append(graph)
        if not any_trigger:
            print(" - Missing at least one trigger")
            valid = False
        if not any_end:
            print(" - Missing at least one end")
            valid = False
        if len(invalid_blocks) > 0:
            print(" - Invalid blocks found")
            valid = False
            for i, block in enumerate(invalid_blocks):
                print(" --", block)
        if len(graphs) > 1:
            print(" - Multiple distinct graphs found in process, only one is allowed")
            valid = False
            for i, graph in enumerate(graphs):
                print(" -- Graph", i + 1, [block.activity()
                      for block in graph])
        return valid

    def _paths_between_blocks(from_block: "Block", to_block: Optional["Block"], include_inverted_from_links : bool = True, paths : Optional[List[List[Block]]] = None, path: Optional[List[Block]] = None) -> List[List[Block]]:
        if paths is None:
            paths = []
        if path is None:
            path = []
        if from_block in path:
            # Current path is cycle
            return paths
        if from_block is to_block or (from_block is None and to_block is None):
            # Found to_block, appending to current path and appending to path list
            path.append(from_block)
            paths.append(path)
            return paths

        if from_block is None:
            # Found end, no continuation
            return paths
        path.append(from_block)
        if include_inverted_from_links:
            for link in from_block.links_with_inverted_from_links():
                paths = Process._paths_between_blocks(
                    link.to_block, to_block, include_inverted_from_links, paths, path.copy())
        else:
            for link in from_block.links():
                paths = Process._paths_between_blocks(
                    link.to_block, to_block, include_inverted_from_links, paths, path.copy())

        return paths

    def _longest_path_between_blocks(from_block: "Block", to_block: Optional["Block"], include_inverted_from_links: bool = True) -> List[Block]:
        _max_length = 0
        _path = None
        for path in Process._paths_between_blocks(from_block, to_block, include_inverted_from_links):
            if len(path) > _max_length:
                _max_length = len(path)
                _path = path
        return _path

    def _longest_path_between_block_and_end(from_block: "Block", include_inverted_from_links: bool = True) -> List[Block]:
        return Process._longest_path_between_blocks(from_block, None, include_inverted_from_links)

    def _longest_path_between_blocks_length(from_block: "Block", to_block: Optional["Block"], include_inverted_from_links: bool = True) -> int:
        return len(Process._longest_path_between_blocks(from_block, to_block, include_inverted_from_links))

    def _longest_path_between_block_and_end_length(from_block: "Block", include_inverted_from_links: bool = True) -> int:
        return len(Process._longest_path_between_block_and_end(from_block, include_inverted_from_links))

    # def _generate_layers(self, block: "Block", layer: int,
    #                      parsed_blocks: List[int] = None, layers: List[List[int]] = None) -> Tuple[List[int], List[List[int]]]:
    #     if parsed_blocks is None:
    #         parsed_blocks = []
    #     if layers is None:
    #         layers = []
    #     if block is None or block.get_id() in parsed_blocks:
    #         return (parsed_blocks, layers)
    #     while len(layers) < layer + 1:
    #         layers.append([])
    #     parsed_blocks.append(block.get_id())
    #     layers[layer].append(block.get_id())
    #     for link in block.links_with_inverted_from_links():
    #         # print("Connected", layer + 1, connected_block.activity())
    #         parsed_blocks, layers = Process._generate_layers(
    #             link.to_block, layer + Process._longest_path_between_blocks(block, link.to_block) - 1, parsed_blocks, layers)
    #     return (parsed_blocks, layers)


    def _generate_layers(self, block: "Block") ->  List[List[int]]:
        
        parsed_blocks = []
        layers: List[List[int]] = []
        all_end_paths = Process._paths_between_blocks(block, None, False)
        end_paths = []
        for end_block in [path[-2] for path in all_end_paths if path is not None]:
            fitting_paths = [path for path in all_end_paths if path[-2] is end_block]
            max_len = 0
            longest_path = None
            for path in fitting_paths:
                if len(path) > max_len:
                    max_len = len(path)
                    longest_path = path
            end_paths.append(longest_path)
        for path in end_paths:
            for i, pathblock in enumerate(path):
                if pathblock is None or pathblock in parsed_blocks:
                    continue
                if len(layers) < (i + 1):
                    layers.append([])
                layers[i].append(pathblock.get_id())
                parsed_blocks.append(pathblock)
        for other_block in self.__blocks:
            if other_block is block:
                continue
            path = Process._longest_path_between_blocks(block, other_block, False)
            if path is not None:
                for i, pathblock in enumerate(path):
                    if pathblock is None or pathblock in parsed_blocks: 
                        continue
                    if len(layers) < (i + 1):
                        layers.append([])
                    print("Layer",i, pathblock)
                    layers[i].append(pathblock.get_id())
                    parsed_blocks.append(pathblock)
        all_layer_blocks = [block for layer in layers for block in layer]
        if set(all_layer_blocks) != set(self.__blocks):
            for other_block in self.__blocks:
                if other_block is block:
                    continue
                path = Process._longest_path_between_blocks(
                    block, other_block, True)
                for i, pathblock in enumerate(path):
                    if pathblock is None or pathblock in parsed_blocks:
                        continue
                    if len(layers) < (i + 1):
                        layers.append([])
                    layers[i].append(pathblock.get_id())
                    parsed_blocks.append(pathblock)

        return layers

    def to_svg(self, file_path: str):
        if not self.validate():
            raise Exception("Invalid processes can not be exported")
        # 1. Find first entry block
        # 2. From there inverse all links
        entry_block = None
        shortest_path = -1
        
        for block in self.blocks():
            if block.triggers() is not None:
                path_length = Process._longest_path_between_block_and_end_length(block)
                if path_length < shortest_path or shortest_path == -1:
                    entry_block = block
                    shortest_path = path_length
        if entry_block is None:
            raise Exception("Unexcepted, but no entry block was found")

        layers = self._generate_layers(entry_block)
        for layer in layers:
            print([self.find_block_by_id(i).activity() for i in layer])

        # print(layers)
