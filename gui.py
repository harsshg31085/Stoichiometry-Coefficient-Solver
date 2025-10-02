import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from solver import solve_stoichiometry
import numpy as np

class ChemicalComponentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chemical Stoichiometry Manager")
        self.root.geometry("1100x750")
        self.root.configure(bg='#f0f0f0')
        
        self.reactants = []
        self.products = []
        self.total_reactant_mass = 0.0
        self.total_product_mass = 0.0
        self.reactions = []

        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
        self.setup_styles()
        self.setup_gui()
        
    def setup_styles(self):
        style = ttk.Style()
        
        style.configure('Primary.TFrame', background=self.colors['light'])
        style.configure('Secondary.TFrame', background=self.colors['primary'])
        style.configure('Accent.TButton', background=self.colors['accent'])
        
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['light'])
        
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       foreground=self.colors['secondary'],
                       background=self.colors['light'])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='black')
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'], 
                       foreground='black')
        
    def setup_gui(self):
        main_container = tk.Frame(self.root, bg=self.colors['light'], padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(main_container, bg=self.colors['primary'], padx=20, pady=15)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, 
                            text="CHEMICAL STOICHIOMETRY MANAGER",
                            font=('Arial', 20, 'bold'),
                            fg='white',
                            bg=self.colors['primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                text="Input Reactants and Products with Total Stream Mass Flow Rates",
                                font=('Arial', 12),
                                fg='#bdc3c7',
                                bg=self.colors['primary'])
        subtitle_label.pack(pady=(5, 0))
        
        content_frame = tk.Frame(main_container, bg=self.colors['light'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        main_paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        left_pane = ttk.Frame(main_paned, padding=10)
        main_paned.add(left_pane, weight=2)
        
        right_pane = ttk.Frame(main_paned, padding=10)
        main_paned.add(right_pane, weight=3)
                
        reactants_frame = ttk.LabelFrame(left_pane, text="📥 REACTANTS INPUT", padding=10)
        reactants_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_mass_frame = tk.Frame(reactants_frame, bg=self.colors['light'])
        total_mass_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(total_mass_frame, text="Total Reactant Mass Flow (kg/h):", 
                font=('Arial', 10, 'bold'),
                bg=self.colors['light']).pack(side=tk.LEFT)
        
        self.total_reactant_mass_entry = ttk.Entry(total_mass_frame, width=12, font=('Arial', 10))
        self.total_reactant_mass_entry.pack(side=tk.LEFT, padx=(10, 10))
        
        ttk.Button(total_mass_frame, text="Update", 
                command=self.update_reactant_total).pack(side=tk.LEFT)
        
        input_grid = tk.Frame(reactants_frame, bg=self.colors['light'])
        input_grid.pack(fill=tk.X, pady=5)
        
        headers = ["Name", "Mole Frac", "MW"]
        for i, header in enumerate(headers):
            tk.Label(input_grid, text=header, font=('Arial', 9, 'bold'),
                    bg=self.colors['light']).grid(row=0, column=i, padx=2, pady=2, sticky=tk.W)
        
        self.reactant_name = ttk.Entry(input_grid, width=12, font=('Arial', 9))
        self.reactant_name.grid(row=1, column=0, padx=2, pady=2)
        
        self.reactant_fraction = ttk.Entry(input_grid, width=8, font=('Arial', 9))
        self.reactant_fraction.grid(row=1, column=1, padx=2, pady=2)
        
        self.reactant_mw = ttk.Entry(input_grid, width=8, font=('Arial', 9))
        self.reactant_mw.grid(row=1, column=2, padx=2, pady=2)
        
        ttk.Button(input_grid, text="➕ Add", 
                command=self.add_reactant, style='Success.TButton').grid(row=1, column=3, padx=5)
        
        products_frame = ttk.LabelFrame(left_pane, text="📤 PRODUCTS OUTPUT", padding=10)
        products_frame.pack(fill=tk.X, pady=(0, 10))
        
        product_input_grid = tk.Frame(products_frame, bg=self.colors['light'])
        product_input_grid.pack(fill=tk.X, pady=5)
        
        for i, header in enumerate(headers):
            tk.Label(product_input_grid, text=header, font=('Arial', 9, 'bold'),
                    bg=self.colors['light']).grid(row=0, column=i, padx=2, pady=2, sticky=tk.W)
        
        self.product_name = ttk.Entry(product_input_grid, width=12, font=('Arial', 9))
        self.product_name.grid(row=1, column=0, padx=2, pady=2)
        
        self.product_fraction = ttk.Entry(product_input_grid, width=8, font=('Arial', 9))
        self.product_fraction.grid(row=1, column=1, padx=2, pady=2)
        
        self.product_mw = ttk.Entry(product_input_grid, width=8, font=('Arial', 9))
        self.product_mw.grid(row=1, column=2, padx=2, pady=2)
        
        ttk.Button(product_input_grid, text="➕ Add", 
                command=self.add_product, style='Success.TButton').grid(row=1, column=3, padx=5)
        
        reaction_frame = ttk.LabelFrame(left_pane, text="🔄 REACTION DEFINITIONS", padding=10)
        reaction_frame.pack(fill=tk.X, pady=(0, 10))
        
        reaction_input_grid = tk.Frame(reaction_frame, bg=self.colors['light'])
        reaction_input_grid.pack(fill=tk.X, pady=5)
        
        reaction_headers = ["Name", "Reactants", "Products"]
        for i, header in enumerate(reaction_headers):
            tk.Label(reaction_input_grid, text=header, font=('Arial', 9, 'bold'),
                    bg=self.colors['light']).grid(row=0, column=i, padx=2, pady=2, sticky=tk.W)
        
        self.reaction_name = ttk.Entry(reaction_input_grid, width=12, font=('Arial', 9))
        self.reaction_name.grid(row=1, column=0, padx=2, pady=2)
        
        self.reaction_reactants = ttk.Entry(reaction_input_grid, width=15, font=('Arial', 9))
        self.reaction_reactants.grid(row=1, column=1, padx=2, pady=2)
        
        self.reaction_products = ttk.Entry(reaction_input_grid, width=15, font=('Arial', 9))
        self.reaction_products.grid(row=1, column=2, padx=2, pady=2)
        
        ttk.Button(reaction_input_grid, text="➕ Add", 
                command=self.add_reaction, style='Success.TButton').grid(row=1, column=3, padx=5)
        
        reaction_table_frame = tk.Frame(reaction_frame, bg=self.colors['light'])
        reaction_table_frame.pack(fill=tk.X, pady=(5, 0))
        
        reaction_columns = ('Name', 'Reactants', 'Products')
        self.reactions_tree = ttk.Treeview(reaction_table_frame, columns=reaction_columns, show='headings', height=4)
        
        column_widths = [80, 120, 120]
        for col, width in zip(reaction_columns, column_widths):
            self.reactions_tree.heading(col, text=col)
            self.reactions_tree.column(col, width=width, minwidth=60)
        
        self.reactions_tree.pack(fill=tk.X)
        
        reaction_controls = tk.Frame(reaction_frame, bg=self.colors['light'], pady=5)
        reaction_controls.pack(fill=tk.X)
        
        ttk.Button(reaction_controls, text="🗑️ Remove", 
                command=self.remove_reaction).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(reaction_controls, text="🗑️ Clear All", 
                command=self.clear_reactions).pack(side=tk.LEFT)
        
        right_paned = ttk.PanedWindow(right_pane, orient=tk.VERTICAL)
        right_paned.pack(fill=tk.BOTH, expand=True)
        
        preview_pane = ttk.Frame(right_paned, padding=5)
        right_paned.add(preview_pane, weight=1)
        self.create_preview_section(preview_pane)
        
        solver_pane = ttk.Frame(right_paned, padding=5)
        right_paned.add(solver_pane, weight=1)
        self.create_stoichiometry_section(solver_pane)
        
        control_frame = tk.Frame(main_container, bg=self.colors['light'], pady=20)
        control_frame.pack(fill=tk.X)
        
        buttons = [
            ("💾 Save to JSON", self.save_to_json, self.colors['accent']),
            ("📂 Load from JSON", self.load_from_json, self.colors['secondary']),
            ("🧮 Calculate All", self.calculate_all_flows, self.colors['success']),
            ("🗑️ Clear All", self.clear_all, self.colors['warning'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(control_frame, text=text, command=command,
                        bg=color, fg='white', font=('Arial', 10, 'bold'),
                        padx=15, pady=8, relief=tk.RAISED, bd=2)
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#34495e'))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))
        
        status_frame = tk.Frame(main_container, bg=self.colors['dark'], height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="🚀 Ready to input chemical components")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                            bg=self.colors['dark'], fg='white',
                            font=('Arial', 9))
        status_label.pack(side=tk.LEFT, padx=10)
        
        self.counter_var = tk.StringVar(value="Reactants: 0 | Products: 0 | Reactions: 0")
        counter_label = tk.Label(status_frame, textvariable=self.counter_var,
                            bg=self.colors['dark'], fg='#bdc3c7',
                            font=('Arial', 9))
        counter_label.pack(side=tk.RIGHT, padx=10)
        
    def create_reactants_section(self, parent):
        reactants_frame = ttk.LabelFrame(parent, text="📥 REACTANTS INPUT", padding=15)
        reactants_frame.pack(fill=tk.X, pady=(0, 15))
        
        total_mass_frame = tk.Frame(reactants_frame, bg=self.colors['light'])
        total_mass_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(total_mass_frame, text="Total Reactant Mass Flow (kg/h):", 
                font=('Arial', 11, 'bold'),
                bg=self.colors['light']).pack(side=tk.LEFT)
        
        self.total_reactant_mass_entry = ttk.Entry(total_mass_frame, width=15, font=('Arial', 11))
        self.total_reactant_mass_entry.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Button(total_mass_frame, text="Update Total", 
                  command=self.update_reactant_total).pack(side=tk.LEFT)
        
        input_grid = tk.Frame(reactants_frame, bg=self.colors['light'])
        input_grid.pack(fill=tk.X, pady=(10, 0))
        
        headers = ["Component Name", "Mole Fraction", "Molar Weight (kg/mol)"]
        for i, header in enumerate(headers):
            tk.Label(input_grid, text=header, font=('Arial', 10, 'bold'),
                    bg=self.colors['light']).grid(row=0, column=i, padx=5, pady=5, sticky=tk.W)
        
        self.reactant_name = ttk.Entry(input_grid, width=20, font=('Arial', 10))
        self.reactant_name.grid(row=1, column=0, padx=5, pady=5)
        
        self.reactant_fraction = ttk.Entry(input_grid, width=15, font=('Arial', 10))
        self.reactant_fraction.grid(row=1, column=1, padx=5, pady=5)
        
        self.reactant_mw = ttk.Entry(input_grid, width=15, font=('Arial', 10))
        self.reactant_mw.grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(input_grid, text="➕ Add Reactant", 
                  command=self.add_reactant, style='Success.TButton').grid(row=1, column=3, padx=10)
        
    def create_products_section(self, parent):
        products_frame = ttk.LabelFrame(parent, text="📤 PRODUCTS OUTPUT", padding=10)
        products_frame.pack(fill=tk.X, pady=(0, 10))
        
        balance_frame = tk.Frame(products_frame, bg=self.colors['light'])
        balance_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(balance_frame, text="⚖️ Calculate Flows from Mass Balance", 
                command=self.calculate_product_flows_from_mass_balance,
                style='Success.TButton').pack(side=tk.LEFT)
        
        input_grid = tk.Frame(products_frame, bg=self.colors['light'])
        input_grid.pack(fill=tk.X, pady=5)
        
        headers = ["Name", "Mole Frac", "MW"]
        for i, header in enumerate(headers):
            tk.Label(input_grid, text=header, font=('Arial', 9, 'bold'),
                    bg=self.colors['light']).grid(row=0, column=i, padx=2, pady=2, sticky=tk.W)
        
        self.product_name = ttk.Entry(input_grid, width=12, font=('Arial', 9))
        self.product_name.grid(row=1, column=0, padx=2, pady=2)
        
        self.product_fraction = ttk.Entry(input_grid, width=8, font=('Arial', 9))
        self.product_fraction.grid(row=1, column=1, padx=2, pady=2)
        
        self.product_mw = ttk.Entry(input_grid, width=8, font=('Arial', 9))
        self.product_mw.grid(row=1, column=2, padx=2, pady=2)
        
        ttk.Button(input_grid, text="➕ Add", 
                command=self.add_product, style='Success.TButton').grid(row=1, column=3, padx=5)

    def create_reaction_input_section(self, parent):
        reaction_frame = ttk.LabelFrame(parent, text="🔄 REACTION DEFINITIONS", padding=15)
        reaction_frame.pack(fill=tk.X, pady=(0, 15))

        input_grid = tk.Frame(reaction_frame, bg=self.colors['light'])
        input_grid.pack(fill=tk.X, pady=10)

        headers = ["Reaction Name", "Reactants (comma-separated)", "Products (comma-separated)"]
        for i, header in enumerate(headers):
            tk.Label(input_grid, text=header, font=('Arial', 10, 'bold'),
                    bg=self.colors['light']).grid(row=0, column=i, padx=5, pady=5, sticky=tk.W)

        self.reaction_name = ttk.Entry(input_grid, width=20, font=('Arial', 10))
        self.reaction_name.grid(row=1, column=0, padx=5, pady=5)

        self.reaction_reactants = ttk.Entry(input_grid, width=30, font=('Arial', 10))
        self.reaction_reactants.grid(row=1, column=1, padx=5, pady=5)

        self.reaction_products = ttk.Entry(input_grid, width=30, font=('Arial', 10))
        self.reaction_products.grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(input_grid, text="➕ Add Reaction", 
                command=self.add_reaction, style='Success.TButton').grid(row=1, column=3, padx=10)

        table_frame = tk.Frame(reaction_frame, bg=self.colors['light'])
        table_frame.pack(fill=tk.X, pady=(10, 0))

        columns = ('Name', 'Reactants', 'Products')
        self.reactions_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=4)

        for col in columns:
            self.reactions_tree.heading(col, text=col)
            self.reactions_tree.column(col, width=150)

        self.reactions_tree.pack(fill=tk.X)

        controls_frame = tk.Frame(reaction_frame, bg=self.colors['light'])
        controls_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(controls_frame, text="🗑️ Remove Selected", 
                command=self.remove_reaction).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="🗑️ Clear All Reactions", 
                command=self.clear_reactions).pack(side=tk.LEFT)
        

    def create_preview_section(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="📊 DATA PREVIEW", padding=8)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        reactants_tab = ttk.Frame(self.notebook, padding=5)
        self.reactants_tab_id = self.notebook.add(reactants_tab, text=f"Reactants ({len(self.reactants)})")
        
        reactants_columns = ('Name', 'Mole Frac', 'MW', 'Mass Flow', 'Molar Flow')
        self.reactants_tree = ttk.Treeview(reactants_tab, columns=reactants_columns, 
                                        show='headings', height=6)
        
        column_widths = [80, 70, 60, 80, 90] 
        for col, width in zip(reactants_columns, column_widths):
            self.reactants_tree.heading(col, text=col)
            self.reactants_tree.column(col, width=width, minwidth=50)
        
        self.reactants_tree.pack(fill=tk.BOTH, expand=True)

        products_tab = ttk.Frame(self.notebook, padding=5)
        self.products_tab_id = self.notebook.add(products_tab, text=f"Products ({len(self.products)})")
        
        self.products_tree = ttk.Treeview(products_tab, columns=reactants_columns, 
                                        show='headings', height=6)
        
        for col, width in zip(reactants_columns, column_widths):
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=width, minwidth=50)
        
        self.products_tree.pack(fill=tk.BOTH, expand=True)

        table_controls = tk.Frame(preview_frame, bg=self.colors['light'], pady=5)
        table_controls.pack(fill=tk.X)
        
        ttk.Button(table_controls, text="🗑️ Remove Reactant", 
                command=self.remove_reactant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(table_controls, text="🗑️ Remove Product", 
                command=self.remove_product).pack(side=tk.LEFT)
        
    def create_control_buttons(self, parent):
        control_frame = tk.Frame(parent, bg=self.colors['light'], pady=20)
        control_frame.pack(fill=tk.X)
        
        buttons = [
            ("💾 Save to JSON", self.save_to_json, self.colors['accent']),
            ("📂 Load from JSON", self.load_from_json, self.colors['secondary']),
            ("🧮 Calculate All", self.calculate_all_flows, self.colors['success']),
            ("🗑️ Clear All", self.clear_all, self.colors['warning'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(control_frame, text=text, command=command,
                          bg=color, fg='white', font=('Arial', 10, 'bold'),
                          padx=15, pady=8, relief=tk.RAISED, bd=2)
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#34495e'))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))
        
    def create_status_bar(self, parent):
        status_frame = tk.Frame(parent, bg=self.colors['dark'], height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="🚀 Ready to input chemical components")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                              bg=self.colors['dark'], fg='white',
                              font=('Arial', 9))
        status_label.pack(side=tk.LEFT, padx=10)
        
        self.counter_var = tk.StringVar(value="Reactants: 0 | Products: 0")
        counter_label = tk.Label(status_frame, textvariable=self.counter_var,
                               bg=self.colors['dark'], fg='#bdc3c7',
                               font=('Arial', 9))
        counter_label.pack(side=tk.RIGHT, padx=10)
    
    def validate_number(self, value, field_name, allow_negative=False, allow_zero=True):
        try:
            num = float(value)
            if not allow_negative and num < 0:
                raise ValueError(f"{field_name} cannot be negative")
            if not allow_zero and num == 0:
                raise ValueError(f"{field_name} cannot be zero")
            return True, num
        except ValueError as e:
            return False, f"Invalid {field_name}: {str(e)}"
    
    def calculate_component_mass_flow(self, mole_fraction, molar_weight, total_mass):
        if molar_weight <= 0:
            return 0
        return total_mass * mole_fraction
    
    def calculate_molar_flow(self, mass_flow, molar_weight):
        if molar_weight <= 0:
            return 0
        return mass_flow / molar_weight
    
    def update_reactant_total(self):
        mass_str = self.total_reactant_mass_entry.get().strip()
        valid, mass = self.validate_number(mass_str, "Total reactant mass flow", allow_negative=False)
        if valid:
            self.total_reactant_mass = mass
            self.status_var.set(f"✅ Total reactant mass flow updated to {mass} kg/h")
            self.calculate_all_flows()
        else:
            messagebox.showerror("Error", mass)
    
    def add_reactant(self):
        name = self.reactant_name.get().strip()
        fraction_str = self.reactant_fraction.get().strip()
        mw_str = self.reactant_mw.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Component name is required")
            return
        
        valid_fraction, fraction = self.validate_number(fraction_str, "Mole fraction")
        if not valid_fraction:
            messagebox.showerror("Error", fraction)
            return
            
        valid_mw, mw = self.validate_number(mw_str, "Molar weight", allow_zero=False)
        if not valid_mw:
            messagebox.showerror("Error", mw)
            return
        
        if not (0 <= fraction <= 1):
            messagebox.showerror("Error", "Mole fraction must be between 0 and 1")
            return
        
        mass_flow = self.calculate_component_mass_flow(fraction, mw, self.total_reactant_mass)
        molar_flow = self.calculate_molar_flow(mass_flow, mw)
        
        reactant_data = {
            'name': name,
            'mole_fraction': fraction,
            'molar_weight': mw,
            'mass_flow': mass_flow,
            'molar_flow': molar_flow
        }
        self.reactants.append(reactant_data)
        
        self.reactants_tree.insert('', tk.END, values=(
            name, f"{fraction:.4f}", f"{mw:.4f}", f"{mass_flow:.4f}", f"{molar_flow:.6f}"
        ))
        
        self.reactant_name.delete(0, tk.END)
        self.reactant_fraction.delete(0, tk.END)
        self.reactant_mw.delete(0, tk.END)
        
        self.status_var.set(f"✅ Added reactant: {name}")
        self.update_counters()

    def add_product(self):
        name = self.product_name.get().strip()
        fraction_str = self.product_fraction.get().strip()
        mw_str = self.product_mw.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Component name is required")
            return
        
        valid_fraction, fraction = self.validate_number(fraction_str, "Mole fraction")
        if not valid_fraction:
            messagebox.showerror("Error", fraction)
            return
            
        valid_mw, mw = self.validate_number(mw_str, "Molar weight", allow_zero=False)
        if not valid_mw:
            messagebox.showerror("Error", mw)
            return
        
        if not (0 <= fraction <= 1):
            messagebox.showerror("Error", "Mole fraction must be between 0 and 1")
            return
        
        product_data = {
            'name': name,
            'mole_fraction': fraction,
            'molar_weight': mw,
            'mass_flow': 0.0, 
            'molar_flow': 0.0  
        }
        self.products.append(product_data)
        
        self.products_tree.insert('', tk.END, values=(
            name, f"{fraction:.4f}", f"{mw:.4f}", "TBD", "TBD"
        ))
        
        self.product_name.delete(0, tk.END)
        self.product_fraction.delete(0, tk.END)
        self.product_mw.delete(0, tk.END)
        
        self.status_var.set(f"✅ Added product: {name} (flows will be calculated)")
        self.update_counters()
        
        if self.total_reactant_mass > 0:
            self.calculate_product_flows_from_mass_balance() 

    def remove_reactant(self):
        selected = self.reactants_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a reactant to remove")
            return
            
        for item in selected:
            index = self.reactants_tree.index(item)
            removed_name = self.reactants[index]['name']
            self.reactants.pop(index)
            self.reactants_tree.delete(item)
            self.status_var.set(f"🗑️ Removed reactant: {removed_name}")
        
        self.update_counters()
    
    def remove_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to remove")
            return
            
        for item in selected:
            index = self.products_tree.index(item)
            removed_name = self.products[index]['name']
            self.products.pop(index)
            self.products_tree.delete(item)
            self.status_var.set(f"🗑️ Removed product: {removed_name}")
        
        self.update_counters()
    
    def calculate_all_flows(self):
        for item in self.reactants_tree.get_children():
            self.reactants_tree.delete(item)
        
        for reactant in self.reactants:
            mass_flow = self.calculate_component_mass_flow(
                reactant['mole_fraction'], 
                reactant['molar_weight'],
                self.total_reactant_mass
            )
            molar_flow = self.calculate_molar_flow(mass_flow, reactant['molar_weight'])
            
            reactant['mass_flow'] = mass_flow
            reactant['molar_flow'] = molar_flow
            
            self.reactants_tree.insert('', tk.END, values=(
                reactant['name'],
                f"{reactant['mole_fraction']:.4f}",
                f"{reactant['molar_weight']:.4f}",
                f"{mass_flow:.4f}",
                f"{molar_flow:.6f}"
            ))
        
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for product in self.products:
            self.products_tree.insert('', tk.END, values=(
                product['name'],
                f"{product['mole_fraction']:.4f}",
                f"{product['molar_weight']:.4f}",
                "TBD",  
                "TBD"   
            ))
        
        self.status_var.set("🔄 Reactant flows recalculated | Product flows: TBD (from stoichiometry)")
        self.update_counters()
    
    def update_counters(self):
        reaction_count = len(self.reactions) if hasattr(self, 'reactions') else 0
        self.counter_var.set(f"Reactants: {len(self.reactants)} | Products: {len(self.products)} | Reactions: {reaction_count}")
        self.update_tab_labels()
    
    def clear_all(self, message_box = True):
        if message_box:
            if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all data?"):
                self.reactants.clear()
                self.products.clear()
                self.total_reactant_mass = 0.0
                self.total_reactant_mass_entry.delete(0, tk.END)
                
                for item in self.reactants_tree.get_children():
                    self.reactants_tree.delete(item)
                for item in self.products_tree.get_children():
                    self.products_tree.delete(item)
                
                self.status_var.set("🗑️ All data cleared")
                self.update_counters()
        else:
            self.reactants.clear()
            self.products.clear()
            self.total_reactant_mass = 0.0
            self.total_reactant_mass_entry.delete(0, tk.END)
                
            for item in self.reactants_tree.get_children():
                self.reactants_tree.delete(item)
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
                
            self.status_var.set("🗑️ All data cleared")
            self.update_counters()
    
    def save_to_json(self):
        if not self.reactants and not self.products:
            messagebox.showwarning("Warning", "No data to save")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Chemical Data"
        )
        
        if filename:
            try:
                data = {
                    'total_reactant_mass': self.total_reactant_mass,
                    'reactants': self.reactants,
                    'products': self.products,
                    'reactions': self.reactions
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                
                self.status_var.set(f"💾 Data saved to {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Data successfully saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def load_from_json(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Chemical Data"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.clear_all(message_box=False)
                
                if 'total_reactant_mass' in data:
                    self.total_reactant_mass = data['total_reactant_mass']
                    self.total_reactant_mass_entry.delete(0, tk.END)
                    self.total_reactant_mass_entry.insert(0, str(self.total_reactant_mass))
                
                if 'reactants' in data:
                    for reactant in data['reactants']:
                        self.reactants.append(reactant)
                
                if 'products' in data:
                    for product in data['products']:
                        self.products.append(product)
                
                if 'reactions' in data:
                    self.reactions = data['reactions']
                    for item in self.reactions_tree.get_children():
                        self.reactions_tree.delete(item)
                    for reaction in self.reactions:
                        self.reactions_tree.insert('', tk.END, values=(
                            reaction['name'],
                            ', '.join(reaction['reactants']),
                            ', '.join(reaction['products'])
                        ))
                
                if self.total_reactant_mass > 0 and self.products:
                    self.calculate_product_flows_from_mass_balance()
                else:
                    self.calculate_all_flows()
                
                self.status_var.set(f"📂 Data loaded from {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Data successfully loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def create_stoichiometry_section(self, parent):
        stoich_frame = ttk.LabelFrame(parent, text="🧪 STOICHIOMETRY SOLVER", padding=8)
        stoich_frame.pack(fill=tk.BOTH, expand=True)
        
        solve_button = tk.Button(stoich_frame, text="🚀 SOLVE STOICHIOMETRY", 
                            command=self.solve_stoichiometry,
                            bg='#e67e22', fg='white', font=('Arial', 11, 'bold'),
                            padx=15, pady=10, relief=tk.RAISED, bd=2)
        solve_button.pack(pady=8)
        solve_button.bind("<Enter>", lambda e: solve_button.configure(bg='#d35400'))
        solve_button.bind("<Leave>", lambda e: solve_button.configure(bg='#e67e22'))
        
        results_frame = tk.Frame(stoich_frame, bg=self.colors['light'])
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        text_frame = tk.Frame(results_frame, bg=self.colors['light'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, height=10, font=('Consolas', 8),
                                wrap=tk.WORD, bg='#f8f9fa', relief=tk.SUNKEN, bd=1)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=text_scrollbar.set)
        
        results_controls = tk.Frame(stoich_frame, bg=self.colors['light'], pady=5)
        results_controls.pack(fill=tk.X)
        
        ttk.Button(results_controls, text="📋 Copy Results", 
                command=self.copy_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(results_controls, text="💾 Save Results", 
                command=self.save_results).pack(side=tk.LEFT)

        self.results_text.insert(tk.END, 
            "👉 To solve stoichiometry:\n"
            "1. Add reactants & products\n"
            "2. Set total mass flow\n" 
            "3. Define reactions\n"
            "4. Click SOLVE above\n"
        )

    def add_reaction(self):
        reactants_str = self.reactants_input.get().strip()
        products_str = self.products_input.get().strip()
        
        if not reactants_str or not products_str:
            messagebox.showerror("Error", "Both reactants and products are required")
            return
        
        reactants = [r.strip() for r in reactants_str.split(',')]
        products = [p.strip() for p in products_str.split(',')]
        
        reaction_str = f"{' + '.join(reactants)} → {' + '.join(products)}"
        self.reactions_listbox.insert(tk.END, reaction_str)

        reaction_data = {
            'reactants': reactants,
            'products': products
        }
        if not hasattr(self, 'reactions'):
            self.reactions = []
        self.reactions.append(reaction_data)

        self.reactants_input.delete(0, tk.END)
        self.products_input.delete(0, tk.END)
        
        self.status_var.set(f"✅ Added reaction: {reaction_str}")

    def remove_reaction(self):
        selected = self.reactions_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a reaction to remove")
            return
        
        for index in selected[::-1]:  
            removed_reaction = self.reactions_listbox.get(index)
            self.reactions_listbox.delete(index)
            if hasattr(self, 'reactions'):
                self.reactions.pop(index)
            self.status_var.set(f"🗑️ Removed reaction: {removed_reaction}")

    def clear_reactions(self):
        if hasattr(self, 'reactions'):
            if messagebox.askyesno("Confirm", "Clear all reactions?"):
                self.reactions_listbox.delete(0, tk.END)
                self.reactions.clear()
                self.status_var.set("🗑️ All reactions cleared")

    def solve_stoichiometry(self):
        if not hasattr(self, 'reactions') or not self.reactions:
            messagebox.showerror("Error", "No reactions defined. Please add reactions first.")
            return
        
        if not self.reactants:
            messagebox.showerror("Error", "No reactants defined.")
            return
        
        if not self.products:
            messagebox.showerror("Error", "No products defined.")
            return
        
        if self.total_reactant_mass <= 0:
            messagebox.showerror("Error", "Total reactant mass flow must be greater than 0")
            return
        
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "🔄 Solving stoichiometry...\nPlease wait...")
            self.results_text.update()
                
            self.calculate_all_flows()
                
            result = solve_stoichiometry(self.reactants, self.products, self.reactions)
                
            self.display_stoichiometry_results(result)

            self.status_var.set("✅ Stoichiometry solved successfully!")
            
        except Exception as e:
            print(e)
            error_msg = f"❌ Error solving stoichiometry: {str(e)}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, error_msg)
            self.status_var.set("❌ Stoichiometry solving failed")

    def display_stoichiometry_results(self, result: dict):
        self.results_text.delete(1.0, tk.END)
        
        text = "=" * 60 + "\n"
        text += "STOICHIOMETRY SOLUTION RESULTS\n"
        text += "=" * 60 + "\n\n"
        
        if not result.get('success', False):
            error_msg = result.get('error', 'Unknown error occurred')
            text += f"❌ SOLUTION FAILED\n"
            text += f"Error: {error_msg}\n\n"
            text += "Troubleshooting tips:\n"
            text += "1. Check that all component names in reactions match your defined components\n"
            text += "2. Verify molar weights are positive numbers\n"
            text += "3. Ensure you have both reactants and products defined\n"
            text += "4. Check that reactions have at least one reactant and one product\n"
            text += "5. Verify total reactant mass flow is set and greater than 0\n"
            self.results_text.insert(tk.END, text)
            return

        text += "STOICHIOMETRIC COEFFICIENTS:\n"
        text += "-" * 40 + "\n"
        
        nu_matrix = np.array(result['stoichiometric_coefficients'])
        component_names = result['component_names']
        
        for r_idx in range(nu_matrix.shape[1]):
            text += f"Reaction {r_idx + 1}:\n"
            reactants = []
            products = []
            
            for c_idx in range(nu_matrix.shape[0]):
                coeff = nu_matrix[c_idx, r_idx]
                if abs(coeff) > 1e-6:  
                    name = component_names[c_idx]
                    if coeff < 0:
                        reactants.append(f"{-coeff:.5f} {name}")
                    else:
                        products.append(f"{coeff:.5f} {name}")
            
            if reactants and products:
                text += f"  {' + '.join(reactants)} -> {' + '.join(products)}\n"
            else:
                text += "  (No significant coefficients found)\n"
        
        self.results_text.insert(tk.END, text)

    def update_product_flows_from_stoichiometry(self, result: dict):
        product_mass_flows = result.get('product_mass_flows', {})
        
        for product in self.products:
            name = product['name']
            if name in product_mass_flows:
                product['mass_flow'] = product_mass_flows[name]
                if product['molar_weight'] > 0:
                    product['molar_flow'] = product_mass_flows[name] / product['molar_weight']
        
        self.calculate_all_flows()

    def copy_results(self):
        results_text = self.results_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(results_text)
        self.status_var.set("📋 Results copied to clipboard")


    def save_results(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Stoichiometry Results"
        )
        
        if filename:
            try:
                results_text = self.results_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(results_text)
                self.status_var.set(f"💾 Results saved to {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def add_reaction(self):
        name = self.reaction_name.get().strip()
        reactants_str = self.reaction_reactants.get().strip()
        products_str = self.reaction_products.get().strip()

        if not name:
            messagebox.showerror("Error", "Reaction name is required")
            return

        if not reactants_str or not products_str:
            messagebox.showerror("Error", "Both reactants and products are required")
            return

        reactants = [r.strip() for r in reactants_str.split(',')]
        products = [p.strip() for p in products_str.split(',')]

        all_components = [comp['name'] for comp in self.reactants + self.products]
        missing_components = []
        
        for comp in reactants + products:
            if comp not in all_components:
                missing_components.append(comp)
        
        if missing_components:
            messagebox.showerror("Error", f"Components not defined: {', '.join(missing_components)}")
            return

        reaction_data = {
            'name': name,
            'reactants': reactants,
            'products': products
        }
        self.reactions.append(reaction_data)

        self.reactions_tree.insert('', tk.END, values=(
            name,
            ', '.join(reactants),
            ', '.join(products)
        ))

        self.reaction_name.delete(0, tk.END)
        self.reaction_reactants.delete(0, tk.END)
        self.reaction_products.delete(0, tk.END)

        self.status_var.set(f"✅ Added reaction: {name}")

    def remove_reaction(self):
        selected = self.reactions_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a reaction to remove")
            return

        for item in selected:
            index = self.reactions_tree.index(item)
            removed_name = self.reactions[index]['name']
            self.reactions.pop(index)
            self.reactions_tree.delete(item)
            self.status_var.set(f"🗑️ Removed reaction: {removed_name}")

    def clear_reactions(self):
        if not self.reactions:
            return

        if messagebox.askyesno("Confirm", "Clear all reactions?"):
            self.reactions.clear()
            for item in self.reactions_tree.get_children():
                self.reactions_tree.delete(item)
            self.status_var.set("🗑️ All reactions cleared")

    def update_tab_labels(self):
        if hasattr(self, 'notebook'):
            tabs = self.notebook.tabs()
            if len(tabs) > 0:
                self.notebook.tab(tabs[0], text=f"Reactants ({len(self.reactants)})")
            
            if len(tabs) > 1:
                self.notebook.tab(tabs[1], text=f"Products ({len(self.products)})")
    
    def calculate_product_flows_from_mass_balance(self):
        if self.total_reactant_mass <= 0:
            messagebox.showerror("Error", "Please set total reactant mass flow first")
            return
        
        if not self.products:
            messagebox.showerror("Error", "No products defined")
            return
        
        total_mole_fraction = sum(product['mole_fraction'] for product in self.products)
        if abs(total_mole_fraction - 1.0) > 0.01:
            messagebox.showwarning("Warning", 
                                f"Product mole fractions sum to {total_mole_fraction:.3f} (should be 1.0)")
        
        total_mass_flow = self.total_reactant_mass

        avg_molar_weight = 0
        for product in self.products:
            mole_frac = product['mole_fraction']
            molar_weight = product['molar_weight']
            avg_molar_weight += mole_frac * molar_weight

        total_molar_flow = total_mass_flow / avg_molar_weight

        total_calculated_mass = 0
        for product in self.products:
            mole_frac = product['mole_fraction']
            molar_weight = product['molar_weight']
            
            molar_flow = total_molar_flow * mole_frac
            
            mass_flow = molar_flow * molar_weight
            
            product['molar_flow'] = molar_flow
            product['mass_flow'] = mass_flow
            
            total_calculated_mass += mass_flow

        self.calculate_all_flows()

        mass_balance_error = abs(total_mass_flow - total_calculated_mass)
        self.status_var.set(f"✅ Product flows updated! Mass balance error: {mass_balance_error:.2f} kg/h")

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, 
            f"📊 CORRECTED PRODUCT FLOWS:\n"
            f"{'='*50}\n"
            f"Total reactant mass: {total_mass_flow:.2f} kg/h\n"
            f"Average product MW: {avg_molar_weight:.2f} kg/kmol\n"
            f"Total product molar flow: {total_molar_flow:.2f} kmol/h\n"
            f"Total product mass: {total_calculated_mass:.2f} kg/h\n"
            f"Mass balance error: {mass_balance_error:.2f} kg/h\n\n"
            f"{'Product':<10} {'Mole Frac':<10} {'Molar Flow':<12} {'Mass Flow':<12}\n"
            f"{'-'*50}\n"
        )
        
        for product in self.products:
            self.results_text.insert(tk.END,
                f"{product['name']:<10} {product['mole_fraction']:<10.4f} "
                f"{product['molar_flow']:<12.2f} {product['mass_flow']:<12.2f}\n"
            )

def main():
    root = tk.Tk()
    app = ChemicalComponentGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()