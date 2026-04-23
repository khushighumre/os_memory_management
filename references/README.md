# OS Memory Management Simulator - Modular Structure

## Project Overview
Educational simulator demonstrating Operating System memory management concepts including:
- Segmentation
- Internal & External Fragmentation
- Logical to Physical Address Translation
- First-Fit Allocation Algorithm

## File Structure

### 1. **memory_manager.py**
**Purpose**: Core memory operations
**OS Concepts**: 
- First-Fit Allocation Algorithm
- Dynamic Partitioning
- Memory Block Management

**Key Functions**:
- `initialize_memory(size)` - Sets up memory with given size
- `allocate_segment(name, size)` - Allocates memory using First-Fit
- `deallocate_process(name)` - Frees memory blocks
- `get_memory_blocks()` - Returns current memory structure

**Explanation Points**:
- How First-Fit searches for the first available free block
- Memory splitting when allocated size < free block size
- Memory structure as list of dictionaries

---

### 2. **segment_table.py**
**Purpose**: Segment table management for address translation
**OS Concepts**:
- Segment Table (stores base address and limit for each segment)
- Metadata storage for logical segments

**Key Functions**:
- `add_segment(process, segment, base, size)` - Adds entry to table
- `find_segment(process, segment)` - Searches for segment
- `remove_process(name)` - Removes all segments of a process
- `get_all_segments()` - Returns complete table

**Explanation Points**:
- Each process has multiple segments (Code, Data, Stack)
- Segment table stores base address for address translation
- How OS maintains this table in real systems

---

### 3. **address_translator.py**
**Purpose**: Logical to physical address translation
**OS Concepts**:
- Address Translation in Segmentation
- Segment Limit Check (protection)
- Formula: Physical Address = Base + Offset

**Key Functions**:
- `translate(process, segment, offset)` - Converts logical to physical address

**Explanation Points**:
- Logical address = (Segment, Offset)
- Validation: offset must be < segment size
- Segmentation Fault when offset exceeds limit
- How CPU uses segment table for translation

---

### 4. **fragmentation_calculator.py**
**Purpose**: Calculate memory fragmentation
**OS Concepts**:
- Internal Fragmentation (waste within allocated blocks)
- External Fragmentation (scattered free memory)

**Key Functions**:
- `add_internal_fragmentation(allocated, requested)` - Tracks internal waste
- `calculate_external_fragmentation(memory)` - Calculates scattered free blocks
- `get_internal_fragmentation()` - Returns total internal fragmentation

**Explanation Points**:
- Internal: Allocated size > Requested size (due to fixed block allocation)
- External: Free memory scattered in small non-contiguous blocks
- Why external fragmentation prevents large allocations

---

### 5. **process_manager.py**
**Purpose**: High-level process operations
**OS Concepts**:
- Process Memory Segmentation (Code, Data, Stack)
- Process lifecycle (creation, deletion)

**Key Functions**:
- `create_process(name, code, data, stack)` - Creates process with 3 segments
- `delete_process(name)` - Removes process and frees memory

**Explanation Points**:
- Why processes are divided into segments
- Code segment: program instructions
- Data segment: global variables
- Stack segment: function calls and local variables
- Integration of memory manager, segment table, and fragmentation calculator

---

### 6. **memory_visualizer.py**
**Purpose**: Visual representation of memory
**OS Concepts**:
- Memory partitioning visualization
- Address space representation

**Key Functions**:
- `draw_memory_blocks(memory)` - Draws rectangles on canvas

**Explanation Points**:
- Blue blocks = allocated segments
- Gray blocks = free memory
- Height proportional to size
- Shows address ranges for each block

---

### 7. **main.py**
**Purpose**: GUI application integrating all modules
**Components**:
- Step 1: Memory Initialization
- Step 2: Process Management (Add/Delete)
- Step 3: Dashboard (Visualization, Segment Table, Address Translation)

**Explanation Points**:
- How all modules work together
- User workflow through the simulator
- Real-time updates of memory state

---

## How to Run
```bash
python main.py
```

## Workflow
1. **Initialize Memory**: Set total memory size (e.g., 1000 KB)
2. **Add Processes**: Create processes with Code, Data, Stack segments
3. **View Dashboard**: 
   - See memory visualization
   - Check fragmentation
   - View segment table
   - Translate addresses
4. **Delete Processes**: Free memory and observe fragmentation changes

## Key OS Concepts Demonstrated

### Segmentation
- Divides process memory into logical units
- Each segment has base address and size
- Allows non-contiguous memory allocation

### First-Fit Allocation
- Searches memory from beginning
- Allocates first free block that fits
- Simple but can cause external fragmentation

### Internal Fragmentation
- Occurs when allocated block > requested size
- Example: Request 25 KB, allocate 30 KB (10 KB blocks) → 5 KB wasted

### External Fragmentation
- Free memory scattered in small blocks
- Total free memory sufficient but not contiguous
- Example: 3 free blocks of 10 KB each, but can't allocate 25 KB

### Address Translation
- Logical address: (Segment, Offset)
- Physical address: Base[Segment] + Offset
- Protection: Offset must be < Segment Size

## Module Dependencies
```
main.py
├── memory_manager.py
├── segment_table.py
├── address_translator.py (uses segment_table)
├── fragmentation_calculator.py
├── process_manager.py (uses memory_manager, segment_table, fragmentation_calculator)
└── memory_visualizer.py
```

## Advantages of Modular Design
1. **Easy to Explain**: Each file focuses on one concept
2. **Easy to Test**: Test each module independently
3. **Easy to Extend**: Add new features without modifying existing code
4. **Clear Separation**: Each module has single responsibility
5. **Reusable**: Modules can be used in other projects
