# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    (GUI Application)                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Step 1:    │  │   Step 2:    │  │   Step 3:    │     │
│  │ Initialize   │→ │   Process    │→ │  Dashboard   │     │
│  │   Memory     │  │  Management  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────-───┘
                            │
                            │ Uses
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Core Modules Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ process_manager  │────────→│ memory_manager   │         │
│  │                  │         │                  │         │
│  │ - create_process │         │ - allocate       │         │
│  │ - delete_process │         │ - deallocate     │         │
│  └────────┬─────────┘         └──────────────────┘         │
│           │                                                  │
│           │                                                  │
│           ↓                                                  │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  segment_table   │←───────│ address_translator│         │
│  │                  │         │                  │         │
│  │ - add_segment    │         │ - translate      │         │
│  │ - find_segment   │         │                  │         │
│  └──────────────────┘         └──────────────────┘         │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ frag_calculator  │         │ memory_visualizer│         │
│  │                  │         │                  │         │
│  │ - internal_frag  │         │ - draw_blocks    │         │
│  │ - external_frag  │         │                  │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Module Interaction Flow

### Creating a Process

```
User Input (main.py)
    │
    │ Process: P1, Code: 200, Data: 100, Stack: 50
    ↓
process_manager.create_process()
    │
    ├─→ For each segment (Code, Data, Stack):
    │   │
    │   ├─→ memory_manager.allocate_segment()
    │   │       │
    │   │       ├─→ Search for free block (First-Fit)
    │   │       ├─→ Split block if needed
    │   │       └─→ Return (success, base_address, allocated_size)
    │   │
    │   ├─→ segment_table.add_segment()
    │   │       │
    │   │       └─→ Store (process, segment, base, size)
    │   │
    │   └─→ frag_calculator.add_internal_fragmentation()
    │           │
    │           └─→ Track (allocated_size - requested_size)
    │
    └─→ Return success message
        │
        ↓
    Update GUI
        │
        ├─→ memory_visualizer.draw_memory_blocks()
        ├─→ Update segment table display
        └─→ Update fragmentation labels
```

### Translating an Address

```
User Input (main.py)
    │
    │ Process: P1, Segment: Data, Offset: 50
    ↓
address_translator.translate()
    │
    ├─→ segment_table.find_segment(P1, Data)
    │       │
    │       └─→ Return {process: P1, segment: Data, base: 200, size: 100}
    │
    ├─→ Validate: offset < size?
    │       │
    │       ├─→ Yes: Calculate physical = base + offset
    │       │         = 200 + 50 = 250
    │       │
    │       └─→ No: Return "Segmentation Fault"
    │
    └─→ Return (success, physical_address, message)
        │
        ↓
    Display result in GUI
```

### Deleting a Process

```
User Input (main.py)
    │
    │ Process: P1
    ↓
process_manager.delete_process()
    │
    ├─→ memory_manager.deallocate_process(P1)
    │       │
    │       └─→ Convert all "P1 *" blocks to "Free"
    │
    ├─→ segment_table.remove_process(P1)
    │       │
    │       └─→ Remove all entries with process=P1
    │
    └─→ Return success message
        │
        ↓
    Update GUI
        │
        ├─→ memory_visualizer.draw_memory_blocks()
        ├─→ Update segment table display
        └─→ Recalculate fragmentation
```

## Data Flow Diagram

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       │ Input
       ↓
┌─────────────────────────────────────┐
│           main.py (GUI)             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Memory Initialization      │   │
│  │  Process Management         │   │
│  │  Dashboard Display          │   │
│  └─────────────────────────────┘   │
└──────┬──────────────────────────────┘
       │
       │ Commands
       ↓
┌─────────────────────────────────────┐
│      process_manager.py             │
│  (Orchestrates operations)          │
└──────┬──────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
       ↓              ↓              ↓              ↓
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ memory_  │  │ segment_ │  │  frag_   │  │ address_ │
│ manager  │  │  table   │  │calculator│  │translator│
└──────────┘  └──────────┘  └──────────┘  └──────────┘
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                      │
                      │ Data
                      ↓
              ┌──────────────┐
              │ memory_      │
              │ visualizer   │
              └──────────────┘
                      │
                      │ Display
                      ↓
              ┌──────────────┐
              │   Canvas     │
              │  (Visual)    │
              └──────────────┘
```

## Memory Structure Evolution

### Initial State
```
┌─────────────────────────────────────┐
│          Free (1000 KB)             │
└─────────────────────────────────────┘
```

### After Adding P1 (Code: 200, Data: 100, Stack: 50)
```
┌──────────────┬──────────────┬──────────────┬─────────────┐
│  P1 Code     │  P1 Data     │  P1 Stack    │   Free      │
│   (200 KB)   │   (100 KB)   │   (50 KB)    │  (650 KB)   │
└──────────────┴──────────────┴──────────────┴─────────────┘
  Base: 0        Base: 200      Base: 300      Base: 350
```

### After Adding P2 (Code: 150, Data: 80, Stack: 30)
```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┐
│  P1 Code     │  P1 Data     │  P1 Stack    │  P2 Code     │  P2 Data     │  P2 Stack    │   Free      │
│   (200 KB)   │   (100 KB)   │   (50 KB)    │   (150 KB)   │   (80 KB)    │   (30 KB)    │  (390 KB)   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
```

### After Deleting P1
```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┐
│    Free      │    Free      │    Free      │  P2 Code     │  P2 Data     │  P2 Stack    │   Free      │
│   (200 KB)   │   (100 KB)   │   (50 KB)    │   (150 KB)   │   (80 KB)    │   (30 KB)    │  (390 KB)   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
                                                                                                    ↑
                                                                                    External Fragmentation!
```

## Segment Table Example

```
┌──────────┬──────────┬──────────┬──────────┐
│ Process  │ Segment  │   Base   │   Size   │
├──────────┼──────────┼──────────┼──────────┤
│   P1     │   Code   │    0     │   200    │
│   P1     │   Data   │   200    │   100    │
│   P1     │   Stack  │   300    │    50    │
│   P2     │   Code   │   350    │   150    │
│   P2     │   Data   │   500    │    80    │
│   P2     │   Stack  │   580    │    30    │
└──────────┴──────────┴──────────┴──────────┘
```

## Address Translation Example

```
Logical Address: (P1, Data, 50)
                      │
                      ↓
            Find in Segment Table
                      │
                      ↓
        ┌─────────────────────────┐
        │ P1, Data, Base=200      │
        │           Size=100      │
        └─────────────────────────┘
                      │
                      ↓
              Validate: 50 < 100? ✓
                      │
                      ↓
        Physical = Base + Offset
                 = 200 + 50
                 = 250
                      │
                      ↓
        Physical Address: 250 KB
```

## Module Dependency Graph

```
                    main.py
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ↓              ↓              ↓
  memory_manager  segment_table  frag_calculator
                       ↑              
                       │              
                 address_translator
                       
                       
        process_manager
        (depends on all above)
        
        
        memory_visualizer
        (independent)
```

## File Size Comparison

```
Original (monolithic):
memory_simulator_visual.py  ████████████████████████ 400+ lines

New (modular):
memory_manager.py          ████ 60 lines
segment_table.py           ██ 35 lines
address_translator.py      ███ 40 lines
fragmentation_calculator.py ███ 35 lines
process_manager.py         ████ 50 lines
memory_visualizer.py       ████ 55 lines
main.py                    ████████████ 250 lines
                           ─────────────────────────
Total:                     525 lines (more features, better organized)
```

## Advantages Visualization

```
Monolithic Design          vs          Modular Design
┌─────────────────┐                   ┌────┐ ┌────┐ ┌────┐
│                 │                   │ M1 │ │ M2 │ │ M3 │
│   Everything    │                   └────┘ └────┘ └────┘
│   in one file   │                   ┌────┐ ┌────┐ ┌────┐
│                 │                   │ M4 │ │ M5 │ │ M6 │
└─────────────────┘                   └────┘ └────┘ └────┘

❌ Hard to understand                 ✅ Easy to understand
❌ Hard to test                       ✅ Easy to test
❌ Hard to explain                    ✅ Easy to explain
❌ Hard to extend                     ✅ Easy to extend
❌ Hard to maintain                   ✅ Easy to maintain
```
