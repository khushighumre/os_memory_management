"""
Process Manager Module
Manages process creation and deletion with segmentation
OS Concept: Process Memory Segmentation (Code, Data, Stack)
"""

# Permission flags per segment type (mirrors SEGMENT_PERMISSIONS in segment_table.py)
_SEGMENT_PERMISSIONS = {
    "Code":  "r-x",   # executable, not writable
    "Data":  "rw-",   # readable + writable
    "Stack": "rw-",   # readable + writable
}

class ProcessManager:
    def __init__(self, memory_manager, segment_table, frag_calculator):
        self.memory_manager = memory_manager
        self.segment_table  = segment_table
        self.frag_calculator = frag_calculator

    def create_process(self, process_name, code_size, data_size, stack_size, algorithm="First-Fit"):
        """Create a process with three segments using the specified allocation algorithm.

        Rollback guarantee: if any segment allocation fails, all previously
        allocated segments for this process are freed and their segment_table
        entries are removed before returning failure.
        """
        segments = [
            ("Code",  code_size),
            ("Data",  data_size),
            ("Stack", stack_size),
        ]

        # Track which segments were successfully allocated so we can roll back
        allocated_so_far = []   # list of segment type strings

        for seg_type, seg_size in segments:
            if seg_size == 0:
                continue

            seg_name = f"{process_name} {seg_type}"
            success, base, allocated_size = self.memory_manager.allocate_segment(
                seg_name, seg_size, algorithm
            )

            if not success:
                # ── ROLLBACK: undo every segment allocated in this call ──────
                for done_type in allocated_so_far:
                    self.memory_manager.deallocate_segment(process_name, done_type)
                    self.segment_table.remove_segment(process_name, done_type)
                # ─────────────────────────────────────────────────────────────
                return False, f"Not enough memory for {seg_name} — rolled back {len(allocated_so_far)} segment(s)"

            # Record internal fragmentation waste
            self.frag_calculator.add_internal_fragmentation(allocated_size, seg_size)

            # Pass the correct permission flags for this segment type
            perms = _SEGMENT_PERMISSIONS.get(seg_type, "rw-")
            self.segment_table.add_segment(process_name, seg_type, base, allocated_size, perms)

            allocated_so_far.append(seg_type)

        return True, f"Process {process_name} created successfully"

    def delete_process(self, process_name):
        """Delete a process and free its memory (coalescing happens inside deallocate_process)."""
        count = self.memory_manager.deallocate_process(process_name)

        if count == 0:
            return False, f"Process '{process_name}' not found"

        self.segment_table.remove_process(process_name)
        return True, f"Process {process_name} deleted ({count} segments freed)"
