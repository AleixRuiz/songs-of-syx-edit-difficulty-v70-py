import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import struct
import zlib
import os

class DifficultyEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Songs of Syx Difficulty Editor")
        self.root.geometry("600x700")
        
        self.file_path = None
        self.decompressed_data = None
        self.settings = [] # List of dicts: {'name': str, 'offset': int, 'value': float, 'var': tk.DoubleVar}
        
        # Top Frame: File Operations
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill=tk.X)
        
        self.btn_load = tk.Button(top_frame, text="Load Save File", command=self.load_file)
        self.btn_load.pack(side=tk.LEFT, padx=10)
        
        self.lbl_file = tk.Label(top_frame, text="No file loaded", fg="gray")
        self.lbl_file.pack(side=tk.LEFT, padx=10)
        
        self.btn_save = tk.Button(top_frame, text="Save Changes", command=self.save_file, state=tk.DISABLED)
        self.btn_save.pack(side=tk.RIGHT, padx=10)

        # Middle Frame: Settings List (Scrollable)
        mid_frame = tk.Frame(root)
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas and Scrollbar
        self.canvas = tk.Canvas(mid_frame)
        self.scrollbar = tk.Scrollbar(mid_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Bottom Frame: Bulk Actions
        bottom_frame = tk.Frame(root, pady=10)
        bottom_frame.pack(fill=tk.X)
        
        tk.Button(bottom_frame, text="Set All to Normal (1.0)", command=lambda: self.bulk_set(1.0)).pack(side=tk.LEFT, padx=10)
        tk.Button(bottom_frame, text="Set All to Hard (0.4)", command=lambda: self.bulk_set(0.4)).pack(side=tk.LEFT, padx=10)
        tk.Button(bottom_frame, text="Set All to Easy (1.5)", command=lambda: self.bulk_set(1.5)).pack(side=tk.LEFT, padx=10)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Save Files", "*.save"), ("All Files", "*.*")])
        if not file_path:
            return
            
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Try decompressing
            try:
                self.decompressed_data = bytearray(zlib.decompress(raw_data))
                print("File decompressed successfully.")
            except zlib.error:
                # Maybe it's already decompressed
                self.decompressed_data = bytearray(raw_data)
                print("File read as raw (assuming already decompressed).")
            
            self.file_path = file_path
            self.lbl_file.config(text=os.path.basename(file_path), fg="black")
            
            self.scan_settings()
            self.populate_ui()
            self.btn_save.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def scan_settings(self):
        self.settings = []
        data = self.decompressed_data
        
        # Find the start of the block
        # We look for "CIVIC_OPINIO" (truncated) in UTF-16LE to avoid overlap issues on the last char
        search_pattern = "CIVIC_OPINIO".encode('utf-16le')
        
        start_index = 0
        found_offset = -1
        
        while True:
            index = data.find(search_pattern, start_index)
            if index == -1:
                break
                
            # Check the 2 bytes before (Length)
            # CIVIC_OPINION length is 13 (0x0D)
            if index >= 2:
                len_bytes = data[index-2:index]
                len_val = struct.unpack('<H', len_bytes)[0]
                
                if len_val == 13:
                    found_offset = index - 2
                    break
            
            start_index = index + 1
        
        if found_offset == -1:
            messagebox.showwarning("Warning", "Could not find difficulty settings block (CIVIC_OPINION not found).")
            return
            
        # The length bytes (2 bytes) are immediately before the name
        current_offset = found_offset
        
        print(f"Scanning started at offset {current_offset}")
        
        while True:
            try:
                if current_offset >= len(data):
                    break
                    
                # Read name length
                len_bytes = data[current_offset:current_offset+2]
                if len(len_bytes) < 2: break
                
                name_len = struct.unpack('<H', len_bytes)[0]
                
                # Sanity check to stop scanning
                if name_len == 0 or name_len > 100:
                    break
                
                # Read name
                name_start = current_offset + 2
                name_end = name_start + name_len * 2
                raw_name_bytes = data[name_start:name_end]
                
                if len(raw_name_bytes) != name_len * 2: break
                
                # Calculate potential value offsets
                normal_value_offset = name_end
                overlap_value_offset = name_end - 1
                
                # Check for overlap
                # Heuristic: Check if the byte at overlap_value_offset looks like the start of a double (0.something or similar)
                # Common double starts for 0.0 - 2.0 range: 3F, 40, 00(0.0)
                byte_at_overlap = data[overlap_value_offset]
                
                is_overlap = False
                if byte_at_overlap in [0x3F, 0x40, 0xBF, 0xC0]: 
                     is_overlap = True
                
                value_offset = overlap_value_offset if is_overlap else normal_value_offset
                
                # Decode name
                real_name_bytes = raw_name_bytes
                if is_overlap:
                    real_name_bytes = raw_name_bytes[:-1] + b'\x00'
                
                try:
                    name = real_name_bytes.decode('utf-16le')
                except:
                    name = "<Decode Error>"
                
                # Read value
                value_bytes = data[value_offset:value_offset+8]
                if len(value_bytes) < 8: break
                
                value = struct.unpack('>d', value_bytes)[0]
                
                # Store setting
                self.settings.append({
                    'name': name,
                    'offset': value_offset,
                    'value': value,
                    'var': tk.DoubleVar(value=value)
                })
                
                # Move to next
                # Value (8) + Unknown (8)
                current_offset = value_offset + 16
                
            except Exception as e:
                print(f"Error scanning at {current_offset}: {e}")
                break
        
        print(f"Found {len(self.settings)} settings.")

    def populate_ui(self):
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Headers
        tk.Label(self.scrollable_frame, text="Setting Name", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self.scrollable_frame, text="Value", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        for i, setting in enumerate(self.settings):
            row = i + 1
            tk.Label(self.scrollable_frame, text=setting['name']).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            entry = tk.Entry(self.scrollable_frame, textvariable=setting['var'], width=10)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)

    def bulk_set(self, value):
        for setting in self.settings:
            setting['var'].set(value)

    def save_file(self):
        if not self.file_path or not self.decompressed_data:
            return
            
        try:
            # Update data in memory
            for setting in self.settings:
                new_val = setting['var'].get()
                offset = setting['offset']
                
                new_bytes = struct.pack('>d', new_val)
                
                # Write bytes to bytearray
                for i in range(8):
                    self.decompressed_data[offset + i] = new_bytes[i]
            
            # Compress
            print("Compressing data...")
            compressed_data = zlib.compress(self.decompressed_data)
            
            # Save dialog
            original_dir = os.path.dirname(self.file_path)
            original_name = os.path.basename(self.file_path)
            new_name = "edited_" + original_name
            
            save_path = filedialog.asksaveasfilename(
                initialdir=original_dir,
                initialfile=new_name,
                defaultextension=".save",
                filetypes=[("Save Files", "*.save")]
            )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(compressed_data)
                messagebox.showinfo("Success", f"File saved to:\n{save_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DifficultyEditor(root)
    root.mainloop()
