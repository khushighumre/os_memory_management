"""
Address Translator Module
Performs logical to physical address translation
OS Concept: Address Translation in Segmentation
Formula: Physical Address = Base Address + Offset
"""

class AddressTranslator:
    def __init__(self, segment_table):
        self.segment_table = segment_table
    
    def translate(self, process, segment, offset):
        """Translate logical address to physical address
        
        Returns: (success, physical_address, error_message)
        """
        # Find segment in table
        seg_entry = self.segment_table.find_segment(process, segment)
        
        if not seg_entry:
            return False, 0, f"Segment '{segment}' not found for process '{process}'"
        
        # Validate offset (Segment Limit Check)
        if offset < 0:
            return False, 0, "Offset cannot be negative"
        
        if offset >= seg_entry["size"]:
            return False, 0, f"Segmentation Fault: Offset {offset} exceeds segment limit {seg_entry['size']}"
        
        # Calculate physical address
        physical_address = seg_entry["base"] + offset
        
        return True, physical_address, f"Physical Address = {seg_entry['base']} + {offset} = {physical_address} KB"
