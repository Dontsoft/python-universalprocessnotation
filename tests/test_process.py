import pytest
from src.universalprocessnotation import Process

def init_process(block_count: int = 0, name : str = "Name"):
    process = Process(name)
    if block_count > 0:
        for i in range(block_count):
            process.add_block(f"{name} Block {i}")
    return process


def test_process_name():
    process = init_process()
    assert process.name() == "Name"

def test_process_block_count():
    process = init_process(10)
    assert len(process.blocks()) == 10

def test_process_find_block():
    process = init_process(10)
    for i in range(10):
        assert process.find_block(f"Name Block {i}").activity() == f"Name Block {i}"

def test_process_find_block_exception():
    process = init_process(10)
    with pytest.raises(Exception):
        process.find_block("Name Block 11")
    
def test_process_block_count_subprocess():
    process = init_process(10)
    block = process.find_block("Name Block 1")
    block.set_subprocess(init_process(10, "Subprocess"))
    assert len(process.blocks()) == 10
    assert len(process.blocks(include_subprocesses=True)) == 20

def test_process_block_find_block_subprocess():
    process = init_process(10)
    block = process.find_block("Name Block 1")
    block.set_subprocess(init_process(10, "Subprocess"))

    for i in range(10):
        assert process.find_block(f"Name Block {i}").activity() == f"Name Block {i}"

    for i in range(10):
        assert process.find_block(f"Name Block {i}", search_subprocesses=True).activity() == f"Name Block {i}"
        assert process.find_block(f"Subprocess Block {i}", search_subprocesses=True).activity() == f"Subprocess Block {i}"

    with pytest.raises(Exception):
        process.find_block("Name Block 11")

    with pytest.raises(Exception):
        process.find_block("Subprocess Block 11", search_subprocesses=True)

def test_process_block_find_block_exception_subprocess():
    process = init_process(10)
    block = process.find_block("Name Block 1")
    block.set_subprocess(init_process(10, "Subprocess"))

    with pytest.raises(Exception):
        process.find_block("Name Block 11")

    with pytest.raises(Exception):
        process.find_block("Subprocess Block 11", search_subprocesses=True)
    
    