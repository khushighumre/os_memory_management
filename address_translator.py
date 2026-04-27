"""
Address Translator Module
Performs logical to physical address translation

OS Concepts:
1. Segmentation
2. Address Translation
3. TLB (Translation Lookaside Buffer)
4. Memory Protection (permission flags: r/w/x)

Formula:
Physical Address = Base Address + Offset
"""

from tlb_cache import TLB


class AddressTranslator:
    def __init__(self, segment_table):
        self.segment_table = segment_table
        self.tlb = TLB(size=4)

    def translate(self, process, segment, offset, access_mode="r"):
        """
        Translate a logical address to a physical address.

        Args:
            process:     process name string (e.g. "P1")
            segment:     segment name string (e.g. "Code", "Data", "Stack")
            offset:      byte/KB offset within the segment (must be >= 0 and < size)
            access_mode: 'r' (read), 'w' (write), or 'x' (execute).
                         Defaults to 'r'.  Checked against the segment's
                         permission flags BEFORE the bounds check.

        Returns:
            (success: bool, physical_address: int, message: str)

        Error cases (in order of checking):
            1. Negative offset
            2. Permission denied  (protection fault)
            3. Offset >= segment size  (segmentation fault)
        """

        # ── Step 0: reject negative offsets immediately ───────────────────
        if offset < 0:
            return False, 0, "Offset cannot be negative"

        # ── Step 1: Check TLB first ───────────────────────────────────────
        hit, cached = self.tlb.lookup(process, segment)

        if hit:
            base_address = cached["base"]
            seg_size     = cached["size"]
            seg_perms    = cached["perms"]

            # Permission check on TLB hit
            mode_index = {"r": 0, "w": 1, "x": 2}.get(access_mode)
            if mode_index is not None and seg_perms[mode_index] == "-":
                return (
                    False, 0,
                    f"Protection Fault: '{access_mode}' access denied on "
                    f"segment '{segment}' (permissions: {seg_perms})"
                )

            # Bounds check on TLB hit
            if offset >= seg_size:
                return (
                    False, 0,
                    f"Segmentation Fault: Offset {offset} exceeds segment "
                    f"limit {seg_size}"
                )

            physical_address = base_address + offset
            return (
                True,
                physical_address,
                f"TLB HIT ✅ | Physical Address = {base_address} + {offset} "
                f"= {physical_address} KB"
            )

        # ── Step 2: TLB MISS → look up segment table ─────────────────────
        seg_entry = self.segment_table.find_segment(process, segment)

        if not seg_entry:
            return False, 0, f"Segment '{segment}' not found for process '{process}'"

        # Permission check on TLB miss
        perms      = seg_entry.get("permissions", "rw-")
        mode_index = {"r": 0, "w": 1, "x": 2}.get(access_mode)
        if mode_index is not None and perms[mode_index] == "-":
            return (
                False, 0,
                f"Protection Fault: '{access_mode}' access denied on "
                f"segment '{segment}' (permissions: {perms})"
            )

        # Bounds check on TLB miss
        if offset >= seg_entry["size"]:
            return (
                False, 0,
                f"Segmentation Fault: Offset {offset} exceeds segment "
                f"limit {seg_entry['size']}"
            )

        # ── Step 3: Add to TLB (base + size + perms) ─────────────────────
        self.tlb.add_entry(
            process,
            segment,
            seg_entry["base"],
            seg_entry["size"],
            perms,
        )

        physical_address = seg_entry["base"] + offset

        return (
            True,
            physical_address,
            f"TLB MISS ❌ → Added to TLB | Physical Address = "
            f"{seg_entry['base']} + {offset} = {physical_address} KB"
        )
