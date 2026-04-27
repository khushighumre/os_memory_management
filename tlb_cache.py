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
        Check if translation exists in TLB

        Returns:
            (True, base_address) if HIT
            (False, None) if MISS
        """
        for entry in self.cache:
            if entry["process"] == process and entry["segment"] == segment:
                self.hit_count += 1
                return True, entry["base"]

        self.miss_count += 1
        return False, None

    def add_entry(self, process, segment, base):
        """
        Add new translation to TLB

        If TLB is full:
        Remove oldest entry (FIFO replacement)
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
            "base": base
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