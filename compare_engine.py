"""
Compare Engine Module
Runs the same process workload (adds + deletes) across all allocation algorithms independently.
OS Concept: Algorithm Performance Comparison

Workload format:
    Each entry is a tuple:
      ("add",    process_name, code_size, data_size, stack_size)
      ("delete", process_name)
"""

from memory_manager import MemoryManager, ALGORITHMS
from segment_table import SegmentTable
from fragmentation_calculator import FragmentationCalculator
from process_manager import ProcessManager


class CompareEngine:
    def __init__(self, total_memory):
        self.total_memory = total_memory
        self.results = {}  # {algorithm: result_dict}

    def run_comparison(self, workload):
        """Run the same workload on all four algorithms independently.

        Args:
            workload: list of ("add", name, code, data, stack)
                                or ("delete", name) tuples

        Returns:
            dict: {algorithm: metrics_dict}
        """
        for algo in ALGORITHMS:
            self.results[algo] = self._simulate_algorithm(algo, workload)
        return self.results

    def _simulate_algorithm(self, algorithm, workload):
        """Replay the full workload for one algorithm in a fresh sandbox."""
        mm = MemoryManager()
        mm.initialize_memory(self.total_memory)
        st = SegmentTable()
        fc = FragmentationCalculator()
        pm = ProcessManager(mm, st, fc)

        success_count  = 0
        failed_processes = []

        for entry in workload:
            op = entry[0]
            if op == "add":
                _, name, code, data, stack = entry
                ok, msg = pm.create_process(name, code, data, stack, algorithm)
                if ok:
                    success_count += 1
                else:
                    failed_processes.append(name)
                print(f"[{algorithm}] ADD {name} -> {msg}")
            elif op == "delete":
                _, name = entry
                ok, msg = pm.delete_process(name)
                print(f"[{algorithm}] DEL {name} -> {msg}")

        # ── metrics ──────────────────────────────────────────────────────────
        blocks    = mm.get_memory_blocks()
        used      = sum(b["size"] for b in blocks if b["type"] == "used")
        free      = sum(b["size"] for b in blocks if b["type"] == "free")
        int_frag  = fc.get_internal_fragmentation()
        ext_frag  = fc.calculate_external_fragmentation(blocks)
        free_blks = sum(1 for b in blocks if b["type"] == "free")

        print(f"[{algorithm}] FINAL blocks: {blocks}")
        print(f"[{algorithm}] used={used} free={free} int_frag={int_frag} ext_frag={ext_frag} free_blocks={free_blks}")

        return {
            "memory_used":   used,
            "free_memory":   free,
            "internal_frag": int_frag,
            "external_frag": ext_frag,
            "free_blocks":   free_blks,
            "success_count": success_count,
            "failed_processes": failed_processes,
            "total_frag":    int_frag + ext_frag,
            "utilization":   round((used / self.total_memory) * 100, 2) if self.total_memory > 0 else 0,
        }

    def get_best_algorithm(self):
        """Pick the algorithm with lowest total fragmentation, then highest utilization."""
        if not self.results:
            return None
        ranked = sorted(
            self.results.items(),
            key=lambda x: (x[1]["total_frag"], -x[1]["utilization"])
        )
        return ranked[0][0]
