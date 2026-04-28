"""
Main GUI Application
Integrates all modules into a complete OS Memory Management Simulator
"""

import tkinter as tk
from tkinter import messagebox, ttk
from memory_manager import MemoryManager, ALGORITHMS, COALESCING_MODES
from segment_table import SegmentTable
from address_translator import AddressTranslator
from fragmentation_calculator import FragmentationCalculator
from process_manager import ProcessManager
from memory_visualizer import MemoryVisualizer
from compare_engine import CompareEngine

class MemorySimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Memory Management Simulator")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f0f4f8")
        
        # Initialize all modules
        self.memory_manager = MemoryManager()
        self.segment_table = SegmentTable()
        self.frag_calculator = FragmentationCalculator()
        self.process_manager = ProcessManager(self.memory_manager, self.segment_table, self.frag_calculator)
        self.address_translator = AddressTranslator(self.segment_table)

        # Coalescing mode selection (persists across steps)
        self.coalescing_var = tk.StringVar(value="Immediate")

        # Compaction toggle (persists across steps)
        self.compaction_var = tk.BooleanVar(value=False)

        # Pending process list for compare mode: list of (name, code, data, stack)
        self.pending_processes = []

        self.current_step = 1
        self.frame1 = None
        self.frame2 = None
        self.frame3 = None
        
        self.show_step1()
    
    def show_step1(self):
        """Step 1: Memory Initialization"""
        self.frame1 = tk.Frame(self.root, bg="#f0f4f8")
        self.frame1.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_frame = tk.Frame(self.frame1, bg="#1e3a8a", relief="flat")
        title_frame.pack(fill="x", pady=(0, 30))
        tk.Label(title_frame, text="🖥️ OS Memory Management Simulator", 
                font=("Arial", 24, "bold"), fg="white", bg="#1e3a8a", pady=20).pack()
        
        tk.Label(self.frame1, text="Step 1: Initialize Memory", 
                font=("Arial", 16, "bold"), fg="#1e3a8a", bg="#f0f4f8").pack(pady=10)
        
        input_frame = tk.Frame(self.frame1, bg="white", relief="raised", bd=2)
        input_frame.pack(pady=30, padx=50, ipadx=30, ipady=30)
        
        tk.Label(input_frame, text="Total Memory Size (KB):", 
                font=("Arial", 13), bg="white", fg="#374151").grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.memory_size_entry = tk.Entry(input_frame, width=25, font=("Arial", 13), relief="solid", bd=1)
        self.memory_size_entry.grid(row=0, column=1, padx=15, pady=15)

        tk.Label(input_frame, text="Coalescing Mode:", 
                font=("Arial", 13), bg="white", fg="#374151").grid(row=1, column=0, padx=15, pady=15, sticky="w")
        coalescing_dropdown = ttk.Combobox(input_frame, textvariable=self.coalescing_var,
                                           values=COALESCING_MODES, state="readonly",
                                           width=23, font=("Arial", 13))
        coalescing_dropdown.grid(row=1, column=1, padx=15, pady=15)

        # Tooltip-style hint label
        hint_text = ("Immediate: merge free blocks right after deallocation  |  "
                     "Deferred: merge only when an allocation fails")
        tk.Label(input_frame, text=hint_text,
                 font=("Arial", 9), bg="white", fg="#6b7280",
                 wraplength=420, justify="left").grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 10))

        # Compaction toggle
        tk.Label(input_frame, text="Auto-Compaction:",
                 font=("Arial", 13), bg="white", fg="#374151").grid(row=3, column=0, padx=15, pady=15, sticky="w")
        compaction_check = tk.Checkbutton(
            input_frame,
            text="Enable  (compact memory after every process deletion)",
            variable=self.compaction_var,
            font=("Arial", 11), bg="white", fg="#374151",
            activebackground="white", selectcolor="white",
            cursor="hand2"
        )
        compaction_check.grid(row=3, column=1, padx=15, pady=15, sticky="w")

        compaction_hint = ("When ON: after deleting a process, all used blocks slide to the front\n"
                           "and all free space is merged into one block at the end.")
        tk.Label(input_frame, text=compaction_hint,
                 font=("Arial", 9), bg="white", fg="#6b7280",
                 wraplength=420, justify="left").grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 10))

        tk.Button(self.frame1, text="Initialize & Continue →", command=self.initialize_memory, 
                 bg="#10b981", fg="white", font=("Arial", 13, "bold"), 
                 width=25, height=2, relief="flat", cursor="hand2").pack(pady=20)
    
    def initialize_memory(self):
        """Initialize memory"""
        try:
            size = int(self.memory_size_entry.get())
            if size <= 0:
                raise ValueError
            
            self.memory_manager.initialize_memory(size)
            self.memory_manager.set_coalescing_mode(self.coalescing_var.get())
            self.segment_table.clear()
            self.frag_calculator.reset()
            
            mode_label = self.coalescing_var.get()
            compact_label = "ON" if self.compaction_var.get() else "OFF"
            messagebox.showinfo("Success", f"Memory initialized with {size} KB\nCoalescing mode: {mode_label}\nAuto-Compaction: {compact_label}")
            self.switch_frames(self.frame1, 2)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer")
    
    def show_step2(self):
        """Step 2: Process Management"""
        self.frame2 = tk.Frame(self.root, bg="#f0f4f8")
        self.frame2.pack(fill="both", expand=True, padx=20, pady=20)

        title_frame = tk.Frame(self.frame2, bg="#1e3a8a", relief="flat")
        title_frame.pack(fill="x", pady=(0, 20))
        tk.Label(title_frame, text="🖥️ OS Memory Management Simulator",
                 font=("Arial", 22, "bold"), fg="white", bg="#1e3a8a", pady=15).pack()

        tk.Label(self.frame2, text="Step 2: Process Management",
                 font=("Arial", 16, "bold"), fg="#1e3a8a", bg="#f0f4f8").pack(pady=10)

        # Active coalescing mode badge
        mode_color = "#065f46" if self.coalescing_var.get() == "Immediate" else "#92400e"
        mode_bg    = "#d1fae5" if self.coalescing_var.get() == "Immediate" else "#fef3c7"
        tk.Label(self.frame2,
                 text=f"🔀 Coalescing Mode: {self.coalescing_var.get()}",
                 font=("Arial", 10, "bold"), fg=mode_color, bg=mode_bg,
                 relief="solid", bd=1, padx=10, pady=4).pack(pady=(0, 4))

        # Active compaction badge
        cmp_on = self.compaction_var.get()
        tk.Label(self.frame2,
                 text=f"🗜️ Auto-Compaction: {'ON' if cmp_on else 'OFF'}",
                 font=("Arial", 10, "bold"),
                 fg="#1e40af" if cmp_on else "#6b7280",
                 bg="#dbeafe" if cmp_on else "#f3f4f6",
                 relief="solid", bd=1, padx=10, pady=4).pack(pady=(0, 8))

        # Process input
        input_frame = tk.LabelFrame(self.frame2, text=" ➕ Add New Process ",
                                    font=("Arial", 12, "bold"), padx=25, pady=20,
                                    bg="white", fg="#1e3a8a", relief="raised", bd=2)
        input_frame.pack(pady=15, padx=40, fill="x")

        tk.Label(input_frame, text="Process Name:", font=("Arial", 11), bg="white", fg="#374151").grid(row=0, column=0, sticky="w", pady=8)
        self.process_name_entry = tk.Entry(input_frame, width=28, font=("Arial", 11), relief="solid", bd=1)
        self.process_name_entry.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(input_frame, text="Code Segment (KB):", font=("Arial", 11), bg="white", fg="#374151").grid(row=1, column=0, sticky="w", pady=8)
        self.code_size_entry = tk.Entry(input_frame, width=28, font=("Arial", 11), relief="solid", bd=1)
        self.code_size_entry.grid(row=1, column=1, padx=15, pady=8)

        tk.Label(input_frame, text="Data Segment (KB):", font=("Arial", 11), bg="white", fg="#374151").grid(row=2, column=0, sticky="w", pady=8)
        self.data_size_entry = tk.Entry(input_frame, width=28, font=("Arial", 11), relief="solid", bd=1)
        self.data_size_entry.grid(row=2, column=1, padx=15, pady=8)

        tk.Label(input_frame, text="Stack Segment (KB):", font=("Arial", 11), bg="white", fg="#374151").grid(row=3, column=0, sticky="w", pady=8)
        self.stack_size_entry = tk.Entry(input_frame, width=28, font=("Arial", 11), relief="solid", bd=1)
        self.stack_size_entry.grid(row=3, column=1, padx=15, pady=8)

        # Algorithm selector
        tk.Label(input_frame, text="Allocation Algorithm:", font=("Arial", 11), bg="white", fg="#374151").grid(row=4, column=0, sticky="w", pady=8)
        self.algorithm_var = tk.StringVar(value="First-Fit")
        algo_dropdown = ttk.Combobox(input_frame, textvariable=self.algorithm_var,
                                     values=ALGORITHMS, state="readonly",
                                     width=26, font=("Arial", 11))
        algo_dropdown.grid(row=4, column=1, padx=15, pady=8)

        button_frame = tk.Frame(self.frame2, bg="#f0f4f8")
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="➕ Add Process", command=self.add_process,
                  bg="#3b82f6", fg="white", font=("Arial", 12, "bold"),
                  width=18, height=2, relief="flat", cursor="hand2").pack(side="left", padx=10)

        tk.Button(button_frame, text="📊 View Dashboard →", command=lambda: self.switch_frames(self.frame2, 3),
                  bg="#f59e0b", fg="white", font=("Arial", 12, "bold"),
                  width=18, height=2, relief="flat", cursor="hand2").pack(side="left", padx=10)

        tk.Button(button_frame, text="⚖️ Compare Algorithms", command=self.open_compare_mode,
                  bg="#7c3aed", fg="white", font=("Arial", 12, "bold"),
                  width=20, height=2, relief="flat", cursor="hand2").pack(side="left", padx=10)

        # Delete Process
        delete_frame = tk.LabelFrame(self.frame2, text=" ❌ Delete Process ",
                                     font=("Arial", 12, "bold"), padx=25, pady=15,
                                     bg="white", fg="#dc2626", relief="raised", bd=2)
        delete_frame.pack(pady=15, padx=40, fill="x")

        tk.Label(delete_frame, text="Process Name:", font=("Arial", 11), bg="white", fg="#374151").grid(row=0, column=0, sticky="w", pady=8)
        self.delete_process_entry = tk.Entry(delete_frame, width=28, font=("Arial", 11), relief="solid", bd=1)
        self.delete_process_entry.grid(row=0, column=1, padx=15, pady=8)

        tk.Button(delete_frame, text="🗑️ Delete Process", command=self.delete_process,
                  bg="#ef4444", fg="white", font=("Arial", 11, "bold"),
                  width=20, relief="flat", cursor="hand2").grid(row=1, column=0, columnspan=2, pady=10)
    
    def update_tlb_display(self):
        """Refresh TLB statistics display"""

        hit = self.address_translator.tlb.hit_count
        miss = self.address_translator.tlb.miss_count
        ratio = self.address_translator.tlb.get_hit_ratio()

        self.tlb_label.config(
            text=f"TLB Hits: {hit} | TLB Misses: {miss} | Hit Ratio: {ratio}%"
        )

    def add_process(self):
        """Add a process using the selected algorithm"""
        try:
            process_name = self.process_name_entry.get().strip()
            code_size = int(self.code_size_entry.get())
            data_size = int(self.data_size_entry.get())
            stack_size = int(self.stack_size_entry.get())
            algorithm = self.algorithm_var.get()

            if not process_name:
                raise ValueError("Process name cannot be empty")
            if code_size < 0 or data_size < 0 or stack_size < 0:
                raise ValueError("Segment sizes must be non-negative")

            # Record in workload for compare mode: ("add", name, code, data, stack)
            self.pending_processes.append(("add", process_name, code_size, data_size, stack_size))

            success, message = self.process_manager.create_process(process_name, code_size, data_size, stack_size, algorithm)

            if success:
                messagebox.showinfo("Success", message + f" (using {algorithm})")
                self.process_name_entry.delete(0, tk.END)
                self.code_size_entry.delete(0, tk.END)
                self.data_size_entry.delete(0, tk.END)
                self.stack_size_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", message)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def delete_process(self):
        """Delete a process"""
        try:
            process_name = self.delete_process_entry.get().strip()
            if not process_name:
                raise ValueError("Process name cannot be empty")
            
            success, message = self.process_manager.delete_process(process_name)

            if success:
                # Record deletion in workload for compare mode: ("delete", name)
                self.pending_processes.append(("delete", process_name))

                # Auto-compaction: slide used blocks to front, merge all free space
                if self.compaction_var.get():
                    self.memory_manager.compact_memory(self.segment_table)
                    message += "  |  Memory compacted ✅"

                messagebox.showinfo("Success", message)
                self.delete_process_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", message)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def show_step3(self):
        """Step 3: Dashboard"""
        self.frame3 = tk.Frame(self.root, bg="#f0f4f8")
        self.frame3.pack(fill="both", expand=True)

        main_canvas = tk.Canvas(self.frame3, bg="#f0f4f8")
        scrollbar = tk.Scrollbar(self.frame3, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#f0f4f8")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Keep scrollable_frame width in sync with the canvas so content stays centred
        def _on_canvas_resize(event):
            main_canvas.itemconfig(canvas_window, width=event.width)

        canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.bind("<Configure>", _on_canvas_resize)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # =========================================================
        # TITLE
        # =========================================================

        title_frame = tk.Frame(scrollable_frame, bg="#1e3a8a")
        title_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            title_frame,
            text="📊 OS Memory Management Dashboard",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1e3a8a",
            pady=15
        ).pack()

        # =========================================================
        # COALESCING MODE BADGE
        # =========================================================

        mode_color = "#065f46" if self.coalescing_var.get() == "Immediate" else "#92400e"
        mode_bg    = "#d1fae5" if self.coalescing_var.get() == "Immediate" else "#fef3c7"
        tk.Label(scrollable_frame,
                 text=f"🔀 Coalescing Mode: {self.coalescing_var.get()}",
                 font=("Arial", 10, "bold"), fg=mode_color, bg=mode_bg,
                 relief="solid", bd=1, padx=10, pady=4).pack(pady=(0, 6))
        
        # Memory Visualization
        viz_frame = tk.LabelFrame(scrollable_frame, text=" 💾 Memory Visualization ", 
                                  font=("Arial", 12, "bold"), padx=15, pady=15,
                                  bg="white", fg="#1e3a8a", relief="raised", bd=2)
        viz_frame.pack(padx=20, pady=10, fill="x")

        self.canvas = tk.Canvas(
            viz_frame,
            width=900,
            bg="#f9fafb",
            relief="solid",
            borderwidth=1,
            highlightthickness=0
        )
        self.canvas.pack(pady=10, fill="x")

        self.visualizer = MemoryVisualizer(
            self.canvas,
            self.memory_manager.total_memory
        )
        self.visualizer.draw_memory_blocks(
            self.memory_manager.get_memory_blocks()
        )

        # =========================================================
        # FRAGMENTATION
        # =========================================================

        frag_frame = tk.LabelFrame(
            scrollable_frame,
            text=" ⚠️ Fragmentation Analysis ",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15,
            bg="white",
            fg="#1e3a8a",
            relief="raised",
            bd=2
        )
        frag_frame.pack(padx=20, pady=10, fill="x")

        stats_container = tk.Frame(frag_frame, bg="white")
        stats_container.pack(pady=5)

        ext_frag = self.frag_calculator.calculate_external_fragmentation(
            self.memory_manager.get_memory_blocks()
        )

        ext_frame = tk.Frame(
            stats_container,
            bg="#fef2f2",
            relief="solid",
            bd=1
        )
        ext_frame.pack(side="left", padx=15, pady=5, ipadx=20, ipady=10)

        self.ext_frag_label = tk.Label(
            ext_frame,
            text=f"🔴 External Fragmentation: {ext_frag} KB",
            font=("Arial", 11, "bold"),
            fg="#dc2626",
            bg="#fef2f2"
        )
        self.ext_frag_label.pack()

        int_frag = self.frag_calculator.get_internal_fragmentation()

        int_frame = tk.Frame(
            stats_container,
            bg="#fff7ed",
            relief="solid",
            bd=1
        )
        int_frame.pack(side="left", padx=15, pady=5, ipadx=20, ipady=10)

        self.int_frag_label = tk.Label(
            int_frame,
            text=f"🟡 Internal Fragmentation: {int_frag} KB",
            font=("Arial", 11, "bold"),
            fg="#ea580c",
            bg="#fff7ed"
        )
        self.int_frag_label.pack()

        # =========================================================
        # SEGMENT TABLE
        # =========================================================

        seg_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 📋 Segment Table ",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15,
            bg="white",
            fg="#1e3a8a",
            relief="raised",
            bd=2
        )
        seg_frame.pack(padx=20, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#f9fafb",
            foreground="#1f2937",
            rowheight=28,
            fieldbackground="#f9fafb",
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#3b82f6",
            foreground="white",
            font=("Arial", 11, "bold"),
            relief="flat"
        )

        self.segment_tree = ttk.Treeview(
            seg_frame,
            columns=("Process", "Segment", "Base", "Size"),
            show="headings",
            height=6
        )

        self.segment_tree.heading("Process", text="Process ID")
        self.segment_tree.heading("Segment", text="Segment Name")
        self.segment_tree.heading("Base", text="Base Address")
        self.segment_tree.heading("Size", text="Size (KB)")

        self.segment_tree.column("Process", width=200, anchor="center")
        self.segment_tree.column("Segment", width=200, anchor="center")
        self.segment_tree.column("Base", width=200, anchor="center")
        self.segment_tree.column("Size", width=200, anchor="center")

        self.segment_tree.pack(pady=10, fill="both", expand=True)

        self.populate_segment_table()

        # =========================================================
        # ADDRESS TRANSLATION
        # =========================================================

        addr_frame = tk.LabelFrame(
            scrollable_frame,
            text=" 🔄 Address Translation ",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15,
            bg="white",
            fg="#1e3a8a",
            relief="raised",
            bd=2
        )
        addr_frame.pack(padx=20, pady=10, fill="x")

        input_frame = tk.Frame(addr_frame, bg="white")
        input_frame.pack(pady=10)

        tk.Label(
            input_frame,
            text="Process ID:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=0, column=0, padx=8, pady=8)

        self.trans_process_entry = tk.Entry(input_frame, width=15)
        self.trans_process_entry.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(
            input_frame,
            text="Segment:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=0, column=2, padx=8, pady=8)

        self.trans_segment_entry = tk.Entry(input_frame, width=15)
        self.trans_segment_entry.grid(row=0, column=3, padx=8, pady=8)

        tk.Label(
            input_frame,
            text="Offset:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=0, column=4, padx=8, pady=8)

        self.trans_offset_entry = tk.Entry(input_frame, width=15)
        self.trans_offset_entry.grid(row=0, column=5, padx=8, pady=8)

        tk.Button(
            addr_frame,
            text="➡️ Translate Address",
            command=self.translate_address,
            bg="#10b981",
            fg="white",
            font=("Arial", 11, "bold"),
            width=22
        ).pack(pady=10)

        result_container = tk.Frame(
            addr_frame,
            bg="#eff6ff",
            relief="solid",
            bd=1
        )
        result_container.pack(pady=10, padx=20, fill="x", ipady=10)

        self.trans_result_label = tk.Label(
            result_container,
            text="Enter values and click Translate",
            font=("Arial", 11, "bold"),
            fg="#3b82f6",
            bg="#eff6ff"
        )
        self.trans_result_label.pack()

        # =========================================================
        # TLB STATISTICS (CORRECT PLACE)
        # =========================================================

        tlb_frame = tk.LabelFrame(
            scrollable_frame,
            text=" ⚡ TLB Statistics ",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15,
            bg="white",
            fg="#1e3a8a",
            relief="raised",
            bd=2
        )
        tlb_frame.pack(padx=20, pady=10, fill="x")

        hit = self.address_translator.tlb.hit_count
        miss = self.address_translator.tlb.miss_count
        ratio = self.address_translator.tlb.get_hit_ratio()

        self.tlb_label = tk.Label(
            tlb_frame,
            text=f"TLB Hits: {hit} | TLB Misses: {miss} | Hit Ratio: {ratio}%",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#059669"
        )
        self.tlb_label.pack(pady=10)

        for entry in self.address_translator.tlb.get_entries():
            tk.Label(
                tlb_frame,
                text=f"{entry['process']} | {entry['segment']} → Base: {entry['base']} KB",
                font=("Arial", 10),
                bg="white",
                fg="#374151"
            ).pack(anchor="w")

        # =========================================================
        # BUTTONS (LAST)
        # =========================================================

        button_frame = tk.Frame(scrollable_frame, bg="#f0f4f8")
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="← Back to Processes",
            command=lambda: self.switch_frames(self.frame3, 2),
            bg="#6b7280",
            fg="white",
            font=("Arial", 11, "bold"),
            width=22
        ).pack(side="left", padx=8)

        tk.Button(
            button_frame,
            text="🔄 Restart Simulator",
            command=self.restart,
            bg="#dc2626",
            fg="white",
            font=("Arial", 11, "bold"),
            width=22
        ).pack(side="left", padx=8)
    
    def populate_segment_table(self):
        """Populate segment table"""
        for item in self.segment_tree.get_children():
            self.segment_tree.delete(item)
        
        for seg in self.segment_table.get_all_segments():
            self.segment_tree.insert("", "end", values=(seg["process"], seg["segment"], seg["base"], seg["size"]))
    
    def translate_address(self):
        """Translate logical to physical address"""
        try:
            process = self.trans_process_entry.get().strip()
            segment = self.trans_segment_entry.get().strip()
            offset = int(self.trans_offset_entry.get())
            
            if not process or not segment:
                raise ValueError("Process and Segment cannot be empty")
            
            success, result, message = self.address_translator.translate(process, segment, offset)
            self.update_tlb_display()
            
            if success:
                self.trans_result_label.config(text=f"✅ {message}", fg="#059669", bg="#d1fae5")
                self.trans_result_label.master.config(bg="#d1fae5")
            else:
                self.trans_result_label.config(text=f"❌ {message}", fg="#dc2626", bg="#fee2e2")
                self.trans_result_label.master.config(bg="#fee2e2")
        except ValueError as e:
            self.trans_result_label.config(text=f"⚠️ Error: {str(e)}", fg="#dc2626", bg="#fee2e2")
            self.trans_result_label.master.config(bg="#fee2e2")
    
    def switch_frames(self, hide_frame, show_step):
        """Switch between frames"""
        if hide_frame:
            hide_frame.pack_forget()
        
        if show_step == 1:
            self.show_step1()
        elif show_step == 2:
            self.show_step2()
        elif show_step == 3:
            self.show_step3()
            
    def open_compare_mode(self):
        """Open Compare Mode window: runs all algorithms on the same workload"""
        has_add = any(e[0] == "add" for e in self.pending_processes)
        if not self.pending_processes or not has_add:
            messagebox.showwarning("No Processes", "Add at least one process before comparing.")
            return

        engine = CompareEngine(self.memory_manager.total_memory)
        results = engine.run_comparison(self.pending_processes)
        best_algo = engine.get_best_algorithm()

        # Open a new Toplevel window
        win = tk.Toplevel(self.root)
        win.title("Algorithm Comparison")
        win.geometry("1050x520")
        win.configure(bg="#f0f4f8")
        win.grab_set()  # Modal

        # Title
        title_frame = tk.Frame(win, bg="#7c3aed")
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="⚖️ Algorithm Comparison Dashboard",
                 font=("Arial", 18, "bold"), fg="white", bg="#7c3aed", pady=12).pack()

        # Subtitle: workload summary
        adds    = [e[1] for e in self.pending_processes if e[0] == "add"]
        deletes = [e[1] for e in self.pending_processes if e[0] == "delete"]
        summary = f"Added: {', '.join(adds)}"
        if deletes:
            summary += f"  |  Deleted: {', '.join(deletes)}"
        summary += f"  |  Memory: {self.memory_manager.total_memory} KB"
        tk.Label(win, text=summary,
                 font=("Arial", 10), fg="#374151", bg="#f0f4f8").pack(pady=(8, 0))

        # Best algorithm banner
        banner_bg = "#d1fae5"
        tk.Label(win, text=f"  🏆  Best Algorithm: {best_algo}  (lowest fragmentation + highest utilization)  ",
                 font=("Arial", 11, "bold"), fg="#065f46", bg=banner_bg,
                 relief="solid", bd=1).pack(pady=8, padx=20, fill="x")

        # Comparison table
        table_frame = tk.Frame(win, bg="#f0f4f8")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.configure("Compare.Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Compare.Treeview.Heading", font=("Arial", 11, "bold"),
                        background="#7c3aed", foreground="white")

        columns = ("Algorithm", "Used (KB)", "Free (KB)", "Int Frag (KB)",
                   "Ext Frag (KB)", "Free Blocks", "Utilization %")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                            height=len(ALGORITHMS), style="Compare.Treeview")

        col_widths = [130, 100, 100, 120, 120, 110, 120]
        for col, w in zip(columns, col_widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")

        # Tag for best row highlight
        tree.tag_configure("best", background="#d1fae5", foreground="#065f46")
        tree.tag_configure("normal", background="#f9fafb")

        for algo in ALGORITHMS:
            r = results[algo]
            tag = "best" if algo == best_algo else "normal"
            label = f"🏆 {algo}" if algo == best_algo else algo
            tree.insert("", "end", tags=(tag,), values=(
                label,
                r["memory_used"],
                r["free_memory"],
                r["internal_frag"],
                r["external_frag"],
                r["free_blocks"],
                f"{r['utilization']}%"
            ))

        tree.pack(fill="both", expand=True)

        # Failed processes note
        all_failed = []
        for algo, r in results.items():
            if r["failed_processes"]:
                all_failed.append(f"{algo}: {', '.join(r['failed_processes'])}")
        if all_failed:
            tk.Label(win, text="⚠️ Allocation failures: " + " | ".join(all_failed),
                     font=("Arial", 9), fg="#dc2626", bg="#f0f4f8").pack(pady=4)

        tk.Button(win, text="Close", command=win.destroy,
                  bg="#6b7280", fg="white", font=("Arial", 11, "bold"),
                  width=15, relief="flat", cursor="hand2").pack(pady=10)

    def restart(self):
        """Restart simulator"""

        self.memory_manager = MemoryManager()
        self.segment_table = SegmentTable()
        self.frag_calculator = FragmentationCalculator()

        self.process_manager = ProcessManager(
            self.memory_manager,
            self.segment_table,
            self.frag_calculator
        )

        self.address_translator = AddressTranslator(self.segment_table)

        self.pending_processes = []  # Clear compare mode process list
        # coalescing_var is intentionally kept so the user's choice survives restart
        
        if self.frame3:
            self.switch_frames(self.frame3, 1)
        elif self.frame2:
            self.switch_frames(self.frame2, 1)

        messagebox.showinfo(
            "Restart",
            "Simulator restarted. Please initialize memory."
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = MemorySimulatorGUI(root)
    root.mainloop()
