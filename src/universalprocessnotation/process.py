from typing import List, Optional, Tuple
import svg
import math
from .block import Block, Link
from .util import *

BLOCK_PADDING = 32

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

    def add_block(self, activity: str, triggers: Optional[List[str]] = None) -> "Block":
        """_summary_

        Args:
            activity (str): _description_
            trigger (Optional[str], optional): _description_. Defaults to None.

        Returns:
            Block: _description_
        """
        return Block(self, activity, triggers)

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

    def _paths_between_blocks(from_block: "Block", to_block: Optional["Block"], include_inverted_from_links: bool = True, paths: Optional[List[List[Block]]] = None, path: Optional[List[Block]] = None) -> List[List[Block]]:
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

    def _generate_layers(self, block: "Block") -> List[List["Block"]]:
        parsed_blocks = []
        layers: List[List["Block"]] = []
        all_end_paths = Process._paths_between_blocks(block, None, False)
        end_paths = []
        for end_block in [path[-2] for path in all_end_paths if path is not None]:
            fitting_paths = [
                path for path in all_end_paths if path[-2] is end_block]
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
                layers[i].append(pathblock)
                parsed_blocks.append(pathblock)
        for other_block in self.__blocks:
            if other_block is block:
                continue
            path = Process._longest_path_between_blocks(
                block, other_block, False)
            if path is not None:
                for i, pathblock in enumerate(path):
                    if pathblock is None or pathblock in parsed_blocks:
                        continue
                    if len(layers) < (i + 1):
                        layers.append([])
                    layers[i].append(pathblock)
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
                    layers[i].append(pathblock)
                    parsed_blocks.append(pathblock)

        return layers

    def _in_coords(y: float, height: int, block: "Block"):
        in_count = (len(block.triggers()) if block.triggers() is not None else 0) + len(block.from_links())
        in_spacing = height / (in_count + 1)
        return [(y + in_spacing * (i + 1)) for i in list(range(in_count))]
    
    def _out_coords(y: float, height: int, block: "Block"):
        out_count = len(block.links())
        out_spacing = height / (out_count + 1)
        return [(y + out_spacing * (i + 1)) for i in list(range(out_count))]

    def to_svg(self, file_path: str, *, padding=(20, 20)):
        if not self.validate():
            raise Exception("Invalid processes can not be exported")
        entry_block = None
        shortest_path = -1

        for block in self.blocks():
            if block.triggers() is not None:
                path_length = Process._longest_path_between_block_and_end_length(
                    block)
                if path_length < shortest_path or shortest_path == -1:
                    entry_block = block
                    shortest_path = path_length
        if entry_block is None:
            raise Exception("Unexcepted, but no entry block was found")

        layers = self._generate_layers(entry_block)
        layer_widths = []
        layer_text_left_widths = []
        layer_text_right_widths = []
        layer_paddings = []
        layer_heights = []
        row_heights = []

        layer_output_count = 0
        for i, layer in enumerate(layers):
            layer_width = 0
            layer_text_left_width = 0
            layer_text_right_width = 0
            layer_height = 0
            layer_input_count = 0
            current_layer_output_count = 0
            for block in layer:
                layer_width = max(layer_width, block.calculate_width())
                layer_text_left_width = max(layer_text_left_width, block.calculate_input_textbox_width())
                layer_text_right_width = max(
                    layer_text_right_width, block.calculate_output_textbox_width())
                current_layer_output_count = current_layer_output_count + len(
                    block.links())
                layer_input_count = layer_input_count + len(block.from_links()) + (0 if block.triggers() is None else len(block.triggers()))
            layer_paddings.append(max(layer_input_count, layer_output_count) * (CHARHEIGHT * 2 + INNER_STROKE_WIDTH))
            layer_output_count = current_layer_output_count
            for row, block in enumerate(layer):
                block_height = block.calculate_height(layer_width)
                if len(row_heights) <= row:
                    row_heights.append(block_height)
                else:
                    row_heights[row] = max(row_heights[row], block_height)
            layer_widths.append(layer_width)
            layer_text_left_widths.append(layer_text_left_width)
            layer_text_right_widths.append(layer_text_right_width)
        svg_height = sum(row_heights) + (len(row_heights) - 1) * BLOCK_PADDING + 2 * STROKE_WIDTH
        svg_width = sum(layer_widths) + sum(layer_text_right_widths) + sum(layer_text_left_widths) + sum(layer_paddings) + 2 * STROKE_WIDTH
        elements = []
        x = 0
        block_coords_lut = {}
        for i, layer in enumerate(layers):
            layer_width = layer_widths[i]
            layer_padding = layer_paddings[i]
            layer_text_left_width = layer_text_left_widths[i]
            layer_text_right_width = layer_text_right_widths[i]
            y = 0
            for row, block in enumerate(layer):
                row_height = row_heights[row]
                height = block.calculate_height(layer_width)
                block_y = y + (row_height - height) / 2
                block_coords_lut[block.get_id()] = {
                    "x": x + layer_text_left_width,
                    "y": block_y,
                    "height": height,
                    "width": layer_width
                }
                elements.append(svg.G(transform=f"translate({x + layer_text_left_width}, {block_y})", elements=[
                                block.to_svg(width=layer_width, height=height)]))
                y = y + row_height + BLOCK_PADDING
            x = x + layer_width + layer_padding + layer_text_right_width
        
        defs = [svg.Defs(elements=[svg.Marker(id="arrow", viewBox="0 0 10 10", refX="5", refY="5", markerWidth="5",
                 markerHeight="5", orient="auto-start-reverse", elements=[svg.Path(d="M 0 0 L 10 5 L 0 10 z")])])]
        
        def to_link_sort(link : "Link"):
            if link.to_block is None:
                return float('inf')
            if link.to_block is link.from_block:
                return float('-inf')
            from_coords = block_coords_lut[link.from_block.get_id()]
            from_y, from_x = from_coords["y"], from_coords["x"]
            to_coords = block_coords_lut[link.to_block.get_id()]
            to_y, to_x = to_coords["y"], to_coords["x"]
            return math.sqrt(math.pow(from_x - to_x, 2) + math.pow(from_y - to_y, 2))

        def from_link_sort(link: "Link"):
            if link.to_block is link.from_block:
                return float('-inf')
            from_coords = block_coords_lut[link.from_block.get_id()]
            from_y, from_x = from_coords["y"], from_coords["x"]
            to_coords = block_coords_lut[link.to_block.get_id()]
            to_y, to_x = to_coords["y"], to_coords["x"]
            return math.sqrt(math.pow(from_x - to_x, 2) + math.pow(from_y - to_y, 2))

        for i, layer in enumerate(layers):
            layer_text_right_width = layer_text_right_widths[i]
            layer_text_left_width = layer_text_left_widths[i]
            for row, block in enumerate(layer):
                coords = block_coords_lut[block.get_id()]
                x, y, width, height = coords["x"], coords["y"], coords["width"], coords["height"]
                out_x = x + layer_width + INNER_STROKE_WIDTH / 2.0
                in_coords = Process._in_coords(y, height, block)
                out_coords = Process._out_coords(y, height, block)

                links = sorted(block.links(), key=to_link_sort)
                triggers = block.triggers()
                if triggers is not None:
                    for i, trigger in enumerate(triggers):
                        in_y = in_coords[i]
                        in_x = x - layer_text_left_width
                        end_x = x - 5
                        elements.append(svg.Path(stroke=ATTACHMENT_COLOR, stroke_width=INNER_STROKE_WIDTH, d=f"M{
                                        in_x},{in_y} L{end_x},{in_y}", marker_end="url(#arrow)", fill="none"))
                for i, link in enumerate(links):
                    out_y = out_coords[i]
                    if link.to_block is None:
                        x = out_x + BLOCK_PADDING / 2.0
                        end_x = x - 5 + layer_text_right_width
                        elements.append(svg.Path(stroke=ATTACHMENT_COLOR, stroke_width=INNER_STROKE_WIDTH, d=f"M{
                                        out_x},{out_y} L{end_x},{out_y}", marker_end="url(#arrow)", fill="none"))
                    else:
                        to_block = link.to_block
                        to_block_coords = block_coords_lut[to_block.get_id()]
                        to_block_x, to_block_y, to_block_width, to_block_height = to_block_coords[
                            "x"], to_block_coords["y"], to_block_coords["width"], to_block_coords["height"]
                        to_block_in_coords = Process._in_coords(to_block_y, to_block_height, to_block)
                        to_block_trigger_count = (len(to_block.triggers()) if to_block.triggers() is not None else 0)
                        to_block_from_links = sorted(to_block.from_links(), key=from_link_sort)
                        link_index = to_block_trigger_count + to_block_from_links.index(link)
                        line_to_coords = []

                        line_to_coords.append((out_x + layer_text_right_width, out_y))


                        end_y = to_block_in_coords[link_index]
                        end_x = to_block_x - 5 - INNER_STROKE_WIDTH / 2
                        line_to_coords.append((end_x, end_y))
                        line_to_string = " ".join(f"L{x},{y}" for (x, y) in line_to_coords)
                        
                        elements.append(svg.Path(stroke=ATTACHMENT_COLOR, stroke_width=INNER_STROKE_WIDTH, d=f"M{out_x},{out_y} {line_to_string}" , marker_end="url(#arrow)", fill="none"))


        with open("out.svg", "w") as f:
            f.write(svg.SVG(style="text(font-family: sans-ferif)", width=svg_width, height=svg_height,
                            elements=defs + [svg.G(transform=f"translate({STROKE_WIDTH / 2.0} {STROKE_WIDTH / 2.0})", elements=elements)]).as_str())

        # print(layers)
