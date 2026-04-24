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

def test_coalescing_modes():
    print("=== Testing Coalescing Modes ===")

    # ── Shared scenario ──────────────────────────────────────────────────────
    # Memory: 1000 KB
    # P1: Code=200, Data=100, Stack=50  → 350 KB  (base 0)
    # P2: Code=150, Data=80,  Stack=30  → 260 KB  (base 350)
    # P3: Code=100, Data=50,  Stack=20  → 170 KB  (base 610)
    # Remaining free: 220 KB            (base 780)
    #
    # After deleting P2 the freed space is three adjacent blocks:
    #   150 KB | 80 KB | 30 KB  (total 260 KB, but no single block ≥ 250 KB)
    #
    # Allocating 250 KB:
    #   Immediate → blocks already merged into one 260 KB block → succeeds directly
    #   Deferred  → largest block is 150 KB → FAILS first attempt
    #               → merge triggered → 260 KB block created → succeeds on retry

    # ── Test 1: Immediate Coalescing ─────────────────────────────────────────
    print("\n--- Test 1: Immediate Coalescing ---")
    mm = MemoryManager()
    mm.initialize_memory(1000)
    mm.set_coalescing_mode("immediate")

    st = SegmentTable()
    fc = FragmentationCalculator()
    pm = ProcessManager(mm, st, fc)

    pm.create_process("P1", 200, 100, 50)
    pm.create_process("P2", 150, 80, 30)
    pm.create_process("P3", 100, 50, 20)
    print(f"After creating P1, P2, P3: {len(mm.get_memory_blocks())} blocks")

    pm.delete_process("P2")
    blocks = mm.get_memory_blocks()
    free_sizes = [b["size"] for b in blocks if b["type"] == "free"]
    print(f"After deleting P2 (immediate): {len(blocks)} blocks, free blocks: {free_sizes}")
    print(f"  → Largest free block: {max(free_sizes)} KB  (expect 260 KB — already merged)")

    # 250 KB fits inside the merged 260 KB block → no merge print expected
    success, base, size = mm.allocate_segment("P4 Code", 250)
    print(f"Allocate 250 KB: Success={success}, Base={base}  (expect: direct success, no merge message)")

    assert success, "FAIL: immediate mode should allocate 250 KB directly"
    assert max(free_sizes) >= 250, "FAIL: merged block should be >= 250 KB"

    # ── Test 2: Deferred Coalescing ──────────────────────────────────────────
    print("\n--- Test 2: Deferred Coalescing ---")
    mm2 = MemoryManager()
    mm2.initialize_memory(1000)
    mm2.set_coalescing_mode("deferred")

    st2 = SegmentTable()
    fc2 = FragmentationCalculator()
    pm2 = ProcessManager(mm2, st2, fc2)

    pm2.create_process("P1", 200, 100, 50)
    pm2.create_process("P2", 150, 80, 30)
    pm2.create_process("P3", 100, 50, 20)
    print(f"After creating P1, P2, P3: {len(mm2.get_memory_blocks())} blocks")

    pm2.delete_process("P2")
    blocks2 = mm2.get_memory_blocks()
    free_sizes2 = [b["size"] for b in blocks2 if b["type"] == "free"]
    print(f"After deleting P2 (deferred): {len(blocks2)} blocks, free blocks: {free_sizes2}")
    print(f"  → Largest free block: {max(free_sizes2)} KB  (expect 150 KB — NOT yet merged)")

    ext_frag = fc2.calculate_external_fragmentation(blocks2)
    print(f"  → External fragmentation: {ext_frag} KB  (expect > 0)")

    assert max(free_sizes2) < 250, \
        "FAIL: deferred mode must NOT merge on deallocation — no single block should be >= 250 KB yet"
    assert ext_frag > 0, "FAIL: deferred mode should show external fragmentation before merge"

    # 250 KB > largest free block (150 KB) → first attempt MUST fail
    # → merge print should appear → retry succeeds
    print("\nAttempting to allocate 250 KB (expect: fail → merge → retry → success):")
    success2, base2, size2 = mm2.allocate_segment("P4 Code", 250)
    print(f"Allocate 250 KB: Success={success2}, Base={base2}  (expect: True after deferred merge)")

    assert success2, "FAIL: deferred mode should succeed after lazy merge"

    blocks_final = mm2.get_memory_blocks()
    print(f"Memory after allocation: {blocks_final}")

    print("\n✅ Coalescing modes test PASSED")
    print("   Immediate: merged on deallocation → direct success, no merge message")
    print("   Deferred:  unmerged after deallocation → fails first → merge triggered → retry succeeds")
    print()

if __name__ == "__main__":
    print("Testing all modules independently...\n")
    
    test_memory_manager()
    test_segment_table()
    test_address_translator()
    test_fragmentation_calculator()
    test_process_manager()
    test_coalescing_modes()
    
    print("=== All tests completed ===")
    print("If no errors above, all modules are working correctly!")
    print("Now run: python main.py")
