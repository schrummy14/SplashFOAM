# Typically, standard library imports come first, followed by third-party libraries, and then local imports.
import os
import re
import signal
import time
import shutil # For file copying
import threading # Import threading for running simulation in a separate thread
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk
import subprocess
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from tkinter import Listbox
from collections import defaultdict # Import defaultdict | for mesh parameters 

# Importing local classes
from SearchWidget import SearchWidget  # Import the SearchWidget class from the other file
from ReplaceProperties import ReplacePropertiesPopup

#______________
#
# TERMINAL APP 
#______________           

class TerminalApp:  
    def __init__(self, root):
        self.root = root
        self.root.config(background="white") # black
        self.root.title("Splash - OpenFOAM")
        
        # Display a welcome message
        self.show_welcome_message()
        
        #  Source OpenFOAM Libraries
        #self.source_openfoam_libraries()
        
        # Add logos
        self.add_logos()
  
        # Add a background image
        #self.add_bgImage()
        
        #________________Sliding images_________________
        self.current_image_index = 0
        #self.image_paths = ["Resources/Images/racing-car.jpg", "Resources/Images/airplaneEngine.jpg", "Resources/Images/ship5.jpg", "Images/bubbles.jpg"]
        self.image_paths = ["Resources/Images/airplaneEngine.jpg", "Resources/Images/racing-car.jpg", "Resources/Images/bubbles.jpg"]
        self.time_delay = 2500  # Setting the time delay in milliseconds
        self.add_bgImage()
        self.start_slideshow()
        #________________Sliding images_________________
        
        # A dictionary to define a help message for each mesh parameter 
        self.PARAMETER_HELP = {
        "minCellSize": "minCellSize:\nSpecify the minimum cell size [in meters]. As a first guess you might take divide the size of the smallest element in your geometry divided by 2!",
        "maxCellSize": "maxCellSize:\nSpecify the maximum cell size [in meters]. As a first guess you might take divide the size of the smallest element in your geometry!",
        "boundaryCellSize": "boundaryCellSize:\nSpecify the cell size near boundaries. As a first guess you might take divide the size of the smallest element in your geometry divided by 5!"}
        

        # Create a button to import a geometry
        style = ttk.Style()
        style.configure("TButton", padding=20, relief="flat", background="lightblue", foreground="black", font=(12))  
        #style.configure("TButton", padding=10, relief="flat", background="cyan", foreground="black") 
        #style.configure("TButton", padding=10, relief="solid", background="#ffffe0", foreground="black")
        #style.configure("TButton", width=15, height=10, relief="solid", background="#ffffe0", foreground="black") # thinner buttons 
        self.import_button = ttk.Button(self.root, text="Import Geometry", command=self.import_geometry)
        self.import_button.grid(row=0, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.import_button, "Click to import the geometry to be simulated")        
        
        # Create a button to open a directory dialog
        self.browse_button = ttk.Button(self.root, text="Physical Properties", command=self.browse_directory)
        self.browse_button.grid(row=1, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.browse_button, "Click to change the physical properties of your fluid")
        self.geometry_loaded = False
        
        # Create a mesh type variable
        self.mesh_type_var = tk.StringVar(value="Cartesian")
        
        # Create a button to create the mesh
        self.create_mesh_button = ttk.Button(self.root, text="Create Mesh", command=self.create_mesh)
        self.create_mesh_button.grid(row=2, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.create_mesh_button, "Click to start building your mesh")
        
        # Create a button to initialize the case directory
        self.initialize_case_button = ttk.Button(self.root, text="Initialize Case", command=self.initialize_case)
        self.initialize_case_button.grid(row=3, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.initialize_case_button, "Click to choose the running directory of your case")
        
        # Create a button to run simulation
        self.run_simulation_button = ttk.Button(self.root, text="Run Simulation", command=self.run_simulation)
        self.run_simulation_button.grid(row=4, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.run_simulation_button, "Click to start your simulation")
        
        # Stop Simulation Button
        self.stop_simulation_button = ttk.Button(self.root, text="Stop Simulation", command=self.stop_simulation)
        self.stop_simulation_button.grid(row=5, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.stop_simulation_button, "Click to terminate your simulation")
        #self.stop_simulation_button["state"] = tk.DISABLED  # Initially disable the button
        
        # Create a button to plot results using xmgrace
        self.plot_results_xmgrace_button = ttk.Button(self.root, text="Plot Results", command=self.plot_results_xmgrace)
        self.plot_results_xmgrace_button.grid(row=6, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.plot_results_xmgrace_button, "Click to plot simulation results using xmgrace")

         # Create a button to execute the command
        self.execute_button = ttk.Button(self.root, text="Execute Command", command=self.execute_command)
        self.execute_button.grid(row=7, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.execute_button, "Click to run a terminal command")

        # Create an entry field for entering the command with a default sentence
        default_sentence =  "top" # Or "htop"
        self.entry = ttk.Entry(self.root, width=10)
        self.entry.grid(row=8, column=2, pady=1, padx=10, sticky="ew")
        self.entry.insert(0, default_sentence) 
        self.entry.configure(foreground="green", background="black")


        # Create a button to stop the command execution
        self.stop_button = ttk.Button(self.root, text="Stop Command", command=self.stop_command, state=tk.DISABLED)
        self.stop_button.grid(row=8, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.stop_button, "Click to stop terminal command")

        # Create a ttk.Style to configure the progress bar
        self.style = ttk.Style()
        self.style.configure("Custom.Horizontal.TProgressbar", thickness=20, troughcolor="lightgray", background="lightblue")
        
        # Test button [10-12 taken!]
        self.magic_box_button = ttk.Button(self.root, text="Magic box!", command=self.magic_box)
        self.magic_box_button.grid(row=9, column=0, pady=1, padx=10, sticky="ew")
        self.add_tooltip(self.magic_box_button, "Magicbox! click to see what's inside :)")
        
        #----------Text Widget with Scrollbar-----------       
        checkMesh_button = ttk.Button(self.root, text="Load mesh quality", command=self.load_meshChecked)
        #checkMesh_button.grid(row=2, column=1, sticky=tk.W, pady=(1, 0), padx=10)
        checkMesh_button.grid(row=2, column=1, pady=1, padx=10, sticky="ew")
        checkMesh_button['width'] = 18  # Adjust the width as needed
        
        checkMesh_button = ttk.Button(self.root, text="Load log file", command=self.load_log_file)
        #checkMesh_button.grid(row=2, column=2, sticky=tk.E, pady=(1, 0), padx=10)
        checkMesh_button.grid(row=2, column=2, pady=1, padx=1, sticky="ew")
        checkMesh_button['width'] = 9  # Adjust the width as needed\
        
        #self.text_box = tk.Text(self.root, wrap="none", height=20, width=110)  # Adjust the width as needed
        self.text_box = tk.Text(self.root, wrap=tk.WORD, height=25, width=110)  # Adjust the width as needed
        self.text_box.grid(row=3, column=1, columnspan=4, padx=10, pady=1, sticky=tk.W, rowspan=5)
        self.text_box.configure(foreground="white", background="black")
        self.text_box_scrollbar = tk.Scrollbar(self.root, command=self.text_box.yview)
        self.text_box_scrollbar.grid(row=3, column=1, columnspan=4, pady=1, sticky='nse', rowspan=5)
        self.text_box['yscrollcommand'] = self.text_box_scrollbar.set
        
        sample_text = """
        This is a sample text widget.
        You can search for words in this text.
        Just type a word in the search bar and press 'Enter'.
        """
        self.text_box.insert(tk.END, sample_text)
        
        # Add the search widget to the main app
        self.search_widget = SearchWidget(root, self.text_box)
        #----------Text Widget with Scrollbar-----------
        
        # Create a progress bar with the custom style
        self.progress_bar_canvas = ttk.Progressbar(self.root, orient="horizontal", length=220, mode="indeterminate", style="Custom.Horizontal.TProgressbar")
        self.progress_bar_canvas.grid(row=9, column=2, padx=50, pady=1)
        self.progress_bar_canvas_flag=True

        # Initialize variables for simulation thread
        self.simulation_thread = None
        self.simulation_running = False
        
        # Initialize the available fuels to choose from
        self.fuels = ["Methanol", "Ammonia", "Dodecane"]
        
        # Create a label for the "Fuel Selector" dropdown
        self.fuel_selector_label = ttk.Label(self.root, text="Fuel selector ▼", font=("TkDefaultFont", 12), background="white") # , foreground="green")
        #self.fuel_selector_label.grid(row=0, column=1, pady=1, padx=10, sticky="w") # can be shown when needed! FLAG

        # Define the fuel options
        fuels = ["Methanol", "Ammonia", "Dodecane"]

        # Create a StringVar to store the selected fuel
        self.selected_fuel = tk.StringVar()

        # Set a default value for the dropdown
        default_value = "Methanol"
        self.selected_fuel.set(default_value)

        # Create a dropdown menu for fuel selection
        self.fuel_selector = ttk.Combobox(self.root, textvariable=self.selected_fuel, values=fuels)
        self.fuel_selector.grid(row=1, column=1, pady=1, padx=10, sticky="w")

        # Bind an event handler to the <<ComboboxSelected>> event
        self.fuel_selector.bind("<<ComboboxSelected>>", self.on_fuel_selected)
       
        # Create a label for status messages
        self.status_label = ttk.Label(self.root, text="", foreground="blue")
        default_status = "This field will show the status of your work!"
        self.status_label.grid(row=0, column=1, columnspan=3, pady=1, padx=10, sticky="w")
        self.status_label.config(text=default_status)

        # ... (other initialization code)
        self.selected_file_path = None
        self.selected_file_content = None
        self.geometry_dest_path = None
        self.control_dict_path = None 
        
        self.header = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  10
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/\n"""
        self.thermo_type_params = ["type", "mixture", "transport", "thermo", "equationOfState", "specie", "energy"]
        self.mixture_params = ["molWeight", "rho", "rho0", "p0", "B", "gamma", "Cv", "Cp", "Hf", "mu", "Pr"]

    def run_terminal_command(self, command):
        # Your existing method for running terminal commands goes here
        pass
    
    def browse_directory(self):
        selected_file = filedialog.askopenfilename()

        if selected_file and os.path.basename(selected_file).startswith("physicalProperties"):
            self.selected_file_path = selected_file
            self.status_label.config(text=f"Selected file: {selected_file}", foreground="blue")

            # Update the current fuel status label
            current_fuel = self.detect_current_fuel()
            if current_fuel:
                self.status_label.config(text=f"Current fuel: {current_fuel}", foreground="blue")

                # Check if the detected current fuel matches any of the available fuels
                # If it does, set it as the selected fuel in the dropdown
                for fuel in self.fuels:
                    if fuel.lower() == current_fuel.lower():
                        self.selected_fuel.set(fuel)
                        break

            with open(selected_file, 'r') as file:
                file_content = file.read()
                self.selected_file_content = file_content
                old_values_mixture = {param: match.group(1) for param in self.mixture_params
                                      for match in re.finditer(f'{param}\s+(\S+)(;|;//.*)', file_content)}
                old_values_thermo_type = {param: match.group(1) for param in self.thermo_type_params
                                           for match in re.finditer(f'{param}\s+(\S+)(;|;//.*)', file_content)}
                self.open_replace_properties_popup(old_values_mixture, old_values_thermo_type)
        else:
            tk.messagebox.showerror("Error", "Selected file is not a physicalProperties file! Please look for the constant dir in your OF case!")
            

    def open_replace_properties_popup(self, old_values_mixture, old_values_thermo_type):
        selected_file = self.selected_file_path
        if selected_file:
            # Open a popup to replace the properties for the mixture and thermoType blocks
            ReplacePropertiesPopup(self, self.thermo_type_params, self.mixture_params, old_values_thermo_type, old_values_mixture)

        else:
            tk.messagebox.showerror("Error", "Please select a valid file first.")
            
    def detect_current_fuel(self):
        # Assuming the path is in the format '.../OpenFOAM-<version>/cases/<case_name>/constant/physicalProperties'
        parts = os.path.abspath(self.selected_file_path).split('.')   #split(os.sep)
        #partsi = os.path.abspath(self.selected_file_path).split('constant')   #split(os.sep)
        try:
            #index = parts.index('constant') 
            current_fuel = parts[1] # 0 + 1
            #print(current_fuel)
            return current_fuel
        except ValueError:
            return None
                  
    def on_fuel_selected(self, event):
        selected_fuel = self.fuel_options_menu.get().lower()
        if selected_fuel and selected_fuel != "Fuel Options":
            current_fuel = self.detect_current_fuel()
            if current_fuel:
                self.status_label.config(text=f"Current fuel: {current_fuel}", foreground="blue")
                self.replace_fuel(selected_fuel, current_fuel)

    def replace_fuel(self, selected_fuel, current_fuel):
        # Assuming the 'constant' directory is inside the case directory
        case_directory = os.path.dirname(os.path.dirname(self.selected_file_path))
            
        
        # Use find and exec to run sed on all files under the 'constant' directory
        #sed_command = f"sed -i 's/{current_fuel}/{selected_fuel}/g' {self.selected_file_path}" 
        sed_command = f"find {case_directory}/constant -type f -exec sed -i 's/{current_fuel}/{selected_fuel}/g' {{}} +"
        
        # Execute the sed command
        subprocess.run(sed_command, shell=True)
        
        # --------------------- Renaming files inside constant/ after the selected fuel ----------------------->
        # Rename the file associated with the current fuel
        current_file_path = os.path.join(case_directory, 'constant', f'physicalProperties.{current_fuel.lower()}')
        new_file_path = os.path.join(case_directory, 'constant', f'physicalProperties.{selected_fuel.lower()}')
        try:
            os.rename(current_file_path, new_file_path)
            tk.messagebox.showinfo("Fuel option", f"Fuel has been updated to {selected_fuel}!")
        except FileNotFoundError:
            # Handle the case where the file does not exist
            pass
            
        # Update the status label
        self.status_label.config(text=f"Fuel replaced. Selected fuel: {selected_fuel}", foreground="blue")
        # -----------------------------------------------------------------------------------------------------<

            
    # -------------- Welcome Message --------------------------    
    def show_welcome_message(self):
        welcome_message = "Welcome to Splash OpenFOAM!\n\n"\
                          "This is your interactive OpenFOAM simulation tool.\n"\
                          "Start by importing geometry and configuring your case."

        # You can choose to display the welcome message in a label or a messagebox
        # Label Example:
        welcome_label = ttk.Label(self.root, text=welcome_message, font=("TkDefaultFont", 12), background="lightblue")
        welcome_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

        # OR
        #self.root.after(3000, welcome_label.destroy)
        
        # Messagebox Example:
        whatnot = "Once you hit OK, you will never see life the same way again!"
        messagebox.showinfo("Welcome", whatnot)
        welcome_label.destroy()
        

    # -------------- Welcome Message -------------------------- 
     
     # -------------- Splash background image(s) --------------------------  
       
###    def add_bgImage(self):

###        # Load and display openfoam logo
###        self.splash_bgImage = Image.open("Resources/Images/racing-car.jpg")  
###        self.splash_bgImage = self.splash_bgImage.resize((1300, 870))
###        ##self.splash_bgImage = Image.open("Resources/Images/bubbles.jpg")  
###        ##self.splash_bgImage = self.splash_bgImage.resize((1300, 850))
###        #self.splash_bgImage = Image.open("Resources/Images/airplaneEngine.jpg")  
###        #self.splash_bgImage = self.splash_bgImage.resize((1300, 950))
###        self.splash_bgImage = ImageTk.PhotoImage(self.splash_bgImage)
###        self.splash_bgImage_label = tk.Label(self.root, image=self.splash_bgImage)
###        self.splash_bgImage_label.grid(row=0, column=3, pady=10, padx=10, sticky="ew", rowspan=15)
###        self.splash_bgImage_label.configure(background="white")  

    def add_bgImage(self):
        self.splash_bgImage_label = tk.Label(self.root)
        self.splash_bgImage_label.grid(row=0, column=5, pady=10, padx=10, sticky="ew", rowspan=15)
        self.splash_bgImage_label.configure(background="white")
        self.show_next_image()

    def show_next_image(self):
        image_path = self.image_paths[self.current_image_index]
        self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)

        # Load and display the next image in the list
        splash_bgImage = Image.open(image_path)
        splash_bgImage = splash_bgImage.resize((1350, 1000))
        #splash_bgImage = splash_bgImage.resize((1300, 870))
        splash_bgImage = ImageTk.PhotoImage(splash_bgImage)
        self.splash_bgImage_label.configure(image=splash_bgImage)
        self.splash_bgImage_label.image = splash_bgImage  # Keep a reference to prevent garbage collection

        # Schedule the next image after the total time delay
        self.root.after(self.time_delay, self.show_next_image)

    def start_slideshow(self):
        # Start the slideshow after the pre-specified delay
        self.root.after(self.time_delay, self.show_next_image)
        # -------------- Splash background image(s) -------------------------- 
    
    # -------------- Main logos --------------------------    
    def add_logos(self):

        # Load and display openfoam logo
        self.logo_openfoam = Image.open("Resources/Logos/openfoam_logo.png")  
        self.logo_openfoam = self.logo_openfoam.resize((140, 40))
        self.logo_openfoam = ImageTk.PhotoImage(self.logo_openfoam)
        self.OF_label = tk.Label(self.root, image=self.logo_openfoam)
        self.OF_label.grid(row=10, column=0, pady=10, padx=10, sticky="ew")
        self.OF_label.configure(background="white")
        
        # Load and display SMLT logo
        self.logo_simulitica = Image.open("Resources/Logos/simulitica_logo.png") 
        self.logo_simulitica = self.logo_simulitica.resize((140, 70))
        self.logo_simulitica = ImageTk.PhotoImage(self.logo_simulitica)
        self.simLabel = tk.Label(self.root, image=self.logo_simulitica)
        self.simLabel.grid(row=11, column=0, pady=10, padx=10, sticky="ew")
        self.simLabel.configure(background="white")

        # Create a label for copyright text
        self.copyright_label = ttk.Label(self.root, text="© 2023 Simulitica Ltd")
        self.copyright_label.grid(row=12, column=0, pady=10, padx=10, sticky="ew")
        self.copyright_label.configure(background="white", font="bold")
   # -------------- Main logos --------------------------        
        
        
    # -------------- importing the geometry --------------------------------------------------------------------    
    def import_geometry(self):
        file_path = filedialog.askopenfilename(
            title="Select Geometry File",
            filetypes=[("STL Files", "*.stl"), ("OBJ Files", "*.obj"), ("All Files", "*.*")],
            initialdir=os.path.dirname(self.selected_file_path) if self.selected_file_path else None
        )

        if file_path:
            self.selected_file_path = file_path
            meshing_folder = os.path.join(os.path.dirname(self.selected_file_path), "Meshing")
            self.status_label.config(text="The geometry file is successfully imported!", foreground="blue")
            # To enable meshing to start
            self.geometry_loaded = True

            # Create the Meshing folder if it doesn't exist
            if not os.path.exists(meshing_folder):
                os.makedirs(meshing_folder)

            # Copy and rename the geometry file
            geometry_filename = f"CAD.{file_path.split('.')[-1].lower()}"
            geometry_dest = os.path.join(meshing_folder, geometry_filename)
            self.geometry_dest_path = os.path.join(geometry_dest.split('CAD')[0])
            #print({self.geometry_dest_path})
            shutil.copyfile(self.selected_file_path, geometry_dest)
            
            # CAD programs logo paths 
            freecad_logo_path = os.path.join("Resources", "Logos", "freecad_logo.png")
            gmsh_logo_path = os.path.join("Resources", "Logos", "gmsh_logo.png")
            paraview_logo_path = os.path.join("Resources", "Logos", "paraview_logo.png")

            # Create a popup to ask the user whether to open the CAD file in FreeCAD, Gmsh, or ParaView
            popup = tk.Toplevel(self.root)
            popup.title("Choose CAD Viewer")
            popup.geometry("400x400")

            def open_freecad():
                subprocess.run(["freecad", geometry_dest, "&"], check=True)
                # Zoom to fit
                try:
                    doc = FreeCAD.ActiveDocument
                    doc.getObject(geometry_filename).ViewObject.Proxy.fit()
                except Exception as e:
                    print(f"Error zooming to fit in FreeCAD: {e}")
                popup.destroy()

            def open_gmsh():
                subprocess.run(["gmsh", geometry_dest, "&"], check=True)
                popup.destroy()

            def open_paraview():
                subprocess.run(["paraview", geometry_dest], check=True)
                popup.destroy()

            # Load logos
            freecad_logo = Image.open(freecad_logo_path).resize((160, 50), Image.ANTIALIAS)
            gmsh_logo = Image.open(gmsh_logo_path).resize((80, 70), Image.ANTIALIAS)
            paraview_logo = Image.open(paraview_logo_path).resize((200, 40), Image.ANTIALIAS)

            freecad_logo = ImageTk.PhotoImage(freecad_logo)
            gmsh_logo = ImageTk.PhotoImage(gmsh_logo)
            paraview_logo = ImageTk.PhotoImage(paraview_logo)

            # Create buttons with logos for the CAD viewers
            style = ttk.Style()
            #style.configure("TButton", padding=10, relief="solid", background="#ffffe0", foreground="black", borderwidth=1)
            style.configure("TButton", padding=10, relief="solid", background="white", foreground="black", borderwidth=1) 
            freecad_button = ttk.Button(popup, text="Open in FreeCAD", command=open_freecad, image=freecad_logo, compound="top")
            freecad_button.image = freecad_logo
            freecad_button.pack(side=tk.TOP, padx=30, pady=10)

            gmsh_button = ttk.Button(popup, text="Open in Gmsh", command=open_gmsh, image=gmsh_logo, compound="top")
            gmsh_button.image = gmsh_logo
            gmsh_button.pack(side=tk.TOP, padx=20, pady=10)

            paraview_button = ttk.Button(popup, text="Open in ParaView", command=open_paraview, image=paraview_logo, compound="top")
            paraview_button.image = paraview_logo
            paraview_button.pack(side=tk.TOP, padx=30, pady=10)

            popup.mainloop()
    
        else:
            tk.messagebox.showerror("Error", "No file selected for import")
        # -------------- importing the geometry --------------------------------------------------------------------    
 

    # -------------------------------- MESH CREATION ------------------------------

    # Start the journey of mesh creation :)
   
    def create_mesh(self):
        # Check if geometry is loaded
        if not self.geometry_loaded:
            messagebox.showinfo("Geometry Not Loaded", "Please load a geometry before creating the mesh.")
            return

        # Ask the user for mesh type using clickable buttons
        mesh_type = self.ask_mesh_type()

        if mesh_type is not None:
            # Execute the meshing command based on the selected mesh type
            if mesh_type == "Cartesian":
                # Execute Cartesian mesh command
                # Running "AllmeshCartesian" script here
                cartMesh_script = os.path.join(self.geometry_dest_path, "AllmeshCartesian")
                if os.path.exists(cartMesh_script):
                    chmod_command = ["chmod", "+x", cartMesh_script]
                    subprocess.run(chmod_command, check=True)

                    try:
                        # Activating the progress bar "again" - to be on the safe side
                        self.progress_bar_canvas_flag = True
                        self.start_progress_bar()

                        # Create a popup to get mesh parameters from the user
                        mesh_params = ["minCellSize", "maxCellSize", "boundaryCellSize", "nLayers", "thicknessRatio", "maxFirstLayerThickness"]  # Add other parameters as needed
                        values = self.ask_mesh_parameters(mesh_params)

# ------------------ In case you want to view meshing process in a separate terminal -------------------------
###                        # Generate the meshing command based on user input
###                        command = [f"./{os.path.basename(cartMesh_script)}"]
###                        for param, value in values.items():
###                            if value:
###                                command.extend([param, value])

###                        # Create a new terminal window and execute the command
###                        self.terminal_process = subprocess.Popen(
###                            f"gnome-terminal -- bash -c 'cd {self.geometry_dest_path}; {' '.join(command)}; exec bash'",
###                            shell=True,
###                            stdout=subprocess.PIPE,
###                            stderr=subprocess.PIPE,
###                            text=True,
###                            preexec_fn=os.setsid,  # Create a new process group
###                        )

###                        # Monitor the terminal process and display the output
###                        self.monitor_terminal()
# ------------------ In case you want to view meshing process in a separate terminal -------------------------
                        
                        # Use Popen to capture real-time output
                        command = [f"./{os.path.basename(cartMesh_script)}"]
                        process = subprocess.Popen(command, cwd=self.geometry_dest_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                        # Continuously read and insert output into the Text widget
                        while True:
                            line = process.stdout.readline()
                            if not line:
                                break
                            self.text_box.insert("end", line)
                            self.text_box.see("end")  # Scroll to the end to show real-time updates
                            self.text_box.update_idletasks()  # Update the widget
                           
                        # Wait for the process to complete
                        process.communicate()

                        # Check the return code and display appropriate messages
                        if process.returncode == 0:
                            tk.messagebox.showinfo("Mesh is generated", "Mesh constructed successfully.")
                        else:
                            tk.messagebox.showerror("Meshing Error", "There was an error during meshing. Check the console output.")
                    
                    

                    except subprocess.CalledProcessError as e:
                        tk.messagebox.showerror("Error", f"Error running AllmeshCartesian script: {e.stderr}")
                    finally:
                        self.progress_bar_canvas_flag = False
                else:
                    tk.messagebox.showerror("Error", "AllmeshCartesian script not found!")

            elif mesh_type == "Polyhedral":
                # Execute Polyhedral mesh command
                pass  # Replace with the actual command
            elif mesh_type == "Tetrahedral":
                # Execute Tetrahedral mesh command
                pass  # Replace with the actual command

# _____________________________________Craft your own mesh______________________________________________________

    def ask_mesh_parameters(self, mesh_params):
        # Read existing values from the AllmeshCartesian script
        existing_values = self.read_mesh_parameters_from_script()

        # Create a popup to ask the user for mesh parameters
        popup = tk.Toplevel(self.root)
        popup.geometry("250x450")
        popup.title("Mesh Parameters")

        param_entries = {}

        def display_help(param):
            # Get the help text from the dictionary or use a default message
            help_text = self.PARAMETER_HELP.get(param, f"{param}:\nProvide a brief description or range of values.")
            messagebox.showinfo("Help", help_text)

        # Populate the popup with parameter entry fields, their old values, and help buttons
        for param in mesh_params:
            frame = ttk.Frame(popup)
            frame.pack(fill=tk.X)

            ttk.Label(frame, text=param).pack()
            #ttk.Label(frame, text=param).pack(side=tk.LEFT padx=(0, 10))
            
            # Add a help button
            style = ttk.Style()
            style.configure("TButton", padding=10, relief="flat", background="lightblue", foreground="black", justify="right")
            help_button = ttk.Button(frame, text="?", command=lambda param=param: display_help(param), width=1)
            #help_button.configure(text="?", foreground="blue")
            help_button.pack(side=tk.RIGHT)
            #help_button.pack(side=tk.LEFT) 
            
            entry_var = tk.StringVar()
            entry_var.set(existing_values.get(param, ""))  # Set the default value from the script
            entry = ttk.Entry(frame, textvariable=entry_var)
            #entry.pack(side=tk.LEFT)
            entry.pack()   

            param_entries[param] = entry

        def update_mesh_parameters():
            # Get the new values from the entry fields
            new_values = {param: entry.get() for param, entry in param_entries.items()}

            # Close the popup
            popup.destroy()

            if new_values:
                # TODO: Apply the new values to the AllmeshCartesian script
                # You need to modify this part based on the structure of your script
                self.update_mesh_parameters_in_script(new_values)

                # Start the meshing process [FLAG!!]
                self.start_meshing()

        # Add an "Update" button to apply the new values
        ttk.Button(popup, text="Start Meshing!", command=update_mesh_parameters).pack() # update mesh parameters then start meshing.

        # Wait for the popup to be closed
        self.root.wait_window(popup)

        # Return the new values or an empty dictionary if the popup was closed without clicking "Update"
        return new_values if "new_values" in locals() else {}

    # ------ rest of fully functioning mesher   
    def read_mesh_parameters_from_script(self):
        # TODO: Implement this method to read existing values from the AllmeshCartesian script
        # You need to modify this part based on the structure of your script
        existing_values = {}
        
        # Full path to AllmeshCartesian script
        script_file_path = os.path.join(self.geometry_dest_path, "AllmeshCartesian")
        
        try:
            with open(script_file_path, "r") as script_file:
                for line in script_file:
                    if "-set" in line:
                        parts = line.split()
                        if len(parts) == 4:
                            param = parts[3]
                            value = parts[4]
                            existing_values[param] = value
        except FileNotFoundError:
            print(f"Error: File not found - {script_file_path}")
        return existing_values
       
    def update_mesh_parameters_in_script(self, new_values):
        # TODO: Implement this method to update the AllmeshCartesian script with new parameter values
        # You need to modify this part based on the structure of your script
        script_file_path = os.path.join(self.geometry_dest_path, "AllmeshCartesian")

        with open(script_file_path, "r") as script_file:
            lines = script_file.readlines()

        for i, line in enumerate(lines):
            for param, value in new_values.items():
                if f"-entry {param} -set" in line:
                    lines[i] = f'foamDictionary system/meshDict -entry {param} -set {value}\n'
                    break

        with open(script_file_path, "w") as script_file:
            script_file.writelines(lines)
            
# ______Craft your own mesh with teh desired type _______

    def ask_mesh_type(self):
        # Create a popup to ask the user for mesh type
        popup = tk.Toplevel(self.root)
        popup.geometry("250x130")

        # Add clickable buttons for mesh type
        ttk.Radiobutton(popup, text="Cartesian", variable=self.mesh_type_var, value="Cartesian").pack()
        ttk.Radiobutton(popup, text="Polyhedral", variable=self.mesh_type_var, value="Polyhedral").pack()
        ttk.Radiobutton(popup, text="Tetrahedral", variable=self.mesh_type_var, value="Tetrahedral").pack()

        # Add a button to confirm the selection
        ttk.Button(popup, text="OK", command=popup.destroy).pack()

        # Wait for the popup to be closed
        self.root.wait_window(popup)

        # Return the selected mesh type
        return self.mesh_type_var.get()
        
# -------------------------------- MESH CREATION ------------------------------            
            
    # --------------------- running the simulation ---------------------------
    def initialize_case(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.selected_file_path = selected_directory
            self.status_label.config(text=f"Case directory identified: {selected_directory}", foreground="blue")
            self.run_simulation_button["state"] = tk.NORMAL  # Enable the "Run Simulation" button
        else:
            self.status_label.config(text="No directory selected.", foreground="red")
            self.run_simulation_button["state"] = tk.DISABLED  # Disable the "Run Simulation" button


    def run_simulation(self):
        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "Please initialize the case directory before running the simulation.")
            return

        if not self.simulation_running:
            self.simulation_thread = threading.Thread(target=self.run_openfoam_simulation)
            self.simulation_thread.start()
            self.simulation_running = True
            self.stop_simulation_button["state"] = tk.NORMAL
        else:
            tk.messagebox.showinfo("Simulation Running", "Simulation is already running.")

    def run_openfoam_simulation(self):
        allrun_script = os.path.join(self.selected_file_path, "Allrun")
        if os.path.exists(allrun_script):
            chmod_command = ["chmod", "+x", allrun_script]
            subprocess.run(chmod_command, check=True)

            try:
                self.start_progress_bar()

                # FLAG! In case the controlDict still has more than 1 instance of "writeNow"
                control_dict_path = os.path.join(self.selected_file_path, "system", "controlDict")
                self.replace_write_now_with_end_time(control_dict_path)
                
                # Use Popen to capture real-time output
                process = subprocess.Popen(["./Allrun"], cwd=self.selected_file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                # Continuously read and insert output into the Text widget
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.text_box.insert("end", line)
                    self.text_box.see("end")  # Scroll to the end to show real-time updates
                    self.text_box.update_idletasks()  # Update the widget
                   
                # Wait for the process to complete
                process.communicate()

                # Check the return code and display appropriate messages
                if process.returncode == 0:
                    tk.messagebox.showinfo("Simulation Finished", "Simulation completed successfully.")
                else:
                    tk.messagebox.showerror("Simulation Error", "There was an error during simulation. Check the console output.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error running Allrun script: {e.stderr}")
            finally:
                self.stop_progress_bar()
                self.stop_simulation_button["state"] = tk.DISABLED
        else:
            tk.messagebox.showerror("Error", "Allrun script not found!")
            
        # Now, update the modification timestamp of the controlDict file
        subprocess.run(["touch", control_dict_path], check=True)  # Update file modification timestamp
        time.sleep(0.1)  # Add a 100ms delay if needed
        
        
    def stop_simulation(self): # FLAG! at the moment, the controlDict file needs to be open and saved and closed, for the function to work :/
        if not self.simulation_running:
            tk.messagebox.showinfo("Nothing to Stop", "There's no simulation currently running to stop.")
            return

        control_dict_path = os.path.join(self.selected_file_path, "system", "controlDict")  # FLAG! Duplication..
        if os.path.exists(control_dict_path):
            try:
                subprocess.run(["sed", "-i", '0,/endTime/s//writeNow/', control_dict_path], check=True)
                #time.sleep(0.1)  # Add a 100ms delay
                #subprocess.run(["ex", "-sc", 'wq', control_dict_path], check=True)
                print(control_dict_path)
                #subprocess.run(["touch", control_dict_path], check=True)  # Update file modification timestamp
                #subprocess.run(["sync"], check=True)  # Flush file system buffers to disk
                #time.sleep(0.1)  # Add a 100ms delay
                tk.messagebox.showinfo("Stop Simulation", "Simulation stopped successfully.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error stopping simulation: {e.stderr}")

        else:
            tk.messagebox.showerror("Error", "controlDict file not found!")

        self.stop_simulation_button["state"] = tk.DISABLED  # FLAG - is that really needed?! 
        
        # Enable the user to user "run simulation" button again
        self.simulation_running = False
        
        # Disable the button until a new sim is launched
        self.stop_simulation_button["state"] = tk.DISABLED

    
    def replace_write_now_with_end_time(self, control_dict_path):
        subprocess.run(["sed", "-i", 's/writeNow/endTime/g', control_dict_path], check=True)
        
    def load_log_file(self):
            # Specify the path to the "log" file
            log_file_path = os.path.join(self.selected_file_path, "log")

            # Check if the file exists
            if os.path.exists(log_file_path):
                # Read the content of the file
                with open(log_file_path, "r") as file:
                    content = file.read()

                # Insert the content into the Text widget
                self.text_box.delete(1.0, "end")  # Clear previous content
                self.text_box.insert("end", content)
            else:
                # If the file doesn't exist, display a message in the Text widget
                self.text_box.delete(1.0, "end")  # Clear previous content
                self.text_box.insert("end", "log file not found.") 
                
    def start_progress_bar(self):
        self.root.after(100, self.update_progress)

    def update_progress(self):
        # Update the progress bar value
        self.progress_bar_canvas.step(5)

        # Check if the flag is activated to stop the progress bar
        if not self.progress_bar_canvas_flag:
            self.stop_progress_bar()
            return  # Exit the method to prevent further updates

        # Schedule the update_progress method to be called after 100 milliseconds
        self.root.after(100, self.update_progress)

    def stop_progress_bar(self):
        # Stop the progress bar
        self.progress_bar_canvas.stop()

        # Set the mode to 'determinate' to reset the progress bar
        self.progress_bar_canvas.configure(mode="determinate")
        self.progress_bar_canvas["value"] = 0
   


#______________________________________________________________________
# FLAG: essentially intended to be dedicated for checkMesh script****
    def load_meshChecked(self):
            # Specify the path to the "AllmeshCartesian" file
            allmesh_cartesian_path = os.path.join(self.geometry_dest_path, "meshChecked")

            # Check if the file exists
            if os.path.exists(allmesh_cartesian_path):
                # Read the content of the file
                with open(allmesh_cartesian_path, "r") as file:
                    content = file.read()

                # Insert the content into the Text widget
                self.text_box.delete(1.0, "end")  # Clear previous content
                self.text_box.insert("end", content)
            else:
                # If the file doesn't exist, display a message in the Text widget
                self.text_box.delete(1.0, "end")  # Clear previous content
                self.text_box.insert("end", "meshChecked file not found.")
#______________________________________________________________________           
             
# -------------------------------- Plot results ------------------------------  
    # Function to plot results using xmgrace
    def plot_results_xmgrace(self):
        try:
            # Check if xmgrace is installed
            subprocess.run(["xmgrace", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Run xmgrace in the same terminal window
            subprocess.run(["xmgrace"])
        except subprocess.CalledProcessError:
            tk.messagebox.showerror("Error", "xmgrace is not installed or not in the system's PATH.")
# -------------------------------- Plot results ------------------------------  
     #=============================================================================
    def execute_command(self):
        #command = "source ~/.bashrc"; self.entry.get()
        command = self.entry.get()

        # Create a new terminal window and execute the command
        self.terminal_process = subprocess.Popen(
            #f"gnome-terminal -- bash -c 'source ~/.bashrc'",
            f"gnome-terminal -- bash -c '{command}; exec bash'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid,  # Create a new process group
        )
        # Enable the stop button
        self.stop_button.config(state=tk.NORMAL)

        # Disable the execute button
        self.execute_button.config(state=tk.DISABLED)

        # Monitor the terminal process and display the output
        self.monitor_terminal()

    def monitor_terminal(self):
        if self.terminal_process:
            try:
                # Read the standard output and standard error of the terminal
                output, _ = self.terminal_process.communicate(timeout=0.1)
                if output:
                    self.output_text.insert(tk.END, output)
                    self.output_text.see(tk.END)
            except subprocess.TimeoutExpired:
                # The terminal process is still running
                self.root.after(100, self.monitor_terminal)
            else:
                # The terminal process has completed
                self.execute_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.status_label.config(text="Command executed successfully", foreground="blue")
                #self.status_label.delete(0, END)
# ================================================================
    def stop_command(self):
        if self.terminal_process:
            # Terminate the terminal process and its process group
            os.killpg(os.getpgid(self.terminal_process.pid), signal.SIGTERM)
            self.status_label.config(text="Command execution stopped", foreground="red")
            
# ===================Tool tip (hover over the button)=============================================
    def add_tooltip(self, widget, text):
        widget.bind("<Enter>", lambda event: self.show_tooltip_right(widget, text))
        widget.bind("<Leave>", lambda event: self.hide_tooltip())
        
    def show_tooltip_right(self, widget, text):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 150  # Adjust 25 as needed for the desired distance
        y += widget.winfo_rooty()
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=text, justify='left', background='#ffffe0', relief='solid', borderwidth=1)
        label.pack(ipadx=1)
        
    def hide_tooltip(self):
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            del self.tooltip
            
    def magic_box(self): # Fixing the issue of updating process with the modification in controlDict | FLAG!
        # Manually touch the controlDict file
        control_dict_path = os.path.join(self.selected_file_path, "system", "controlDict")
        try:
            subprocess.run(["touch", control_dict_path], check=True)
        except subprocess.CalledProcessError as e:
            tk.messagebox.showerror("Error", f"Error touching controlDict: {e.stderr}")
            
     

        
        
if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalApp(root)
    root.mainloop()   




#        # Monitor residuals using foamMonitor
#        self.monitor_residuals()

#    def monitor_residuals(self):
#        residuals_file = os.path.join(os.path.dirname(self.selected_file_path), "postProcessing", "residuals", "0", "residuals.dat")

#        # Check if the residuals file exists
#        if not os.path.exists(residuals_file):
#            tk.messagebox.showerror("Error", "Residuals file not found!")
#            return

#        # Run foamMonitor to continuously monitor residuals
#        foam_monitor_command = f"foamMonitor -l {residuals_file}"
#        process = subprocess.Popen(foam_monitor_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

#        # Read and display residuals in real-time
#        for line in iter(process.stdout.readline, b''):
#            print(line.decode("utf-8"))

#            # Extract residuals from the output and update the plot
#            residuals = [float(x) for x in re.findall(r"residual\s*=\s*([\d.]+)", line.decode("utf-8"))]

#            if residuals:
#                self.update_plot(residuals)

#        process.stdout.close()
#        process.stderr.close()

#        # Wait for foamMonitor to finish
#        process.wait()

#        # Update UI
#        self.simulation_running = False
#        print("Residual monitoring completed.")

#    def update_plot(self, residuals):
#        # Update the plot with new residuals
#        self.ax.clear()
#        self.ax.plot(residuals, label="Residuals")
#        self.ax.set_xlabel("Iteration")
#        self.ax.set_ylabel("Residual Value")
#        self.ax.legend()
#        self.canvas.draw()
    # --------------------- running the simulation ---------------------------
            
            

#    def import_geometry(self):
#        # Ask the user to select a geometry file
#        geometry_file = filedialog.askopenfilename(
#            #filetypes=[("Geometry files", "*.stl;*.obj"), ("All files", "*.*")],
#            filetypes=[("Geometry files", "*.stl"), ("All files", "*.*")],
#            initialdir=os.path.dirname(self.selected_file_path) if self.selected_file_path else None
#        )

#        if geometry_file:
#            # Get the destination path for the "Meshing" folder
#            meshing_folder = os.path.join(os.path.dirname(self.selected_file_path), "Meshing")

#            # Check if the "Meshing" folder exists; if not, create it
#            if not os.path.exists(meshing_folder):
#                os.makedirs(meshing_folder)

#            # Copy the selected geometry file to the "Meshing" folder and rename it to "CAD.stl"
#            geometry_file_name = "CAD.stl"
#            destination_path = os.path.join(meshing_folder, geometry_file_name)
#            shutil.copy(geometry_file, destination_path)

#            # Update the status label
#            self.status_label.config(text=f"Geometry file {geometry_file_name} imported to Meshing folder", foreground="green")
#        else:
#            self.status_label.config(text="Geometry import canceled", foreground="blue")
#            
#        # Check if a file is selected
#        if not self.selected_file_path:
#            self.status_label.config(text="No file selected for import", foreground="red")
#            return
           
         
            
#        # Configure rows and columns to expand
#        self.root.grid_columnconfigure(0, weight=1)
#        self.root.grid_columnconfigure(1, weight=1)
#        self.root.grid_columnconfigure(2, weight=1)
#        self.root.grid_columnconfigure(3, weight=1)

#        # Create an entry field for entering the command
#        self.entry = ttk.Entry(self.root, width=40)
#        self.entry.grid(row=0, column=0, pady=10, padx=10, columnspan=2, sticky="ew")

#        # Create a button to execute the command
#        self.execute_button = ttk.Button(self.root, text="Execute Command", command=self.execute_command)
#        self.execute_button.grid(row=0, column=2, pady=10, padx=10, sticky="ew")

#        # Create a label to display the status of the command execution
#        self.status_label = ttk.Label(self.root, text="", foreground="blue")
#        self.status_label.grid(row=1, column=0, pady=5, padx=10, columnspan=2, sticky="w")

#        # Create a button to stop the command execution
#        self.stop_button = ttk.Button(self.root, text="Stop Command", command=self.stop_command, state=tk.DISABLED)
#        self.stop_button.grid(row=0, column=3, pady=5, padx=10, sticky="ew")

#        # Create a button to start meshing
#        self.mesh_button = ttk.Button(self.root, text="Start Meshing!", command=self.create_mesh)
#        self.mesh_button.grid(row=1, column=3, pady=5, padx=10, sticky="ew")

#        # Create buttons to load and display images or GIFs
#        self.load_image_button = ttk.Button(self.root, text="Load Image or GIF", command=lambda: self.load_image("image1"))
#        self.load_image_button.grid(row=2, column=3, pady=10, padx=10, sticky="ew")

#        # Create labels to display the loaded images or GIFs
#        self.image_labels = []

#        # Load and display the logo
#        #self.logo_image = Image.open("logoWinGD.jpg")  # Replace with your logo file name
#        self.logo_image = Image.open("logoS.png")  # Replace with your logo file name
#        self.logo_image = self.logo_image.resize((100, 100))
#        self.logo_image = ImageTk.PhotoImage(self.logo_image)
#        self.logo_label = tk.Label(self.root, image=self.logo_image)
#        self.logo_label.grid(row=95, column=3, pady=10, padx=10, rowspan=5, columnspan=10, sticky="ew")

#        # Create a label for copyright text
#        self.copyright_label = ttk.Label(self.root, text="© 2023 Simulitica Ltd")
#        self.copyright_label.grid(row=100, column=3, rowspan=5, columnspan=6, pady=10, padx=10, sticky="ew")

#        self.terminal_process = None

#    # -------------------------- COMBOBOX ---------------------------------------
#    #=============================================================================
#    def execute_command(self):
#        #command = "source ~/.bashrc"; self.entry.get()
#        command = self.entry.get()

#        # Create a new terminal window and execute the command
#        self.terminal_process = subprocess.Popen(
#            #f"gnome-terminal -- bash -c 'source ~/.bashrc'",
#            f"gnome-terminal -- bash -c '{command}; exec bash'",
#            shell=True,
#            stdout=subprocess.PIPE,
#            stderr=subprocess.PIPE,
#            text=True,
#            preexec_fn=os.setsid,  # Create a new process group
#        )
#        # Enable the stop button
#        self.stop_button.config(state=tk.NORMAL)

#        # Disable the execute button
#        self.execute_button.config(state=tk.DISABLED)

#        # Monitor the terminal process and display the output
#        self.monitor_terminal()
## ================================================================
#    # Defining the function of meshing button 
#    def create_mesh(self):
#        command = "sh mesh.sh"

#        # Create a new terminal window and execute the command
#        self.terminal_process = subprocess.Popen(
#            f"gnome-terminal -- bash -c '{command}; exec bash'",
#            shell=True,
#            stdout=subprocess.PIPE,
#            stderr=subprocess.PIPE,
#            text=True,
#            preexec_fn=os.setsid,  # Create a new process group
#        )

#        # Enable the stop button
#        self.stop_button.config(state=tk.NORMAL)

#        # Disable the execute button
#        self.execute_button.config(state=tk.NORMAL)

#        # Monitor the terminal process and display the output
#        self.monitor_terminal()
## ================================================================
#    def monitor_terminal(self):
#        if self.terminal_process:
#            try:
#                # Read the standard output and standard error of the terminal
#                output, _ = self.terminal_process.communicate(timeout=0.1)
#                if output:
#                    self.output_text.insert(tk.END, output)
#                    self.output_text.see(tk.END)
#            except subprocess.TimeoutExpired:
#                # The terminal process is still running
#                self.root.after(100, self.monitor_terminal)
#            else:
#                # The terminal process has completed
#                self.execute_button.config(state=tk.NORMAL)
#                self.stop_button.config(state=tk.DISABLED)
#                self.status_label.config(text="Command executed successfully", foreground="green")
#                #self.status_label.delete(0, END)
## ================================================================
#    def stop_command(self):
#        if self.terminal_process:
#            # Terminate the terminal process and its process group
#            os.killpg(os.getpgid(self.terminal_process.pid), signal.SIGTERM)
#            self.status_label.config(text="Command execution stopped", foreground="red")
## ================================================================
#    def load_image(self, image_type):
#        file_path = filedialog.askopenfilename(filetypes=[
#            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
#            ("GIF files", "*.gif")
#        ])
#        if file_path:
#            # Open and display the selected image or GIF using PIL
#            image = Image.open(file_path)
#            image = image.resize((800, 800))  # Resize the image as needed
#            photo = ImageTk.PhotoImage(image=image)
#            
#            # Create a new label for each loaded image
#            image_label = tk.Label(self.root, image=photo)
#            image_label.image = photo  # Keep a reference to prevent garbage collection
#            
#            # Append the label to the list and place it in the grid
#            self.image_labels.append(image_label)
#            row = len(self.image_labels) + 4
#            #column = 0 if image_type == "image" else (1 if image_type == "image2" else 2)
#            column = 0 
#            image_label.grid(row=row, column=column, pady=5, padx=10, sticky="nsew")
#            
#            self.status_label.config(text=f"{image_type.capitalize()} loaded successfully", foreground="green")
## ================================================================


