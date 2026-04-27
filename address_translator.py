"""
Address Translator Module
Performs logical to physical address translation

OS Concepts:
1. Segmentation
2. Address Translation
3. TLB (Translation Lookaside Buffer)

Formula:
Physical Address = Base Address + Offset
"""

from tlb_cache import TLB


class AddressTranslator:
    def __init__(self, segment_table):
        self.segment_table = segment_table
        self.tlb = TLB(size=4)

    def translate(self, process, segment, offset):
        """
        Translate logical address to physical address

        Returns:
            (success, physical_address, message)
        """

        # STEP 1 → Check TLB first
        hit, base_address = self.tlb.lookup(process, segment)

        if hit:
            if offset < 0:
                return False, 0, "Offset cannot be negative"

            physical_address = base_address + offset

            return (
                True,
                physical_address,
                f"TLB HIT ✅ | Physical Address = {base_address} + {offset} = {physical_address} KB"
            )

        # STEP 2 → TLB MISS → Search Segment Table
        seg_entry = self.segment_table.find_segment(process, segment)

        if not seg_entry:
            return False, 0, f"Segment '{segment}' not found"

        if offset < 0:
            return False, 0, "Offset cannot be negative"

        if offset >= seg_entry["size"]:
            return (
                False,
                0,
                f"Segmentation Fault: Offset exceeds segment limit"
            )

        # STEP 3 → Add to TLB
        self.tlb.add_entry(
            process,
            segment,
            seg_entry["base"]
        )

        physical_address = seg_entry["base"] + offset

        return (
            True,
            physical_address,
            f"TLB MISS ❌ → Added to TLB | Physical Address = {seg_entry['base']} + {offset} = {physical_address} KB"
        )