"""
Contiguity Test — verifies that allocation is STRICTLY contiguous.
Each segment must fit entirely inside ONE free block.
"""

from memory_manager import MemoryManager

def test_contiguity_enforcement():
    print("=" * 70)
    print("CONTIGUITY TEST: Allocation must fit in ONE block")
    print("=" * 70)
    
    # ── Scenario 1: Non-adjacent free blocks ─────────────────────────────────
    print("\n[Scenario 1] Non-adjacent free blocks: 200 KB | 100 KB | 200 KB")
    print("             Request: 250 KB")
    print("             Expected: FAIL (no single block >= 250 KB)")
    print()
    
    mm = MemoryManager()
    mm.initialize_memory(700)
    mm.set_coalescing_mode("immediate")
    mm.memory = [
        {"name": "Free",   "size": 200, "type": "free"},
        {"name": "P1 X",   "size": 100, "type": "used"},  # separator
        {"name": "Free",   "size": 100, "type": "free"},
        {"name": "P2 X",   "size": 100, "type": "used"},  # separator
        {"name": "Free",   "size": 200, "type": "free"},
    ]
    
    success, base, size = mm.allocate_segment("Test", 250)
    print(f"Result: success={success}")
    
    if not success:
        print("✅ PASS: Correctly rejected (cannot span multiple blocks)")
    else:
        print("❌ FAIL: Incorrectly allocated across non-contiguous blocks!")
        return False
    
    # ── Scenario 2: Adjacent free blocks (deferred mode) ─────────────────────
    print("\n[Scenario 2] Adjacent free blocks: 200 KB | 100 KB (touching)")
    print("             Request: 250 KB")
    print("             Mode: Deferred")
    print("             Expected: FAIL first → merge → SUCCESS on retry")
    print()
    
    mm2 = MemoryManager()
    mm2.initialize_memory(500)
    mm2.set_coalescing_mode("deferred")
    mm2.memory = [
        {"name": "Free", "size": 200, "type": "free"},
        {"name": "Free", "size": 100, "type": "free"},  # adjacent to above
        {"name": "P1 X", "size": 200, "type": "used"},
    ]
    
    success2, base2, size2 = mm2.allocate_segment("Test", 250)
    print(f"Result: success={success2}, base={base2}")
    
    if success2 and base2 == 0:
        print("✅ PASS: Deferred merge created contiguous 300 KB block")
    else:
        print("❌ FAIL: Deferred merge did not work correctly")
        return False
    
    # ── Scenario 3: Total free space sufficient but fragmented ───────────────
    print("\n[Scenario 3] Fragmented: 100 KB | 100 KB | 100 KB | 100 KB")
    print("             Total free: 400 KB")
    print("             Request: 250 KB")
    print("             Expected: FAIL (no single block >= 250 KB)")
    print()
    
    mm3 = MemoryManager()
    mm3.initialize_memory(800)
    mm3.set_coalescing_mode("immediate")
    mm3.memory = [
        {"name": "Free", "size": 100, "type": "free"},
        {"name": "P1 X", "size": 100, "type": "used"},
        {"name": "Free", "size": 100, "type": "free"},
        {"name": "P2 X", "size": 100, "type": "used"},
        {"name": "Free", "size": 100, "type": "free"},
        {"name": "P3 X", "size": 100, "type": "used"},
        {"name": "Free", "size": 100, "type": "free"},
        {"name": "P4 X", "size": 100, "type": "used"},
    ]
    
    success3, base3, size3 = mm3.allocate_segment("Test", 250)
    print(f"Result: success={success3}")
    
    if not success3:
        print("✅ PASS: Correctly rejected despite 400 KB total free")
    else:
        print("❌ FAIL: Incorrectly allocated across fragmented blocks!")
        return False
    
    # ── Scenario 4: Exact fit ────────────────────────────────────────────────
    print("\n[Scenario 4] Exact fit: 250 KB block available")
    print("             Request: 250 KB")
    print("             Expected: SUCCESS")
    print()
    
    mm4 = MemoryManager()
    mm4.initialize_memory(500)
    mm4.set_coalescing_mode("immediate")
    mm4.memory = [
        {"name": "Free", "size": 250, "type": "free"},
        {"name": "P1 X", "size": 250, "type": "used"},
    ]
    
    success4, base4, size4 = mm4.allocate_segment("Test", 250)
    print(f"Result: success={success4}, base={base4}")
    
    if success4 and base4 == 0:
        print("✅ PASS: Exact fit allocation succeeded")
    else:
        print("❌ FAIL: Exact fit should have succeeded")
        return False
    
    print("\n" + "=" * 70)
    print("ALL CONTIGUITY TESTS PASSED ✅")
    print("Allocation is strictly contiguous — no cross-block placement")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_contiguity_enforcement()
    exit(0 if success else 1)
