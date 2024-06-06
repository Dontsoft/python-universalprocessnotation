import pytest
from src.universalprocessnotation import Block, Process

def init_process(block_count: int = 0, name : str = "Name"):
    process = Process(name)
    if block_count > 0:
        for i in range(block_count):
            process.add_block(f"{name} Block {i}")
    return process

def test_block_process_none():
    with pytest.raises(Exception):
        Block(None, "", None)

def test_block_activity():
    process = Process("Name")
    assert process.add_block("Block 1").activity() == "Block 1"

def test_block_process_comparison():
    process = Process("Name")
    block1 = process.add_block("Block 1")
    block2 = Block(process, "Block 2")
    assert block1.process() == block2.process()

def test_block_attachment():
    process = Process("Name")
    block = process.add_block("Block 1")
    assert not block.has_attachment()
    block.set_attachment(False)
    assert not block.has_attachment()
    block.set_attachment(True)
    assert block.has_attachment()
    block.unset_attachment()
    assert not block.has_attachment()

def test_block_trigger():
    process = Process("Name")
    block = process.add_block("Block 1")
    assert block.triggers() is None
    block.add_trigger("Trigger")
    assert "Trigger" in block.triggers()
    block.unset_triggers()
    assert block.triggers() is None
    block.set_triggers(["Trigger", "Trigger 2"])
    assert "Trigger 2" in block.triggers()

def test_block_whos():
    process = Process("Name")
    block = process.add_block("Block 1")
    
    block.add_who("Who 1")
    assert len(block.whos()) == 1
    assert "Who 1" in block.whos()

    block.add_who("Who 2")
    assert len(block.whos()) == 2
    assert "Who 2" in block.whos()

    block.remove_who("Who 1")
    assert len(block.whos()) == 1
    assert "Who 2" in block.whos()
    assert "Who 1" not in block.whos()

    with pytest.raises(Exception):
        block.remove_who("Who 1")

    block.clear_whos()
    assert len(block.whos()) == 0
    assert "Who 1" not in block.whos()
    assert "Who 2" not in block.whos()

    whos = ["Who 1", "Who 2"]

    block.set_whos(whos)
    assert block.whos() is whos
    assert len(block.whos()) == 2
    assert "Who 1" in block.whos()
    assert "Who 2" in block.whos()

    block.clear_whos()
    assert len(block.whos()) == 0
    assert "Who 1" not in block.whos()
    assert "Who 2" not in block.whos()

    whos = ["Who 1", "Who 2"]

    block.set_whos(whos, copy=True)
    assert block.whos() is not whos
    assert len(block.whos()) == 2
    assert "Who 1" in block.whos()
    assert "Who 2" in block.whos()


    
def test_block_with_whats():
    process = Process("Name")
    block = process.add_block("Block 1")
    
    block.add_with_what("With What 1")
    assert len(block.with_whats()) == 1
    assert "With What 1" in block.with_whats()

    block.add_with_what("With What 2")
    assert len(block.with_whats()) == 2
    assert "With What 2" in block.with_whats()

    block.remove_with_what("With What 1")
    assert len(block.with_whats()) == 1
    assert "With What 2" in block.with_whats()
    assert "With What 1" not in block.with_whats()

    with pytest.raises(Exception):
        block.remove_with_what("With What 1")

    block.clear_with_whats()
    assert len(block.with_whats()) == 0
    assert "With What 1" not in block.with_whats()
    assert "With What 2" not in block.with_whats()

    with_whats = ["With What 1", "With What 2"]

    block.set_with_whats(with_whats)
    assert block.with_whats() is with_whats
    assert len(block.with_whats()) == 2
    assert "With What 1" in block.with_whats()
    assert "With What 2" in block.with_whats()

    block.clear_with_whats()
    assert len(block.with_whats()) == 0
    assert "With What 1" not in block.with_whats()
    assert "With What 2" not in block.with_whats()

    with_whats = ["With What 1", "With What 2"]

    block.set_with_whats(with_whats, copy=True)
    assert block.with_whats() is not with_whats
    assert len(block.with_whats()) == 2
    assert "With What 1" in block.with_whats()
    assert "With What 2" in block.with_whats()


def test_block_subprocess_success():
    process1 = init_process(10, "Process 1")
    process2 = init_process(10, "Process 2")
    block1_1 = process1.find_block("Process 1 Block 1")
    block1_1.set_subprocess(process2)
    assert block1_1.subprocess() is not None
    assert block1_1.subprocess().name() == "Process 2"


def test_block_subprocess_same_process_exception():
    process1 = init_process(10, "Process 1")
    block1_1 = process1.find_block("Process 1 Block 1")
    with pytest.raises(Exception):
        block1_1.set_subprocess(process1)
    assert block1_1.subprocess() is None

def test_block_subprocess_part_of_subprocess_exception():
    process1 = init_process(10, "Process 1")
    process2 = init_process(10, "Process 2")
    process3 = init_process(10, "Process 3")
    block1_1 = process1.find_block("Process 1 Block 1")
    block2_1 = process2.find_block("Process 2 Block 1")
    block3_1 = process3.find_block("Process 3 Block 1")
    block3_1.set_subprocess(process1)
    block2_1.set_subprocess(process3)
    with pytest.raises(Exception):
        block1_1.set_subprocess(process2)
    assert block1_1.subprocess() is None

def test_block_connect():
    process = init_process(2, "Process")
    block0 = process.find_block("Process Block 0")
    block1 = process.find_block("Process Block 1")
    block0.connect("Why", block1)
    block1.connect("Back", block0)
    block1.connect_end("End")

    assert len(block0.links()) == 1
    assert len(block0.from_links()) == 1
    assert len(block1.links()) == 2
    assert len(block1.from_links()) == 1


def test_block_connect_different_processes():
    process1 = init_process(1, "Process 1")
    block1_0 = process1.find_block("Process 1 Block 0")
    
    process2 = init_process(1, "Process 2")
    block2_0 = process2.find_block("Process 2 Block 0")
    
    with pytest.raises(Exception):
        block1_0.connect("Test", block2_0)

