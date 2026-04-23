# Quick Reference - Module Cheat Sheet

## File Purpose (One Line Each)

| File | Purpose |
|------|---------|
| **memory_manager.py** | Allocates and deallocates memory blocks (First-Fit) |
| **segment_table.py** | Stores segment metadata (base, size) for address translation |
| **address_translator.py** | Converts logical address to physical address |
| **fragmentation_calculator.py** | Calculates internal and external fragmentation |
| **process_manager.py** | Creates/deletes processes with 3 segments each |
| **memory_visualizer.py** | Draws memory blocks on canvas |
| **main.py** | GUI application integrating all modules |

---

## Key Functions Quick Reference

### memory_manager.py
```python
initialize_memory(size)              # Setup memory
allocate_segment(name, size)         # Allocate using First-Fit
deallocate_process(process_name)     # Free all segments of process
get_memory_blocks()                  # Return memory structure
```

### segment_table.py
```python
add_segment(process, segment, base, size)  # Add entry
find_segment(process, segment)             # Search entry
remove_process(process_name)               # Remove all entries
get_all_segments()                         # Return table
```

### address_translator.py
```python
translate(process, segment, offset)  # Logical → Physical
# Returns: (success, physical_address, message)
```

### fragmentation_calculator.py
```python
add_internal_fragmentation(allocated, requested)  # Track waste
calculate_external_fragmentation(memory_blocks)   # Calculate scattered free
get_internal_fragmentation()                      # Get total internal
```

### process_manager.py
```python
create_process(name, code, data, stack)  # Create with 3 segments
delete_process(name)                     # Delete and free memory
```

### memory_visualizer.py
```python
draw_memory_blocks(memory_blocks)  # Draw on canvas
```

---

## Data Structures

### Memory Block
```python
{
    "name": "P1 Code",    # Segment name or "Free"
    "size": 200,          # Size in KB
    "type": "used"        # "used" or "free"
}
```

### Segment Table Entry
```python
{
    "process": "P1",      # Process ID
    "segment": "Code",    # Segment type
    "base": 0,            # Base address
    "size": 200           # Segment size
}
```

---

## OS Concepts Mapping

### Segmentation
- **File**: segment_table.py
- **Concept**: Divide process into logical units (Code, Data, Stack)
- **Real OS**: x86 segment registers (CS, DS, SS)

### First-Fit Allocation
- **File**: memory_manager.py
- **Concept**: Allocate first free block that fits
- **Real OS**: Linux buddy allocator, malloc()

### Address Translation
- **File**: address_translator.py
- **Formula**: Physical = Base + Offset
- **Real OS**: MMU (Memory Management Unit)

### Internal Fragmentation
- **File**: fragmentation_calculator.py
- **Cause**: Allocated size > Requested size
- **Real OS**: Page internal fragmentation (4KB pages)

### External Fragmentation
- **File**: fragmentation_calculator.py
- **Cause**: Free memory scattered in small blocks
- **Real OS**: Solved by compaction or paging

---

## Common Scenarios

### Scenario 1: Add Process
1. User enters process details in GUI (main.py)
2. main.py calls process_manager.create_process()
3. process_manager calls memory_manager.allocate_segment() for each segment
4. memory_manager finds free block using First-Fit
5. process_manager calls segment_table.add_segment() to record base
6. process_manager calls frag_calculator.add_internal_fragmentation()
7. GUI updates visualization

### Scenario 2: Delete Process
1. User enters process name in GUI
2. main.py calls process_manager.delete_process()
3. process_manager calls memory_manager.deallocate_process()
4. memory_manager converts used blocks to free
5. process_manager calls segment_table.remove_process()
6. GUI updates showing increased fragmentation

### Scenario 3: Address Translation
1. User enters (Process, Segment, Offset) in GUI
2. main.py calls address_translator.translate()
3. address_translator calls segment_table.find_segment()
4. Validates: offset < segment size
5. Calculates: physical = base + offset
6. GUI displays result

---

## Testing Checklist

- [ ] Run `python test_modules.py` - all tests pass
- [ ] Run `python main.py` - GUI opens
- [ ] Initialize memory (e.g., 1000 KB)
- [ ] Add process P1 (200, 100, 50)
- [ ] Add process P2 (150, 80, 30)
- [ ] View dashboard - see visualization
- [ ] Check segment table - 6 entries (3 per process)
- [ ] Check fragmentation - internal > 0
- [ ] Translate address - P1, Data, 50
- [ ] Delete P1 - external fragmentation increases
- [ ] Restart - back to step 1

---

## Explanation Order for Presentation

1. **memory_manager.py** (Core allocation logic)
2. **segment_table.py** (Metadata storage)
3. **address_translator.py** (Address conversion)
4. **fragmentation_calculator.py** (Memory waste)
5. **process_manager.py** (High-level coordination)
6. **memory_visualizer.py** (Visual representation)
7. **main.py** (GUI integration)
8. **Live Demo** (Run application)

---

## Key Formulas

```
First-Fit Allocation:
  for each free_block in memory:
    if free_block.size >= requested_size:
      allocate from this block
      break

Address Translation:
  Physical Address = Base Address + Offset
  
Internal Fragmentation:
  Allocated Size - Requested Size
  
External Fragmentation:
  Sum of all free blocks - Largest free block

Allocated Size (with fixed blocks):
  ((requested + block_size - 1) // block_size) * block_size
```

---

## Module Dependencies Graph

```
main.py
  ├─→ memory_manager.py (no dependencies)
  ├─→ segment_table.py (no dependencies)
  ├─→ address_translator.py
  │     └─→ segment_table.py
  ├─→ fragmentation_calculator.py (no dependencies)
  ├─→ process_manager.py
  │     ├─→ memory_manager.py
  │     ├─→ segment_table.py
  │     └─→ fragmentation_calculator.py
  └─→ memory_visualizer.py (no dependencies)
```

---

## Advantages of This Design

1. **Modularity**: Each file = one responsibility
2. **Testability**: Test each module independently
3. **Clarity**: Easy to understand and explain
4. **Extensibility**: Add features without breaking existing code
5. **Reusability**: Use modules in other projects
6. **Educational**: Mirrors real OS architecture

---

## Quick Commands

```bash
# Test modules
python test_modules.py

# Run application
python main.py

# Check file structure
dir  # Windows
ls   # Linux/Mac
```
