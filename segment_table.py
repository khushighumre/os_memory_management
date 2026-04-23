"""
Segment Table Module
Manages segment table for address translation
OS Concept: Segment Table - stores base address, limit, and protection flags per segment

Permission flags follow Unix rwx notation:
  r = read, w = write, x = execute, - = denied
  Code  → "r-x"  (readable + executable, not writable)
  Data  → "rw-"  (readable + writable, not executable)
  Stack → "rw-"  (readable + writable, not executable)
"""

# Default permission map per segment type
SEGMENT_PERMISSIONS = {
    "Code":  "r-x",
    "Data":  "rw-",
    "Stack": "rw-",
}

class SegmentTable:
    def __init__(self):
        self.table = []

    def add_segment(self, process, segment, base, size, permissions=None):
        """Add a segment entry to the table.

        permissions: optional string like "r-x"; auto-derived from segment
                     type if not provided (Code→"r-x", Data/Stack→"rw-").
        """
        # Auto-assign permissions based on segment type when not explicitly given
        if permissions is None:
            permissions = SEGMENT_PERMISSIONS.get(segment, "rw-")

        self.table.append({
            "process":     process,
            "segment":     segment,
            "base":        base,
            "size":        size,
            "permissions": permissions,   # NEW: memory protection flags
        })
    
    def remove_process(self, process_name):
        """Remove all segments of a process"""
        self.table = [seg for seg in self.table if seg["process"] != process_name]

    def remove_segment(self, process_name, segment_type):
        """Remove a single segment entry — used by rollback in process_manager."""
        self.table = [
            seg for seg in self.table
            if not (seg["process"] == process_name and seg["segment"] == segment_type)
        ]

    def find_segment(self, process, segment):
        """Find a segment entry"""
        for seg in self.table:
            if seg["process"] == process and seg["segment"] == segment:
                return seg
        return None

    def check_access(self, process, segment, mode):
        """Check whether a given access mode is permitted for a segment.

        Args:
            process: process name string
            segment: segment name string ("Code", "Data", "Stack")
            mode:    single character — 'r' (read), 'w' (write), or 'x' (execute)

        Returns:
            True  if the permission flag for mode is set
            False if denied or segment not found
        """
        seg_entry = self.find_segment(process, segment)
        if seg_entry is None:
            return False  # segment doesn't exist → deny

        perms = seg_entry.get("permissions", "---")
        mode_index = {"r": 0, "w": 1, "x": 2}.get(mode)
        if mode_index is None:
            return False  # unknown mode → deny

        return perms[mode_index] != "-"

    def get_permissions(self, process, segment):
        """Return the permission string for a segment, or None if not found."""
        seg_entry = self.find_segment(process, segment)
        return seg_entry["permissions"] if seg_entry else None

    def get_all_segments(self):
        """Return all segment entries"""
        return self.table

    def clear(self):
        """Clear the segment table"""
        self.table = []
