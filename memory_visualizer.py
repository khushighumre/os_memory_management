"""
Memory Visualizer Module
Draws memory blocks on canvas
OS Concept: Visual representation of memory partitioning
"""

# Minimum pixel height guaranteed per block so text never overlaps
MIN_BLOCK_HEIGHT = 48
CANVAS_WIDTH     = 900
BLOCK_WIDTH      = 460   # the coloured bar
ADDR_X           = 175   # x centre of left address column
LEGEND_X         = 720   # x start of right legend column
MARGIN           = 20    # top / bottom padding

PROCESS_COLORS = {
    "free":  ("#e5e7eb", "#9ca3af", "#d1d5db"),   # fill, text, border
    "Code":  ("#3b82f6", "#ffffff", "#1e40af"),
    "Data":  ("#10b981", "#ffffff", "#065f46"),
    "Stack": ("#f59e0b", "#ffffff", "#92400e"),
}


class MemoryVisualizer:
    def __init__(self, canvas, total_memory):
        self.canvas = canvas
        self.total_memory = total_memory

    # ── helpers ──────────────────────────────────────────────────────────────

    def _colors(self, block):
        """Return (fill, text_color, border_color) for a block."""
        if block["type"] == "free":
            return PROCESS_COLORS["free"]
        for key in ("Code", "Data", "Stack"):
            if key in block["name"]:
                return PROCESS_COLORS[key]
        return PROCESS_COLORS["Code"]

    def _block_height(self, block_size, total_canvas_height):
        """Proportional height with a guaranteed minimum."""
        proportional = (block_size / self.total_memory) * total_canvas_height
        return max(proportional, MIN_BLOCK_HEIGHT)

    # ── public API ────────────────────────────────────────────────────────────

    def draw_memory_blocks(self, memory_blocks):
        """Draw memory blocks as a vertical bar with address rulers on the left
        and a name+size label on the right.  Text never overlaps because each
        block is at least MIN_BLOCK_HEIGHT pixels tall."""
        self.canvas.delete("all")
        if not memory_blocks:
            return

        # ── 1. calculate total canvas height needed ───────────────────────
        # Give every block its proportional share of a 'base' height, but
        # guarantee MIN_BLOCK_HEIGHT per block so nothing is squashed.
        base_height   = max(len(memory_blocks) * MIN_BLOCK_HEIGHT * 2, 400)
        block_heights = [
            self._block_height(b["size"], base_height) for b in memory_blocks
        ]
        total_needed  = int(sum(block_heights)) + 2 * MARGIN

        # Resize the canvas to fit all blocks
        self.canvas.config(height=total_needed, width=CANVAS_WIDTH)

        # ── 2. layout constants ───────────────────────────────────────────
        bar_x1 = (CANVAS_WIDTH - BLOCK_WIDTH) // 2
        bar_x2 = bar_x1 + BLOCK_WIDTH

        y      = MARGIN
        addr   = 0

        # ── 3. draw each block ────────────────────────────────────────────
        for block, bh in zip(memory_blocks, block_heights):
            fill, text_col, border = self._colors(block)
            y1 = y
            y2 = y + bh
            mid_y = (y1 + y2) / 2
            end_addr = addr + block["size"]

            # shadow
            self.canvas.create_rectangle(
                bar_x1 + 4, y1 + 4, bar_x2 + 4, y2 + 4,
                fill="#cbd5e1", outline=""
            )
            # main block
            self.canvas.create_rectangle(
                bar_x1, y1, bar_x2, y2,
                fill=fill, outline=border, width=2
            )

            # ── left ruler: start address at top edge ─────────────────
            self.canvas.create_line(
                bar_x1 - 6, y1, bar_x1, y1, fill="#6b7280", width=1
            )
            self.canvas.create_text(
                bar_x1 - 10, y1,
                text=f"{addr} KB",
                font=("Courier", 8), fill="#374151", anchor="e"
            )

            # ── text INSIDE block (only name + size, centred) ─────────
            # Always show at least the name; add size if block is tall enough
            if bh >= MIN_BLOCK_HEIGHT * 1.5:
                inside_label = f"{block['name']}\n{block['size']} KB"
            else:
                inside_label = block["name"]

            self.canvas.create_text(
                (bar_x1 + bar_x2) / 2, mid_y,
                text=inside_label,
                font=("Arial", 9, "bold"), fill=text_col,
                justify="center"
            )

            # ── right side: address range label ───────────────────────
            self.canvas.create_text(
                bar_x2 + 12, mid_y,
                text=f"[{addr} – {end_addr}]",
                font=("Arial", 8), fill="#374151", anchor="w"
            )

            y    = y2
            addr = end_addr

        # draw the final bottom address on the ruler
        self.canvas.create_line(
            bar_x1 - 6, y, bar_x1, y, fill="#6b7280", width=1
        )
        self.canvas.create_text(
            bar_x1 - 10, y,
            text=f"{addr} KB",
            font=("Courier", 8), fill="#374151", anchor="e"
        )

        # ── 4. legend (top-right corner) ──────────────────────────────────
        legend_items = [
            ("Code",  PROCESS_COLORS["Code"][0]),
            ("Data",  PROCESS_COLORS["Data"][0]),
            ("Stack", PROCESS_COLORS["Stack"][0]),
            ("Free",  PROCESS_COLORS["free"][0]),
        ]
        lx, ly = CANVAS_WIDTH - 110, MARGIN
        self.canvas.create_text(
            lx, ly, text="Legend",
            font=("Arial", 9, "bold"), fill="#1e3a8a", anchor="nw"
        )
        for i, (label, color) in enumerate(legend_items):
            ry = ly + 18 + i * 20
            self.canvas.create_rectangle(
                lx, ry, lx + 14, ry + 14,
                fill=color, outline="#6b7280"
            )
            self.canvas.create_text(
                lx + 18, ry + 7,
                text=label, font=("Arial", 9), fill="#374151", anchor="w"
            )
