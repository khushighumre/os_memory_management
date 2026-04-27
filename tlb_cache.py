"""
TLB Cache Module
OS Concept: Translation Lookaside Buffer (TLB)

Stores recently used address translations
to speed up logical → physical address translation
"""

class TLB:
    def __init__(self, size=4):
        """
        size = maximum number of entries in TLB
        """
        self.size = size
        self.cache = []  # list of dictionaries

        self.hit_count = 0
        self.miss_count = 0

    def lookup(self, process, segment):
        """
        Check if translation exists in TLB.

        Returns:
            (True,  {"base": ..., "size": ..., "perms": ...})  on HIT
            (False, None)                                       on MISS
        """
        for entry in self.cache:
            if entry["process"] == process and entry["segment"] == segment:
                self.hit_count += 1
                return True, {
                    "base":  entry["base"],
                    "size":  entry["size"],
                    "perms": entry["perms"],
                }

        self.miss_count += 1
        return False, None

    def add_entry(self, process, segment, base, size, perms="rw-"):
        """
        Add new translation to TLB.

        Stores base, size, and perms so the hit path can perform both
        the bounds check and the permission check without going back to
        the segment table.

        If TLB is full: remove oldest entry (FIFO replacement).
        """

        # Avoid duplicate entries
        for entry in self.cache:
            if entry["process"] == process and entry["segment"] == segment:
                return

        if len(self.cache) >= self.size:
            self.cache.pop(0)  # FIFO replacement

        self.cache.append({
            "process": process,
            "segment": segment,
            "base":    base,
            "size":    size,    # needed for bounds check on TLB hit
            "perms":   perms,   # needed for permission check on TLB hit
        })

    def get_hit_ratio(self):
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0
        return round((self.hit_count / total) * 100, 2)

    def get_entries(self):
        return self.cache

    def reset(self):
        self.cache = []
        self.hit_count = 0
        self.miss_count = 0