import universalprocessnotation
import universalprocessnotation.process

process = universalprocessnotation.process.Process("Test")
block1 = process.add_block("Test")
block2 = process.add_block("Test 2")
block3 = process.add_block("Test 3")
block4 = process.add_block("Test 4")

block1.set_trigger("Trigger")
block1.set_attachment(True)
block1.connect("Because", block2)
block2.connect("Because 2", block3)
block3.connect("Because 3", block4)
block3.connect("Because 4", block2)
block4.connect_end("Because End")

print(block1)