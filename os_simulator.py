import time
import random
import matplotlib.pyplot as plt
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import scrolledtext
import threading
from itertools import cycle

# ===============================
# ANIMATION UTILITIES
# ===============================

class AnimationHelper:
    """Helper class for smooth animations and visual effects"""
    
    @staticmethod
    def animate_text_insertion(widget, text, delay=10, char_delay=0):
        """Smoothly insert text character by character"""
        lines = text.split('\n')
        for line_idx, line in enumerate(lines):
            for char_idx, char in enumerate(line):
                widget.insert(tk.END, char)
                widget.see(tk.END)
                widget.update()
                if char_delay > 0:
                    time.sleep(char_delay / 1000.0)
            widget.insert(tk.END, '\n')
            widget.update()
            if delay > 0:
                time.sleep(delay / 1000.0)
    
    @staticmethod
    def create_pulse_effect(widget, duration=500):
        """Create a pulsing color effect"""
        original_color = widget.cget('bg')
        
        def pulse():
            colors = ['#E8F4F8', '#D0E8F0', '#B8DCE8', '#D0E8F0']
            color_cycle = cycle(colors)
            
            for _ in range(len(colors) * 2):
                widget.configure(bg=next(color_cycle))
                widget.update()
                time.sleep(duration / (len(colors) * 2) / 1000.0)
            
            widget.configure(bg=original_color)
        
        thread = threading.Thread(target=pulse, daemon=True)
        thread.start()
    
    @staticmethod
    def fade_frame(widget, show=True, steps=10, duration=300):
        """Fade in/out effect for frames"""
        if show:
            widget.pack()
        
        thread = threading.Thread(target=lambda: _fade_worker(widget, show, steps, duration), daemon=True)
        thread.start()
    
    @staticmethod
    def button_press_animation(button):
        """Button click animation"""
        original_color = button.cget('bg')
        button.configure(bg='#004578')
        button.update()
        time.sleep(0.05)
        button.configure(bg=original_color)


def _fade_worker(widget, show, steps, duration):
    """Worker function for fade effect"""
    step_duration = duration / steps / 1000.0
    for i in range(steps):
        try:
            alpha = (i / steps) if show else (1 - i / steps)
            widget.update()
            time.sleep(step_duration)
        except:
            break
    if not show:
        widget.pack_forget()


# ===============================
# PROCESS CONTROL BLOCK
# ===============================

class PCB:

    def __init__(self, pid, burst, memory):

        self.pid = pid
        self.burst_time = burst
        self.remaining = burst
        self.memory = memory
        self.state = "READY"
        self.waiting = 0
        self.turnaround = 0


# ===============================
# PROCESS MANAGER
# ===============================

class ProcessManager:

    def __init__(self):

        self.processes = []

    def create_process(self):

        pid = len(self.processes) + 1

        burst = random.randint(1, 15)

        memory = random.randint(50, 300)

        pcb = PCB(pid, burst, memory)

        self.processes.append(pcb)

        return f"Process {pid} created with burst time {burst}ms and memory {memory}MB"

    def get_process_table(self):

        if not self.processes:
            return "No processes created yet."

        table = "PID | STATE | BURST | REMAIN | MEMORY\n"
        table += "-" * 45 + "\n"
        for p in self.processes:
            table += f"{p.pid:3} | {p.state:6} | {p.burst_time:5} | {p.remaining:6} | {p.memory:6}\n"

        return table


# ===============================
# FCFS CPU SCHEDULER
# ===============================

class CPUScheduler:

    def __init__(self, processes):

        self.processes = processes

        self.timeline = []
        self.log = []

    def fcfs(self):

        time_counter = 0

        self.log.append("CPU Scheduling Started (FCFS)\n")

        for process in self.processes:

            if process.remaining > 0:

                process.state = "RUNNING"

                self.log.append(f"Running P{process.pid}")

                for i in range(process.remaining):

                    self.timeline.append(process.pid)

                    process.remaining -= 1

                    time_counter += 1

                process.state = "TERMINATED"

                process.turnaround = time_counter

                self.log.append(f"P{process.pid} finished (Turnaround: {process.turnaround})")

        return self.get_log()

    def get_log(self):
        return "\n".join(self.log)

    def draw_gantt(self):

        fig, ax = plt.subplots(figsize=(14, 4))

        # Color palette for processes
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                 '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#ABEBC6']
        
        # Create a color map for each process
        process_colors = {}
        for idx, process in enumerate(self.processes):
            process_colors[process.pid] = colors[idx % len(colors)]

        start = 0

        for pid in self.timeline:
            color = process_colors[pid]
            ax.barh(0, 1, left=start, height=0.6, color=color, edgecolor='black', linewidth=1.5)
            ax.text(start + 0.5, 0, f"P{pid}", ha='center', va='center', 
                   fontweight='bold', fontsize=11, color='white')
            start += 1

        ax.set_xlim(0, len(self.timeline))
        ax.set_title("CPU Gantt Chart (FCFS Scheduling)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Time Units", fontsize=11)
        ax.set_yticks([])
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=process_colors[pid], edgecolor='black', label=f'P{pid}')
                          for pid in process_colors.keys()]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

        plt.tight_layout()
        plt.show()


# ===============================
# MEMORY MANAGER
# ===============================

class MemoryManager:

    def __init__(self):

        self.partitions = [200, 200, 300, 400]

        self.allocated = {}
        self.log = []

    def allocate(self, process):

        for size in self.partitions:

            if size >= process.memory and size not in self.allocated:

                self.allocated[size] = process.pid

                frag = size - process.memory

                self.log.append(f"P{process.pid} allocated to {size}MB partition")
                self.log.append(f"Internal Fragmentation: {frag}MB")

                return True

        self.log.append(f"ERROR: No memory partition available for P{process.pid}")
        return False

    def get_memory_map(self):

        result = "MEMORY MAP\n"
        result += "-" * 40 + "\n"

        for p in self.partitions:

            if p in self.allocated:
                result += f"{p}MB -> Process {self.allocated[p]}\n"
            else:
                result += f"{p}MB -> FREE\n"

        total_allocated = sum([self.allocated[p] for p in self.allocated])
        result += "-" * 40 + "\n"
        result += f"Total Memory: {sum(self.partitions)}MB\n"

        return result
    
    def get_log(self):
        return "\n".join(self.log)


# ===============================
# FILE SYSTEM
# ===============================

class FileSystem:

    def __init__(self):

        self.files = {}
        self.log = []

    def create_file(self, name, data):

        self.files[name] = data

        self.log.append(f"File '{name}' created successfully")
        return f"File '{name}' created successfully"

    def delete_file(self, name):

        if name in self.files:

            del self.files[name]

            self.log.append(f"File '{name}' deleted")
            return f"File '{name}' deleted"

        else:

            self.log.append(f"Error: File '{name}' not found")
            return f"Error: File '{name}' not found"

    def list_files(self):

        if not self.files:
            return "No files in system"

        result = "FILES IN SYSTEM\n"
        result += "-" * 40 + "\n"
        for i, f in enumerate(self.files, 1):
            result += f"{i}. {f} ({len(self.files[f])} bytes)\n"

        return result
    
    def get_log(self):
        return "\n".join(self.log)


# ===============================
# PRINTER I/O SPOOLING
# ===============================

class Printer:

    def __init__(self):

        self.queue = deque()
        self.log = []

    def add_job(self, job_name):

        self.queue.append(job_name)

        self.log.append(f"Print job '{job_name}' added to queue")
        return f"Job '{job_name}' added to queue (Queue size: {len(self.queue)})"

    def process(self):

        if not self.queue:
            return "Print queue is empty"

        result = "PROCESSING PRINT JOBS\n"
        result += "-" * 40 + "\n"

        while self.queue:

            job = self.queue.popleft()

            result += f"Printing: {job}\n"
            self.log.append(f"Printed: {job}")

        result += "-" * 40 + "\nAll jobs printed successfully!"

        return result
    
    def get_queue_status(self):
        if not self.queue:
            return "Print Queue: Empty"
        return f"Print Queue: {len(self.queue)} jobs waiting\n" + "\n".join([f"  {i+1}. {job}" for i, job in enumerate(self.queue)])
    
    def get_log(self):
        return "\n".join(self.log) if self.log else "No print jobs processed yet"


# ===============================
# DISK SCHEDULER
# ===============================

class DiskScheduler:

    def __init__(self):

        self.requests = []

        self.head = 50
        self.log = []

    def add_request(self, request):

        try:
            r = int(request)
            if 0 <= r <= 200:
                self.requests.append(r)
                self.log.append(f"Disk request added: {r}")
                return f"Request {r} added successfully"
            else:
                return "Error: Request must be between 0 and 200"
        except:
            return "Error: Invalid request value"

    def fcfs(self):

        if not self.requests:
            return "No disk requests to process"

        head = self.head

        total = 0

        result = "FCFS DISK SCHEDULING\n"
        result += "-" * 40 + "\n"

        for r in self.requests:

            dist = abs(head - r)

            total += dist

            result += f"{head} -> {r} (distance: {dist})\n"

            head = r

        result += "-" * 40 + "\n"
        result += f"Total head movement: {total} cylinders"

        self.log.append(f"FCFS scheduled. Total movement: {total}")

        return result

    def scan(self):

        if not self.requests:
            return "No disk requests to process"

        head = self.head

        disk_size = 200

        left = [r for r in self.requests if r < head]

        right = [r for r in self.requests if r >= head]

        left.sort(reverse=True)

        right.sort()

        movement = 0

        result = "SCAN DISK SCHEDULING\n"
        result += "-" * 40 + "\n"

        for r in right:

            dist = abs(head - r)
            movement += dist

            result += f"{head} -> {r} (distance: {dist})\n"

            head = r

        movement += abs(head - (disk_size - 1))
        result += f"{head} -> {disk_size - 1} (distance: {abs(head - (disk_size - 1))})\n"
        head = disk_size - 1

        for r in left:

            dist = abs(head - r)
            movement += dist

            result += f"{head} -> {r} (distance: {dist})\n"

            head = r

        result += "-" * 40 + "\n"
        result += f"Total head movement: {movement} cylinders"

        self.log.append(f"SCAN scheduled. Total movement: {movement}")

        return result
    
    def get_log(self):
        return "\n".join(self.log) if self.log else "No disk operations yet"


# ===============================
# OS SIMULATOR
# ===============================

# ===============================
# OS SIMULATOR WITH GUI
# ===============================

class OSSimulator:

    def __init__(self):

        self.pm = ProcessManager()

        self.mm = MemoryManager()

        self.fs = FileSystem()

        self.printer = Printer()

        self.disk = DiskScheduler()
        
        self.scheduler = None

    def create_gui(self):
        """Create the modern Windows-like GUI using tkinter with animations"""
        
        # Create main window
        root = tk.Tk()
        root.title("OS Simulator - Windows Edition")
        root.geometry("1200x750")
        root.minsize(1000, 600)
        
        # Configure window style
        root.configure(bg='#F0F0F0')
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure enhanced colors and styles
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), background='#F0F0F0', foreground='#0078D4')
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'), background='#F0F0F0')
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.map('TButton', 
                 background=[('active', '#005A9E'), ('pressed', '#004578')],
                 foreground=[('active', 'white')])
        
        # Title with animation
        title_frame = tk.Frame(root, bg='#F0F0F0')
        title_frame.pack(fill='x', padx=20, pady=10)
        title_label = tk.Label(title_frame, text="Operating System Simulator", 
                              font=('Segoe UI', 16, 'bold'), fg='#0078D4', bg='#F0F0F0')
        title_label.pack()
        
        # Add a subtle divider
        divider = tk.Frame(root, height=2, bg='#0078D4')
        divider.pack(fill='x', padx=10)
        
        # Create notebook (tabs) with enhanced styling
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Process Management Tab
        process_tab = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(process_tab, text='📋 Processes')
        self.setup_process_tab(process_tab)
        
        # CPU Scheduler Tab
        cpu_tab = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(cpu_tab, text='⚙️ CPU Scheduler')
        self.setup_cpu_tab(cpu_tab)
        
        # Memory Management Tab
        memory_tab = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(memory_tab, text='💾 Memory')
        self.setup_memory_tab(memory_tab)
        
        # File System Tab
        file_tab = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(file_tab, text='📂 File System')
        self.setup_file_tab(file_tab)
        
        # Printer Tab
        printer_tab = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(printer_tab, text='🖨️ Printer')
        self.setup_printer_tab(printer_tab)
        
        # Disk Scheduler Tab
        disk_tab = tk.Frame(notebook, bg='#F0F0F0')
        notebook.add(disk_tab, text='💿 Disk Scheduler')
        self.setup_disk_tab(disk_tab)
        # Exit Button with enhanced styling
        exit_frame = tk.Frame(root, bg='#F0F0F0')
        exit_frame.pack(fill='x', padx=10, pady=10)
        exit_button = tk.Button(exit_frame, text="⛔ Exit", command=root.quit, 
                               font=('Segoe UI', 11, 'bold'), bg='#D13438', fg='white', 
                               padx=20, pady=8, activebackground='#A02830')
        exit_button.pack(side='right')
        
        self.root = root
        return root
    
    def setup_process_tab(self, parent):
        """Setup Process Management tab"""
        # Buttons frame with enhanced styling
        btn_frame = tk.Frame(parent, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="➕ Create Process", command=self.create_process,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="📋 Show Processes", command=self.show_processes,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Output frame
        output_frame = tk.LabelFrame(parent, text="Process Information", font=('Segoe UI', 10, 'bold'),
                                    bg='#F0F0F0', fg='#333333')
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.process_output = scrolledtext.ScrolledText(output_frame, height=20, width=60, 
                                                        bg='white', fg='black', font=('Courier', 9))
        self.process_output.pack(fill='both', expand=True)
    
    def setup_cpu_tab(self, parent):
        """Setup CPU Scheduler tab"""
        # Buttons frame
        btn_frame = tk.Frame(parent, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="▶️  Run Scheduler", command=self.run_scheduler,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="📊 View Gantt Chart", command=self.view_gantt,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Output frame
        output_frame = tk.LabelFrame(parent, text="Scheduling Log", font=('Segoe UI', 10, 'bold'),
                                    bg='#F0F0F0', fg='#333333')
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.cpu_output = scrolledtext.ScrolledText(output_frame, height=20, width=60,
                                                    bg='white', fg='black', font=('Courier', 9))
        self.cpu_output.pack(fill='both', expand=True)
    
    def setup_memory_tab(self, parent):
        """Setup Memory Management tab"""
        # Buttons frame
        btn_frame = tk.Frame(parent, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="💾 Allocate Memory", command=self.allocate_memory,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="🗂️  Show Memory Map", command=self.show_memory,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Output frame
        output_frame = tk.LabelFrame(parent, text="Memory Information", font=('Segoe UI', 10, 'bold'),
                                    bg='#F0F0F0', fg='#333333')
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.memory_output = scrolledtext.ScrolledText(output_frame, height=20, width=60,
                                                      bg='white', fg='black', font=('Courier', 9))
        self.memory_output.pack(fill='both', expand=True)
    
    def setup_file_tab(self, parent):
        """Setup File System tab"""
        # Buttons frame
        btn_frame = tk.Frame(parent, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="➕ Create File", command=self.create_file,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="🗑️  Delete File", command=self.delete_file,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="📂 List Files", command=self.list_files,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Output frame
        output_frame = tk.LabelFrame(parent, text="File System", font=('Segoe UI', 10, 'bold'),
                                    bg='#F0F0F0', fg='#333333')
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.file_output = scrolledtext.ScrolledText(output_frame, height=20, width=60,
                                                    bg='white', fg='black', font=('Courier', 9))
        self.file_output.pack(fill='both', expand=True)
    
    def setup_printer_tab(self, parent):
        """Setup Printer tab"""
        # Buttons frame
        btn_frame = tk.Frame(parent, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="➕ Add Print Job", command=self.add_print_job,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="🖨️  Process Jobs", command=self.process_jobs,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="📈 Queue Status", command=self.queue_status,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Output frame
        output_frame = tk.LabelFrame(parent, text="Printer Queue", font=('Segoe UI', 10, 'bold'),
                                    bg='#F0F0F0', fg='#333333')
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.printer_output = scrolledtext.ScrolledText(output_frame, height=20, width=60,
                                                       bg='white', fg='black', font=('Courier', 9))
        self.printer_output.pack(fill='both', expand=True)
    
    def setup_disk_tab(self, parent):
        """Setup Disk Scheduler tab"""
        # Buttons frame
        btn_frame = tk.Frame(parent, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(btn_frame, text="Add Disk Request:", font=('Segoe UI', 10, 'bold'), bg='#F0F0F0').pack(side='left', padx=5)
        tk.Button(btn_frame, text="➕ Add Request", command=self.add_disk_request,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        tk.Label(btn_frame, text="Scheduling Algorithm:", font=('Segoe UI', 10, 'bold'), bg='#F0F0F0').pack(side='left', padx=5)
        tk.Button(btn_frame, text="FCFS", command=self.fcfs_schedule,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="SCAN", command=self.scan_schedule,
                 font=('Segoe UI', 11, 'bold'), bg='#0078D4', fg='white', padx=15, pady=8,
                 activebackground='#005A9E', relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        # Output frame
        output_frame = tk.LabelFrame(parent, text="Disk Scheduling", font=('Segoe UI', 10, 'bold'),
                                    bg='#F0F0F0', fg='#333333')
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.disk_output = scrolledtext.ScrolledText(output_frame, height=20, width=60,
                                                    bg='white', fg='black', font=('Courier', 9))
        self.disk_output.pack(fill='both', expand=True)
    
    # Event handlers
    def display_animated_output(self, widget, text):
        """Display text with smooth animation using a thread"""
        widget.delete(1.0, tk.END)
        thread = threading.Thread(target=lambda: AnimationHelper.animate_text_insertion(widget, text, delay=5, char_delay=0), daemon=True)
        thread.start()
    
    def create_process(self):
        result = self.pm.create_process()
        full_output = result + "\n\n--- All Processes ---\n" + self.pm.get_process_table()
        self.display_animated_output(self.process_output, full_output)
    
    def show_processes(self):
        self.display_animated_output(self.process_output, self.pm.get_process_table())
    
    def run_scheduler(self):
        if not self.pm.processes:
            messagebox.showerror("Error", "No processes created. Create some processes first!")
            return
        
        # Reset process states for new scheduling
        for p in self.pm.processes:
            p.remaining = p.burst_time
            p.state = "READY"
        
        self.scheduler = CPUScheduler(self.pm.processes)
        log = self.scheduler.fcfs()
        self.display_animated_output(self.cpu_output, log)
    
    def view_gantt(self):
        if self.scheduler and self.scheduler.timeline:
            self.scheduler.draw_gantt()
        else:
            messagebox.showerror("Error", "Run the scheduler first to generate a Gantt chart!")
    
    def allocate_memory(self):
        if not self.pm.processes:
            messagebox.showerror("Error", "No processes created. Create some processes first!")
            return
        
        self.mm.log = []
        for p in self.pm.processes:
            self.mm.allocate(p)
        output = self.mm.get_log() + "\n\n" + self.mm.get_memory_map()
        self.display_animated_output(self.memory_output, output)
    
    def show_memory(self):
        self.display_animated_output(self.memory_output, self.mm.get_memory_map())
    
    def create_file(self):
        # Create a simple dialog window with enhanced styling
        dialog = tk.Toplevel(self.root)
        dialog.title("Create File")
        dialog.geometry("450x450")
        dialog.configure(bg='#F0F0F0')
        dialog.resizable(False, False)
        
        # Title
        title_label = tk.Label(dialog, text="Create New File", font=('Segoe UI', 12, 'bold'), 
                              bg='#F0F0F0', fg='#0078D4')
        title_label.pack(pady=10)
        
        # Divider
        divider = tk.Frame(dialog, height=1, bg='#D0D0D0')
        divider.pack(fill='x', padx=10)
        
        # Content frame - use fixed height instead of expand=True
        content_frame = tk.Frame(dialog, bg='#F0F0F0', height=300)
        content_frame.pack(fill='both', expand=False, padx=15, pady=10)
        
        tk.Label(content_frame, text="File Name:", font=('Segoe UI', 10, 'bold'), bg='#F0F0F0').pack(anchor='w', pady=(0, 5))
        fname_entry = tk.Entry(content_frame, font=('Segoe UI', 10), width=40, bd=1, relief='solid')
        fname_entry.pack(anchor='w', pady=(0, 10), ipady=5)
        fname_entry.focus()
        
        tk.Label(content_frame, text="Content:", font=('Segoe UI', 10, 'bold'), bg='#F0F0F0').pack(anchor='w', pady=(0, 5))
        fcontent = tk.Text(content_frame, font=('Segoe UI', 9), height=10, width=45, bd=1, relief='solid')
        fcontent.pack(fill='both', expand=True, pady=(0, 10))
        
        # Button frame - will be at bottom, always visible
        btn_frame = tk.Frame(dialog, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        def save_file():
            fname = fname_entry.get()
            content = fcontent.get(1.0, tk.END)
            if fname:
                result = self.fs.create_file(fname, content)
                messagebox.showinfo("✓ Success", result)
                dialog.destroy()
                self.display_animated_output(self.file_output, result)
            else:
                messagebox.showerror("Error", "File name cannot be empty!")
        
        tk.Button(btn_frame, text="✓ Create", command=save_file, font=('Segoe UI', 11, 'bold'),
                 bg='#107C10', fg='white', padx=20, pady=8, activebackground='#0E6F0B', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✕ Cancel", command=dialog.destroy, font=('Segoe UI', 11, 'bold'),
                 bg='#D13438', fg='white', padx=20, pady=8, activebackground='#A02830', relief='flat', cursor='hand2').pack(side='right', padx=5)
    
    def delete_file(self):
        if not self.fs.files:
            messagebox.showerror("Error", "No files to delete!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete File")
        dialog.geometry("400x200")
        dialog.configure(bg='#F0F0F0')
        dialog.resizable(False, False)
        
        # Title
        title_label = tk.Label(dialog, text="Delete File", font=('Segoe UI', 12, 'bold'), 
                              bg='#F0F0F0', fg='#D13438')
        title_label.pack(pady=15)
        
        # Divider
        divider = tk.Frame(dialog, height=1, bg='#D0D0D0')
        divider.pack(fill='x', padx=10)
        
        # Content frame
        content_frame = tk.Frame(dialog, bg='#F0F0F0')
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        tk.Label(content_frame, text="Select file to delete:", font=('Segoe UI', 10, 'bold'), bg='#F0F0F0').pack(pady=(0, 10))
        
        file_var = tk.StringVar()
        file_menu = ttk.Combobox(content_frame, textvariable=file_var, values=list(self.fs.files.keys()),
                                state='readonly', font=('Segoe UI', 10), width=35)
        file_menu.pack(fill='x', pady=(0, 20))
        
        # Button frame
        btn_frame = tk.Frame(dialog, bg='#F0F0F0')
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        def delete():
            fname = file_var.get()
            if fname:
                result = self.fs.delete_file(fname)
                messagebox.showinfo("✓ Success", result)
                dialog.destroy()
                self.display_animated_output(self.file_output, result)
        
        tk.Button(btn_frame, text="✓ Delete", command=delete, font=('Segoe UI', 11, 'bold'),
                 bg='#D13438', fg='white', padx=20, pady=8, activebackground='#A02830', relief='flat', cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✕ Cancel", command=dialog.destroy, font=('Segoe UI', 11, 'bold'),
                 bg='#808080', fg='white', padx=20, pady=8, activebackground='#696969', relief='flat', cursor='hand2').pack(side='right', padx=5)
    
    def list_files(self):
        self.display_animated_output(self.file_output, self.fs.list_files())
    
    def add_print_job(self):
        job_name = simpledialog.askstring("Add Print Job", "Enter print job name:")
        if job_name:
            result = self.printer.add_job(job_name)
            messagebox.showinfo("✓ Success", result)
            self.display_animated_output(self.printer_output, result)
    
    def process_jobs(self):
        result = self.printer.process()
        self.display_animated_output(self.printer_output, result)
    
    def queue_status(self):
        status = self.printer.get_queue_status()
        self.display_animated_output(self.printer_output, status)
    
    def add_disk_request(self):
        request = simpledialog.askstring("Add Disk Request", "Enter disk request (0-200):")
        if request:
            result = self.disk.add_request(request)
            messagebox.showinfo("✓ Success", result)
            self.display_animated_output(self.disk_output, result)
    
    def fcfs_schedule(self):
        result = self.disk.fcfs()
        self.display_animated_output(self.disk_output, result)
    
    def scan_schedule(self):
        result = self.disk.scan()
        self.display_animated_output(self.disk_output, result)

    def run_gui(self):
        """Run the GUI"""
        root = self.create_gui()
        root.mainloop()


# ===============================
# RUN
# ===============================

if __name__ == "__main__":

    os = OSSimulator()


    os.run_gui()
