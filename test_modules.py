"""
Test file to verify all modules work correctly
Run this to test modules independently before running GUI
"""

from memory_manager import MemoryManager
from segment_table import SegmentTable
from address_translator import AddressTranslator
from fragmentation_calculator import FragmentationCalculator
from process_manager import ProcessManager

def test_memory_manager():
    print("=== Testing Memory Manager ===")
    mm = MemoryManager()
    mm.initialize_memory(1000)
    print(f"Memory initialized: {mm.total_memory} KB")
    
    success, base, allocated = mm.allocate_segment("P1 Code", 200)
    print(f"Allocated P1 Code: Success={success}, Base={base}, Size={allocated}")
    
    success, base, allocated = mm.allocate_segment("P1 Data", 100)
    print(f"Allocated P1 Data: Success={success}, Base={base}, Size={allocated}")
    
    print(f"Memory blocks: {mm.get_memory_blocks()}")
    print()

def test_segment_table():
    print("=== Testing Segment Table ===")
    st = SegmentTable()
    st.add_segment("P1", "Code", 0, 200)
    st.add_segment("P1", "Data", 200, 100)
    st.add_segment("P1", "Stack", 300, 50)
    
    print(f"All segments: {st.get_all_segments()}")
    
    seg = st.find_segment("P1", "Data")
    print(f"Found segment P1 Data: {seg}")
    
    st.remove_process("P1")
    print(f"After removing P1: {st.get_all_segments()}")
    print()

def test_address_translator():
    print("=== Testing Address Translator ===")
    st = SegmentTable()
    st.add_segment("P1", "Code", 0, 200)
    st.add_segment("P1", "Data", 200, 100)
    
    at = AddressTranslator(st)
    
    success, addr, msg = at.translate("P1", "Data", 50)
    print(f"Translate P1 Data+50: {msg}")
    
    success, addr, msg = at.translate("P1", "Data", 150)
    print(f"Translate P1 Data+150: {msg}")
    print()

def test_fragmentation_calculator():
    print("=== Testing Fragmentation Calculator ===")
    fc = FragmentationCalculator()
    
    fc.add_internal_fragmentation(200, 195)
    fc.add_internal_fragmentation(100, 92)
    print(f"Internal fragmentation: {fc.get_internal_fragmentation()} KB")
    
    memory = [
        {"name": "P1 Code", "size": 200, "type": "used"},
        {"name": "Free", "size": 50, "type": "free"},
        {"name": "P2 Data", "size": 100, "type": "used"},
        {"name": "Free", "size": 30, "type": "free"},
        {"name": "Free", "size": 620, "type": "free"}
    ]
    
    ext_frag = fc.calculate_external_fragmentation(memory)
    print(f"External fragmentation: {ext_frag} KB")
    print()

def test_process_manager():
    print("=== Testing Process Manager ===")
    mm = MemoryManager()
    mm.initialize_memory(1000)
    
    st = SegmentTable()
    fc = FragmentationCalculator()
    pm = ProcessManager(mm, st, fc)
    
    success, msg = pm.create_process("P1", 200, 100, 50)
    print(f"Create P1: {msg}")
    
    success, msg = pm.create_process("P2", 150, 80, 30)
    print(f"Create P2: {msg}")
    
    print(f"Segment table: {st.get_all_segments()}")
    print(f"Memory blocks: {mm.get_memory_blocks()}")
    
    success, msg = pm.delete_process("P1")
    print(f"Delete P1: {msg}")
    
    print(f"Memory after deletion: {mm.get_memory_blocks()}")
    print()

if __name__ == "__main__":
    print("Testing all modules independently...\n")
    
    test_memory_manager()
    test_segment_table()
    test_address_translator()
    test_fragmentation_calculator()
    test_process_manager()
    
    print("=== All tests completed ===")
    print("If no errors above, all modules are working correctly!")
    print("Now run: python main.py")
