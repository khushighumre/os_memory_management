"""
Fragmentation Calculator Module
Calculates internal and external fragmentation
OS Concepts: Internal vs External Fragmentation
"""

class FragmentationCalculator:
    def __init__(self):
        self.internal_fragmentation = 0
    
    def add_internal_fragmentation(self, allocated_size, requested_size):
        """Add internal fragmentation from allocation"""
        self.internal_fragmentation += (allocated_size - requested_size)
    
    def get_internal_fragmentation(self):
        """Get total internal fragmentation"""
        return self.internal_fragmentation
    
    def calculate_external_fragmentation(self, memory_blocks):
        """Calculate external fragmentation from memory structure
        
        External Fragmentation: Free memory scattered in non-contiguous blocks
        """
        free_blocks = [block["size"] for block in memory_blocks if block["type"] == "free"]
        
        if len(free_blocks) <= 1:
            return 0
        
        # Sum all free blocks except the largest
        return sum(free_blocks) - max(free_blocks)
    
    def reset(self):
        """Reset fragmentation counters"""
        self.internal_fragmentation = 0
