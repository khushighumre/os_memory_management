"""
Memory Manager Module
Handles core memory operations: allocation, deallocation, and memory structure management
OS Concepts: Segmentation, First-Fit, Best-Fit, Worst-Fit, Next-Fit Allocation, Dynamic Partitioning

Coalescing Modes:
  "immediate" — adjacent free blocks are merged right after every deallocation (default).
  "deferred"  — free blocks are NOT merged on deallocation; merging is triggered lazily
                 only when an allocation attempt fails, giving it one retry chance.
"""

ALGORITHMS       = ["First-Fit", "Best-Fit", "Worst-Fit", "Next-Fit"]
COALESCING_MODES = ["Immediate", "Deferred"]

class MemoryManager:
    def __init__(self):
        self.memory = []        # List of memory blocks
        self.total_memory = 0
        self.block_size = 10    # Fixed block size for internal fragmentation simulation
        # Next-Fit: persists across allocations so scanning resumes from last position
        self.next_fit_index = 0
        # Coalescing strategy: "immediate" or "deferred"
        self.coalescing_mode = "immediate"

    def initialize_memory(self, size):
        """Initialize memory with given size"""
        self.total_memory = size
        self.memory = [{"name": "Free", "size": size, "type": "free"}]
        self.next_fit_index = 0   # reset pointer only on full re-initialisation

    # ── private helpers ──────────────────────────────────────────────────────

    def _round_up(self, size):
        """Round size up to nearest block_size boundary (causes internal fragmentation)"""
        return ((size + self.block_size - 1) // self.block_size) * self.block_size

    def _place(self, i, seg_name, allocated_size):
        """Insert an allocated block at index i, splitting the free block if needed.
        Returns the base address of the placed block."""
        base_address = sum(b["size"] for b in self.memory[:i])
        block = self.memory[i]
        if block["size"] == allocated_size:
            self.memory[i] = {"name": seg_name, "size": allocated_size, "type": "used"}
        else:
            remaining = block["size"] - allocated_size
            self.memory[i] = {"name": seg_name, "size": allocated_size, "type": "used"}
            self.memory.insert(i + 1, {"name": "Free", "size": remaining, "type": "free"})
        return base_address

    # ── allocation strategies ─────────────────────────────────────────────────

    def _first_fit(self, seg_name, allocated_size):
        """First-Fit: scan from start, pick the FIRST block that fits.
        Fast but can leave many small fragments at the front."""
        for i, block in enumerate(self.memory):
            if block["type"] == "free":
                print(f"[First-Fit]  Trying block of size {block['size']} KB for request {allocated_size} KB")
                if block["size"] >= allocated_size:
                    base = self._place(i, seg_name, allocated_size)
                    return True, base, allocated_size
        return False, 0, 0

    def _best_fit(self, seg_name, allocated_size):
        """Best-Fit: scan all free blocks, pick the SMALLEST one that still fits.
        Minimises wasted space per allocation but can create tiny unusable fragments."""
        best_i = -1
        best_size = float("inf")
        for i, block in enumerate(self.memory):
            if block["type"] == "free":
                print(f"[Best-Fit]   Trying block of size {block['size']} KB for request {allocated_size} KB")
                if block["size"] >= allocated_size:
                    if block["size"] < best_size:
                        best_size = block["size"]
                        best_i = i
        if best_i == -1:
            return False, 0, 0
        base = self._place(best_i, seg_name, allocated_size)
        return True, base, allocated_size

    def _worst_fit(self, seg_name, allocated_size):
        """Worst-Fit: scan all free blocks, pick the LARGEST one.
        Leaves the biggest possible remainder, reducing tiny-fragment buildup."""
        worst_i = -1
        worst_size = -1
        for i, block in enumerate(self.memory):
            if block["type"] == "free":
                print(f"[Worst-Fit]  Trying block of size {block['size']} KB for request {allocated_size} KB")
                if block["size"] >= allocated_size:
                    if block["size"] > worst_size:
                        worst_size = block["size"]
                        worst_i = i
        if worst_i == -1:
            return False, 0, 0
        base = self._place(worst_i, seg_name, allocated_size)
        return True, base, allocated_size

    def _next_fit(self, seg_name, allocated_size):
        """Next-Fit: like First-Fit but starts scanning from where the LAST allocation ended.
        Distributes allocations more evenly across memory.
        Uses self.next_fit_index which persists between calls (never reset mid-session)."""
        n = len(self.memory)
        for offset in range(n):
            i = (self.next_fit_index + offset) % n
            block = self.memory[i]
            if block["type"] == "free":
                print(f"[Next-Fit]   Trying block of size {block['size']} KB for request {allocated_size} KB")
                if block["size"] >= allocated_size:
                    base = self._place(i, seg_name, allocated_size)
                    # Advance pointer past the just-placed block; wrap with current length
                    # (_place may have inserted a new block, so re-read len)
                    self.next_fit_index = (i + 1) % len(self.memory)
                    return True, base, allocated_size
        return False, 0, 0

    def _merge_free_blocks(self):
        """Coalesce adjacent free blocks into one.

        Traverses the memory list once; whenever two consecutive blocks are
        both free, the second is absorbed into the first.  Repeats until no
        adjacent free pair remains.  This eliminates the external fragmentation
        that builds up after process deletions.
        """
        i = 0
        while i < len(self.memory) - 1:
            curr = self.memory[i]
            nxt  = self.memory[i + 1]
            if curr["type"] == "free" and nxt["type"] == "free":
                # Merge: grow current block, remove the next one
                self.memory[i] = {"name": "Free", "size": curr["size"] + nxt["size"], "type": "free"}
                self.memory.pop(i + 1)
                # Don't advance i — the merged block might be adjacent to another free block
            else:
                i += 1

        # After merging, clamp next_fit_index so it stays within bounds
        if self.memory:
            self.next_fit_index = self.next_fit_index % len(self.memory)

    # ── public API ────────────────────────────────────────────────────────────

    def set_coalescing_mode(self, mode: str):
        """Set the coalescing strategy.

        Args:
            mode: "immediate" or "deferred" (case-insensitive)
        """
        self.coalescing_mode = mode.lower()

    def allocate_segment(self, seg_name, seg_size, algorithm="First-Fit"):
        """Allocate a segment using the chosen algorithm.

        Flow:
          Step 1 — Attempt allocation on current memory, no merging.
          Step 2 — If that fails AND mode is "deferred":
                     print "Deferred: Trying allocation without merge"  (already
                     printed at step 1 entry, see below)
                     Call _merge_free_blocks() exactly once.
          Step 3 — Retry allocation exactly once.
          Step 4 — Return result regardless of outcome (no further retries).

        _merge_free_blocks() is NEVER called before the first attempt and is
        NEVER called in immediate mode from this method.

        Args:
            seg_name:  block label, e.g. 'P1 Code'
            seg_size:  requested size in KB
            algorithm: one of ALGORITHMS list

        Returns: (success, base_address, allocated_size)
        """
        allocated_size = self._round_up(seg_size)

        dispatch = {
            "First-Fit": self._first_fit,
            "Best-Fit":  self._best_fit,
            "Worst-Fit": self._worst_fit,
            "Next-Fit":  self._next_fit,
        }
        fn = dispatch.get(algorithm, self._first_fit)

        # ── Step 1: first attempt — no merging under any mode ─────────────────
        if self.coalescing_mode == "deferred":
            print("Deferred: Trying allocation without merge")
        success, base, size = fn(seg_name, allocated_size)
        if success:
            return success, base, size

        # ── Step 2 & 3: deferred only — merge once, then retry exactly once ───
        if self.coalescing_mode == "deferred":
            print("Deferred: Merging and retrying")
            self._merge_free_blocks()
            success, base, size = fn(seg_name, allocated_size)

        # ── Step 4: return result (failure if still not allocated) ────────────
        return success, base, size

    def deallocate_process(self, process_name):
        """Deallocate all segments of a process.

        Immediate mode  → merge adjacent free blocks right away.
        Deferred mode   → leave free blocks unmerged; merging happens lazily
                          inside allocate_segment when needed.
        """
        count = 0
        for i, block in enumerate(self.memory):
            if block["name"].startswith(process_name + " "):
                self.memory[i] = {"name": "Free", "size": block["size"], "type": "free"}
                count += 1

        if count and self.coalescing_mode == "immediate":
            self._merge_free_blocks()

        return count

    def deallocate_segment(self, process_name, segment_type):
        """Deallocate a single named segment — used by rollback in process_manager.

        Respects coalescing_mode: rollback is an internal bookkeeping operation,
        not a user-visible deallocation, so it follows the same rules.
        In deferred mode the freed block is left unmerged, consistent with how
        deallocate_process behaves.
        """
        seg_label = f"{process_name} {segment_type}"
        for i, block in enumerate(self.memory):
            if block["name"] == seg_label:
                self.memory[i] = {"name": "Free", "size": block["size"], "type": "free"}
                if self.coalescing_mode == "immediate":
                    self._merge_free_blocks()
                return True
        return False

    def compact_memory(self, segment_table):
        """Compact memory: slide all used blocks to the front, collect all free
        space into a single block at the end, and update segment_table base addresses.

        Args:
            segment_table: SegmentTable instance whose entries will be updated
                           to reflect the new base addresses after compaction.

        Returns:
            The updated memory list (same object as self.memory).
        """
        # 1. Separate used and free blocks
        used_blocks = [b for b in self.memory if b["type"] == "used"]
        total_free  = sum(b["size"] for b in self.memory if b["type"] == "free")

        # 2. Rebuild memory: used blocks packed at the front
        new_memory = []
        cursor = 0  # running base address

        for block in used_blocks:
            new_memory.append(block.copy())

            # 3. Update the matching segment_table entry with the new base address
            #    Block name format is "ProcessName SegmentType" e.g. "P1 Code"
            parts = block["name"].split(" ", 1)   # ["P1", "Code"]
            if len(parts) == 2:
                proc_name, seg_type = parts
                seg_entry = segment_table.find_segment(proc_name, seg_type)
                if seg_entry:
                    seg_entry["base"] = cursor   # mutate in-place

            cursor += block["size"]

        # 4. Append the single consolidated free block (if any free space exists)
        if total_free > 0:
            new_memory.append({"name": "Free", "size": total_free, "type": "free"})

        self.memory = new_memory
        # Reset Next-Fit pointer to start — memory layout has changed completely
        self.next_fit_index = 0
        return self.memory

    def get_memory_blocks(self):
        """Return current memory structure"""
        return self.memory
