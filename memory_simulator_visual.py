import tkinter as tk
from tkinter import messagebox, ttk

class MemoryManagementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Management Simulator")
        self.root.geometry("800x700")
        
        # Memory structure: list of dictionaries with name, size, and type
        self.memory = []
        self.total_memory = 0
        self.current_step = 1
        
        # Segment table: stores metadata for each segment (OS Concept: Segmentation)
        # Each entry contains process ID, segment name, base address, and size
        self.segment_table = []
        
        # Internal fragmentation tracking (OS Concept: Memory waste within allocated blocks)
        self.internal_fragmentation = 0
        self.block_size = 10  # Fixed block size for allocation (simulates memory allocation in fixed units)
        
        # Create frames for each step
        self.frame1 = None  # Memory initialization
        self.frame2 = None  # Process input
        self.frame3 = None  # Visualization
        
        self.show_step1()
    
    def switch_frames(self, hide_frame, show_step):
        """Switch between different frames/steps"""
        if hide_frame:
            hide_frame.pack_forget()
        
        if show_step == 1:
            self.show_step1()
        elif show_step == 2:
            self.show_step2()
        elif show_step == 3:
            self.show_step3()
    
    def show_step1(self):
        """Step 1: Memory Initialization"""
        self.current_step = 1
        self.frame1 = tk.Frame(self.root)
        self.frame1.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(self.frame1, text="Memory Management Simulator", 
                font=("Arial", 20, "bold")).pack(pady=20)
        
        tk.Label(self.frame1, text="Step 1: Initialize Memory", 
                font=("Arial", 14, "bold"), fg="blue").pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.frame1)
        input_frame.pack(pady=30)
        
        tk.Label(input_frame, text="Total Memory Size (KB):", 
                font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.memory_size_entry = tk.Entry(input_frame, width=20, font=("Arial", 12))
        self.memory_size_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Next button
        tk.Button(self.frame1, text="Next", command=self.initialize_memory, 
                 bg="#4CAF50", fg="white", font=("Arial", 12), 
                 width=15, height=2).pack(pady=20)
    
    def initialize_memory(self):
        """Initialize memory and move to step 2"""
        try:
            size = int(self.memory_size_entry.get())
            if size <= 0:
                raise ValueError
            
            self.total_memory = size
            # Memory starts as one large free block
            self.memory = [{"name": "Free", "size": size, "type": "free"}]
            self.segment_table = []  # Reset segment table
            self.internal_fragmentation = 0  # Reset internal fragmentation
            
            messagebox.showinfo("Success", f"Memory initialized with {size} KB")
            self.switch_frames(self.frame1, 2)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer")
    
    def show_step2(self):
        """Step 2: Add Processes"""
        self.current_step = 2
        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(self.frame2, text="Memory Management Simulator", 
                font=("Arial", 20, "bold")).pack(pady=10)
        
        tk.Label(self.frame2, text="Step 2: Add Processes with Segments", 
                font=("Arial", 14, "bold"), fg="blue").pack(pady=10)
        
        # Process input frame
        input_frame = tk.LabelFrame(self.frame2, text="Process Details", 
                                    font=("Arial", 12), padx=20, pady=20)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Process Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.process_name_entry = tk.Entry(input_frame, width=25, font=("Arial", 11))
        self.process_name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(input_frame, text="Code Segment Size (KB):", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=5)
        self.code_size_entry = tk.Entry(input_frame, width=25, font=("Arial", 11))
        self.code_size_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(input_frame, text="Data Segment Size (KB):", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=5)
        self.data_size_entry = tk.Entry(input_frame, width=25, font=("Arial", 11))
        self.data_size_entry.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(input_frame, text="Stack Segment Size (KB):", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=5)
        self.stack_size_entry = tk.Entry(input_frame, width=25, font=("Arial", 11))
        self.stack_size_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.frame2)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add Process", command=self.add_process, 
                 bg="#2196F3", fg="white", font=("Arial", 12), 
                 width=15, height=2).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Next (Visualize)", command=lambda: self.switch_frames(self.frame2, 3), 
                 bg="#FF9800", fg="white", font=("Arial", 12), 
                 width=15, height=2).pack(side="left", padx=10)
        
        # Delete Process Section
        delete_frame = tk.LabelFrame(self.frame2, text="Delete Process", 
                                     font=("Arial", 12), padx=20, pady=15)
        delete_frame.pack(pady=10)
        
        tk.Label(delete_frame, text="Process Name to Delete:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.delete_process_entry = tk.Entry(delete_frame, width=25, font=("Arial", 11))
        self.delete_process_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Button(delete_frame, text="Delete Process", command=self.delete_process, 
                 bg="#FF5722", fg="white", font=("Arial", 11), 
                 width=15).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Add Refresh Visualization button
        tk.Button(self.frame2, text="Refresh Visualization", command=self.refresh_visualization, 
                 bg="#9C27B0", fg="white", font=("Arial", 11), 
                 width=20).pack(pady=5)
    
    def add_process(self):
        """Add a process with three segments: Code, Data, Stack"""
        try:
            process_name = self.process_name_entry.get().strip()
            code_size = int(self.code_size_entry.get())
            data_size = int(self.data_size_entry.get())
            stack_size = int(self.stack_size_entry.get())
            
            if not process_name:
                raise ValueError("Process name cannot be empty")
            if code_size < 0 or data_size < 0 or stack_size < 0:
                raise ValueError("Segment sizes must be non-negative")
            
            # Allocate segments using segmentation technique
            success = self.allocate_segments(process_name, code_size, data_size, stack_size)
            
            if success:
                messagebox.showinfo("Success", f"Process {process_name} added successfully")
                # Clear input fields
                self.process_name_entry.delete(0, tk.END)
                self.code_size_entry.delete(0, tk.END)
                self.data_size_entry.delete(0, tk.END)
                self.stack_size_entry.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def allocate_segments(self, process_name, code_size, data_size, stack_size):
        """Allocate three segments for a process in memory using segmentation technique
        
        OS Concept: Segmentation - divides process memory into logical segments (Code, Data, Stack)
        Each segment has a base address and size stored in the segment table
        """
        segments = [
            ("Code", code_size),
            ("Data", data_size),
            ("Stack", stack_size)
        ]
        
        for seg_type, seg_size in segments:
            if seg_size == 0:
                continue
            
            seg_name = f"{process_name} {seg_type}"
            
            # Calculate allocated size (rounded to block_size for internal fragmentation simulation)
            allocated_size = ((seg_size + self.block_size - 1) // self.block_size) * self.block_size
            internal_frag = allocated_size - seg_size
            self.internal_fragmentation += internal_frag
            
            # First-fit allocation: find first free block that fits
            allocated = False
            base_address = 0
            
            # Calculate base address by summing previous blocks
            for i, block in enumerate(self.memory):
                if block["type"] == "free" and block["size"] >= allocated_size:
                    if block["size"] == allocated_size:
                        # Exact fit
                        self.memory[i] = {"name": seg_name, "size": allocated_size, "type": "used"}
                    else:
                        # Split the free block (OS Concept: Dynamic Partitioning)
                        remaining = block["size"] - allocated_size
                        self.memory[i] = {"name": seg_name, "size": allocated_size, "type": "used"}
                        self.memory.insert(i + 1, {"name": "Free", "size": remaining, "type": "free"})
                    allocated = True
                    break
                base_address += block["size"]
            
            if not allocated:
                messagebox.showerror("Error", f"Not enough memory for {seg_name} ({allocated_size} KB)")
                return False
            
            # Update segment table (OS Concept: Segment Table for address translation)
            self.update_segment_table(process_name, seg_type, base_address, allocated_size)
        
        return True
    
    def update_segment_table(self, process, segment, base, size):
        """Update the segment table with new segment entry
        
        OS Concept: Segment Table - maintains mapping of logical segments to physical addresses
        """
        self.segment_table.append({
            "process": process,
            "segment": segment,
            "base": base,
            "size": size
        })
    
    def show_step3(self):
        """Step 3: Complete Memory Management Dashboard"""
        self.current_step = 3
        self.frame3 = tk.Frame(self.root)
        self.frame3.pack(fill="both", expand=True)
        
        # Create scrollable canvas
        main_canvas = tk.Canvas(self.frame3)
        scrollbar = tk.Scrollbar(self.frame3, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        tk.Label(scrollable_frame, text="OS Memory Management Dashboard", 
                font=("Arial", 18, "bold")).pack(pady=10)
        
        # Memory Visualization Section
        viz_frame = tk.LabelFrame(scrollable_frame, text="Memory Visualization", 
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        viz_frame.pack(padx=20, pady=10, fill="x")
        
        self.canvas = tk.Canvas(viz_frame, width=700, height=300, bg="white", relief="solid", borderwidth=2)
        self.canvas.pack(pady=5)
        self.draw_memory_blocks()
        
        # Fragmentation Display Section
        frag_frame = tk.LabelFrame(scrollable_frame, text="Fragmentation Analysis", 
                                   font=("Arial", 12, "bold"), padx=10, pady=10)
        frag_frame.pack(padx=20, pady=10, fill="x")
        
        ext_frag = self.calculate_external_fragmentation()
        self.ext_frag_label = tk.Label(frag_frame, text=f"External Fragmentation: {ext_frag} KB", 
                                       font=("Arial", 11), fg="red")
        self.ext_frag_label.pack(pady=5)
        
        self.int_frag_label = tk.Label(frag_frame, text=f"Internal Fragmentation: {self.internal_fragmentation} KB", 
                                       font=("Arial", 11), fg="orange")
        self.int_frag_label.pack(pady=5)
        
        # Segment Table Section
        seg_frame = tk.LabelFrame(scrollable_frame, text="Segment Table", 
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        seg_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.segment_tree = ttk.Treeview(seg_frame, columns=("Process", "Segment", "Base", "Size"), 
                                         show="headings", height=6)
        self.segment_tree.heading("Process", text="Process ID")
        self.segment_tree.heading("Segment", text="Segment Name")
        self.segment_tree.heading("Base", text="Base Address")
        self.segment_tree.heading("Size", text="Size (KB)")
        
        self.segment_tree.column("Process", width=150)
        self.segment_tree.column("Segment", width=150)
        self.segment_tree.column("Base", width=150)
        self.segment_tree.column("Size", width=150)
        
        self.segment_tree.pack(pady=5, fill="both", expand=True)
        self.populate_segment_table()
        
        # Address Translation Section
        addr_frame = tk.LabelFrame(scrollable_frame, text="Address Translation", 
                                   font=("Arial", 12, "bold"), padx=10, pady=10)
        addr_frame.pack(padx=20, pady=10, fill="x")
        
        input_frame = tk.Frame(addr_frame)
        input_frame.pack(pady=5)
        
        tk.Label(input_frame, text="Process ID:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.trans_process_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.trans_process_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="Segment:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.trans_segment_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.trans_segment_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(input_frame, text="Offset:", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5)
        self.trans_offset_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.trans_offset_entry.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(addr_frame, text="Translate Address", command=self.translate_address, 
                 bg="#4CAF50", fg="white", font=("Arial", 10), width=20).pack(pady=5)
        
        self.trans_result_label = tk.Label(addr_frame, text="", font=("Arial", 11, "bold"), fg="blue")
        self.trans_result_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Back to Add Process", 
                 command=lambda: self.switch_frames(self.frame3, 2), 
                 bg="#9E9E9E", fg="white", font=("Arial", 11), 
                 width=20).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Restart", 
                 command=self.restart, 
                 bg="#f44336", fg="white", font=("Arial", 11), 
                 width=20).pack(side="left", padx=5)
    
    def draw_memory_blocks(self):
        """Draw memory blocks as rectangles on canvas
        
        OS Concept: Visual representation of memory partitioning and segmentation
        Blue blocks = allocated segments, Gray blocks = free memory
        """
        if not self.memory:
            return
        
        canvas_width = 700
        canvas_height = 300
        margin = 30
        block_width = 400
        
        # Calculate total height available for blocks
        available_height = canvas_height - 2 * margin
        
        # Draw each memory block
        y_offset = margin
        current_address = 0
        
        for block in self.memory:
            # Calculate block height proportional to size
            block_height = max((block["size"] / self.total_memory) * available_height, 15)
            
            # Determine color based on type
            if block["type"] == "free":
                color = "#E0E0E0"  # Light gray for free memory
                text_color = "black"
            else:
                color = "#2196F3"  # Blue for used segments
                text_color = "white"
            
            # Draw rectangle
            x1 = (canvas_width - block_width) // 2
            y1 = y_offset
            x2 = x1 + block_width
            y2 = y1 + block_height
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2)
            
            # Add text label with address range
            text_y = y1 + block_height / 2
            label_text = f"{block['name']}\n{block['size']} KB\n[{current_address}-{current_address + block['size']}]"
            self.canvas.create_text((x1 + x2) / 2, text_y, 
                                   text=label_text, 
                                   font=("Arial", 9, "bold"), fill=text_color)
            
            y_offset += block_height
            current_address += block["size"]
    
    def calculate_external_fragmentation(self):
        """Calculate external fragmentation: sum of all free blocks that are scattered
        
        OS Concept: External Fragmentation - free memory scattered in small non-contiguous blocks
        that cannot be used for larger allocations
        """
        free_blocks = [block["size"] for block in self.memory if block["type"] == "free"]
        
        # External fragmentation occurs when free memory is scattered
        # If there are multiple free blocks, they represent fragmentation
        if len(free_blocks) <= 1:
            return 0
        
        # Sum all free blocks except the largest (which is still usable)
        if free_blocks:
            return sum(free_blocks) - max(free_blocks)
        return 0
    
    def calculate_internal_fragmentation(self):
        """Calculate internal fragmentation: wasted space within allocated blocks
        
        OS Concept: Internal Fragmentation - memory wasted when allocated block size
        is larger than requested size (due to fixed block allocation)
        """
        return self.internal_fragmentation
    
    def delete_process(self):
        """Delete a process and convert its segments to free memory blocks"""
        if not self.memory:
            messagebox.showerror("Error", "No memory initialized")
            return
        
        try:
            process_name = self.delete_process_entry.get().strip()
            
            if not process_name:
                raise ValueError("Process name cannot be empty")
            
            # Find all segments belonging to this process
            deleted_count = 0
            
            for i, block in enumerate(self.memory):
                # Check if block belongs to the process
                if block["name"].startswith(process_name + " "):
                    # Convert used segment to free memory
                    self.memory[i] = {"name": "Free", "size": block["size"], "type": "free"}
                    deleted_count += 1
            
            # Remove from segment table
            self.segment_table = [seg for seg in self.segment_table if seg["process"] != process_name]
            
            if deleted_count == 0:
                messagebox.showerror("Error", f"Process '{process_name}' not found")
                return
            
            messagebox.showinfo("Success", f"Process {process_name} deleted ({deleted_count} segments freed)")
            self.delete_process_entry.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def refresh_visualization(self):
        """Refresh the canvas visualization and fragmentation display"""
        if self.current_step == 3 and hasattr(self, 'canvas'):
            # Clear canvas
            self.canvas.delete("all")
            # Redraw memory blocks
            self.draw_memory_blocks()
            # Update fragmentation
            ext_frag = self.calculate_external_fragmentation()
            self.ext_frag_label.config(text=f"External Fragmentation: {ext_frag} KB")
            self.int_frag_label.config(text=f"Internal Fragmentation: {self.internal_fragmentation} KB")
            # Update segment table
            self.populate_segment_table()
    
    def populate_segment_table(self):
        """Populate the segment table treeview with current segments
        
        OS Concept: Segment Table Display - shows the mapping maintained by OS
        for logical to physical address translation
        """
        # Clear existing entries
        for item in self.segment_tree.get_children():
            self.segment_tree.delete(item)
        
        # Add all segments
        for seg in self.segment_table:
            self.segment_tree.insert("", "end", values=(
                seg["process"], 
                seg["segment"], 
                seg["base"], 
                seg["size"]
            ))
    
    def translate_address(self):
        """Translate logical address to physical address using segmentation
        
        OS Concept: Address Translation in Segmentation
        Logical Address = (Segment, Offset)
        Physical Address = Base Address + Offset
        
        Validates offset against segment limit to prevent segmentation fault
        """
        try:
            process = self.trans_process_entry.get().strip()
            segment = self.trans_segment_entry.get().strip()
            offset = int(self.trans_offset_entry.get())
            
            if not process or not segment:
                raise ValueError("Process and Segment cannot be empty")
            
            # Find segment in segment table
            seg_entry = None
            for seg in self.segment_table:
                if seg["process"] == process and seg["segment"] == segment:
                    seg_entry = seg
                    break
            
            if not seg_entry:
                self.trans_result_label.config(
                    text=f"Error: Segment '{segment}' not found for process '{process}'",
                    fg="red"
                )
                return
            
            # Validate offset (OS Concept: Segment Limit Check)
            if offset >= seg_entry["size"]:
                self.trans_result_label.config(
                    text=f"Segmentation Fault: Offset {offset} exceeds segment limit {seg_entry['size']}",
                    fg="red"
                )
                return
            
            if offset < 0:
                self.trans_result_label.config(
                    text=f"Error: Offset cannot be negative",
                    fg="red"
                )
                return
            
            # Calculate physical address (OS Concept: Address Translation)
            physical_address = seg_entry["base"] + offset
            
            self.trans_result_label.config(
                text=f"Physical Address = {seg_entry['base']} + {offset} = {physical_address} KB",
                fg="green"
            )
            
        except ValueError as e:
            self.trans_result_label.config(
                text=f"Error: {str(e)}",
                fg="red"
            )
    
    def restart(self):
        """Restart the simulator from Step 1 with fresh memory"""
        # Reset all data
        self.memory = []
        self.total_memory = 0
        self.current_step = 1
        self.segment_table = []
        self.internal_fragmentation = 0
        
        # Switch to Step 1
        if self.frame3:
            self.switch_frames(self.frame3, 1)
        elif self.frame2:
            self.switch_frames(self.frame2, 1)
        
        messagebox.showinfo("Restart", "Simulator restarted. Please initialize memory.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryManagementSimulator(root)
    root.mainloop()
