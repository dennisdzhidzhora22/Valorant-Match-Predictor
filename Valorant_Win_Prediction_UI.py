import pickle
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, font

class ValorantMatchPredictor(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.title("Valorant Match Predictor")
        self.geometry("900x700")
        self.configure(bg="#0f1923")  # Valorant dark blue background

        # Define colors
        self.valorant_red = "#ff4655"
        self.valorant_blue = "#0f1923"
        self.valorant_white = "#ece8e1"

        # Load custom font
        self.load_custom_fonts()

        # Set app icon if available
        try:
            self.iconbitmap("valorant_icon.ico")
        except:
            pass

        # Define agents and maps
        self.all_agents = sorted(['yoru', 'chamber', 'reyna', 'breach', 'cypher',
                           'phoenix', 'sage', 'astra', 'raze', 'viper',
                           'jett', 'brimstone', 'killjoy', 'omen', 'skye',
                           'kayo', 'sova'])

        self.all_maps = ['Ascent', 'Bind', 'Breeze', 'Fracture', 'Haven',
                         'Icebox', 'Split', 'TBD']

        # Expected column order for the model
        self.expected_column_order = ['RoundNumber', 'Team1_RoundScore', 'Team2_RoundScore', 'team1_astra',
                                   'team1_breach', 'team1_brimstone', 'team1_chamber', 'team1_cypher',
                                   'team1_jett', 'team1_kayo', 'team1_killjoy', 'team1_omen',
                                   'team1_phoenix', 'team1_raze', 'team1_reyna', 'team1_sage',
                                   'team1_skye', 'team1_sova', 'team1_viper', 'team1_yoru', 'team2_astra',
                                   'team2_breach', 'team2_brimstone', 'team2_chamber', 'team2_cypher',
                                   'team2_jett', 'team2_kayo', 'team2_killjoy', 'team2_omen',
                                   'team2_phoenix', 'team2_raze', 'team2_reyna', 'team2_sage',
                                   'team2_skye', 'team2_sova', 'team2_viper', 'team2_yoru', 'Map_Ascent',
                                   'Map_Bind', 'Map_Breeze', 'Map_Fracture', 'Map_Haven', 'Map_Icebox',
                                   'Map_Split', 'Map_TBD']

        # Initialize game state variables
        self.team1_agents = []
        self.team2_agents = []
        self.selected_map = tk.StringVar(value=self.all_maps[0])
        self.round_number = 1
        self.team1_score = 0
        self.team2_score = 0

        # Load the pre-trained model
        self.load_model()

        # Create UI elements
        self.create_widgets()

    def load_custom_fonts(self):
        # Define a fallback font and the Valorant-style font
        self.default_font = ("Helvetica", 12)
        self.header_font = ("Helvetica", 24, "bold")
        self.title_font = ("Helvetica", 18, "bold")
        self.subtitle_font = ("Helvetica", 14, "bold")
        self.content_font = ("Helvetica", 12)

        # Try to load Tungsten-Bold font if available (similar to Valorant font)
        # Fallback to fonts that should be available on most systems
        try:
            self.custom_fonts = {
                "header": font.Font(family="Tungsten-Bold", size=24, weight="bold"),
                "title": font.Font(family="Tungsten-Bold", size=18, weight="bold"),
                "subtitle": font.Font(family="Tungsten-Bold", size=14, weight="bold"),
                "content": font.Font(family="Din", size=12),
            }
            self.header_font = self.custom_fonts["header"]
            self.title_font = self.custom_fonts["title"]
            self.subtitle_font = self.custom_fonts["subtitle"]
            self.content_font = self.custom_fonts["content"]
        except:
            # If custom fonts fail, we'll use the defaults defined above
            pass

    def load_model(self):
        try:
            with open('gradient_boosting_model2.pkl', 'rb') as f:
                self.rf_model = pickle.load(f)
            print("Model loaded successfully!")
        except FileNotFoundError:
            messagebox.showerror("Error", "Model file 'gradient_boosting_model2.pkl' not found!")
            self.destroy()

    def create_widgets(self):
        # Main header
        header_frame = tk.Frame(self, bg=self.valorant_blue)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        title_label = tk.Label(header_frame, text="VALORANT MATCH PREDICTOR",
                               font=self.header_font,
                               fg=self.valorant_red, bg=self.valorant_blue)
        title_label.pack()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Setup tab
        self.setup_tab = tk.Frame(self.notebook, bg=self.valorant_blue)
        self.notebook.add(self.setup_tab, text="Team Setup")

        # Prediction tab
        self.prediction_tab = tk.Frame(self.notebook, bg=self.valorant_blue)
        self.notebook.add(self.prediction_tab, text="Predictions")

        # Configure notebook style to fix the text color issue
        style = ttk.Style()
        style.theme_create("valorant_theme", parent="alt",
                           settings={
                               "TNotebook": {
                                   "configure": {"background": self.valorant_blue, "tabmargins": [2, 5, 2, 0]}},
                               "TNotebook.Tab": {
                                   "configure": {
                                       "background": self.valorant_blue,
                                       "foreground": self.valorant_white,  # Fix for text color
                                       "padding": [10, 5],
                                   },
                                   "map": {
                                       "background": [("selected", self.valorant_red)],
                                       "foreground": [("selected", self.valorant_white)],
                                       "expand": [("selected", [1, 1, 1, 0])]
                                   }
                               }
                           })
        style.theme_use("valorant_theme")

        # Setup the team selection UI
        self.create_setup_ui()

        # Setup the prediction UI
        self.create_prediction_ui()

    def create_setup_ui(self):
        # Create a canvas with scrollbar for the agent lists
        main_frame = tk.Frame(self.setup_tab, bg=self.valorant_blue)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Team 1 Frame with scrollable content
        team1_outer_frame = tk.LabelFrame(main_frame, text="Team 1",
                                          font=self.subtitle_font,
                                          fg=self.valorant_white, bg=self.valorant_blue)
        team1_outer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create canvas and scrollbar for Team 1
        team1_canvas = tk.Canvas(team1_outer_frame, bg=self.valorant_blue,
                                 highlightthickness=0)
        team1_scrollbar = ttk.Scrollbar(team1_outer_frame, orient="vertical",
                                        command=team1_canvas.yview)
        team1_canvas.configure(yscrollcommand=team1_scrollbar.set)

        team1_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        team1_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create frame for checkboxes inside canvas
        team1_frame = tk.Frame(team1_canvas, bg=self.valorant_blue)
        team1_canvas.create_window((0, 0), window=team1_frame, anchor="nw",
                                   tags="team1_frame")

        # Team 2 Frame with scrollable content
        team2_outer_frame = tk.LabelFrame(main_frame, text="Team 2",
                                          font=self.subtitle_font,
                                          fg=self.valorant_white, bg=self.valorant_blue)
        team2_outer_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create canvas and scrollbar for Team 2
        team2_canvas = tk.Canvas(team2_outer_frame, bg=self.valorant_blue,
                                 highlightthickness=0)
        team2_scrollbar = ttk.Scrollbar(team2_outer_frame, orient="vertical",
                                        command=team2_canvas.yview)
        team2_canvas.configure(yscrollcommand=team2_scrollbar.set)

        team2_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        team2_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create frame for checkboxes inside canvas
        team2_frame = tk.Frame(team2_canvas, bg=self.valorant_blue)
        team2_canvas.create_window((0, 0), window=team2_frame, anchor="nw",
                                   tags="team2_frame")

        # Team 1 Agent Checkboxes
        self.team1_vars = {}
        for idx, agent in enumerate(sorted(self.all_agents)):
            var = tk.BooleanVar()
            self.team1_vars[agent] = var
            agent_cb = tk.Checkbutton(team1_frame, text=agent.capitalize(),
                                      variable=var,
                                      bg=self.valorant_blue,
                                      fg=self.valorant_white,
                                      selectcolor=self.valorant_blue,
                                      activebackground=self.valorant_blue,
                                      activeforeground=self.valorant_white,
                                      font=self.content_font)
            agent_cb.grid(row=idx, column=0, sticky="w", padx=10, pady=3)

        # Team 2 Agent Checkboxes
        self.team2_vars = {}
        for idx, agent in enumerate(sorted(self.all_agents)):
            var = tk.BooleanVar()
            self.team2_vars[agent] = var
            agent_cb = tk.Checkbutton(team2_frame, text=agent.capitalize(),
                                      variable=var,
                                      bg=self.valorant_blue,
                                      fg=self.valorant_white,
                                      selectcolor=self.valorant_blue,
                                      activebackground=self.valorant_blue,
                                      activeforeground=self.valorant_white,
                                      font=self.content_font)
            agent_cb.grid(row=idx, column=0, sticky="w", padx=10, pady=3)

        # Map selection frame
        map_frame = tk.LabelFrame(self.setup_tab, text="Map",
                                  font=self.subtitle_font,
                                  fg=self.valorant_white, bg=self.valorant_blue)
        map_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Map selection dropdown
        map_label = tk.Label(map_frame, text="Select Map:",
                             font=self.content_font,
                             fg=self.valorant_white, bg=self.valorant_blue)
        map_label.pack(side=tk.LEFT, padx=10, pady=10)

        map_dropdown = ttk.Combobox(map_frame, textvariable=self.selected_map,
                                    values=self.all_maps, width=15,
                                    font=self.content_font)
        map_dropdown.pack(side=tk.LEFT, padx=10, pady=10)

        # Start button
        start_button = tk.Button(map_frame, text="START MATCH",
                                 command=self.start_match,
                                 bg=self.valorant_red, fg=self.valorant_white,
                                 font=self.subtitle_font,
                                 relief=tk.FLAT,
                                 padx=15, pady=5)
        start_button.pack(side=tk.RIGHT, padx=20, pady=10)

        # Configure the canvas to update scroll region when frame size changes
        team1_frame.bind("<Configure>", lambda e: team1_canvas.configure(
            scrollregion=team1_canvas.bbox("all")))
        team2_frame.bind("<Configure>", lambda e: team2_canvas.configure(
            scrollregion=team2_canvas.bbox("all")))

    def create_prediction_ui(self):
        # Score and Round Display
        info_frame = tk.Frame(self.prediction_tab, bg=self.valorant_blue)
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        self.round_label = tk.Label(info_frame, text="Round: 1",
                                    font=self.title_font,
                                    fg=self.valorant_white, bg=self.valorant_blue)
        self.round_label.pack(side=tk.TOP, pady=5)

        score_frame = tk.Frame(info_frame, bg=self.valorant_blue)
        score_frame.pack(side=tk.TOP, pady=5)

        self.team1_score_label = tk.Label(score_frame, text="Team 1: 0",
                                          font=self.subtitle_font,
                                          fg=self.valorant_white, bg=self.valorant_blue)
        self.team1_score_label.pack(side=tk.LEFT, padx=50)

        self.team2_score_label = tk.Label(score_frame, text="Team 2: 0",
                                          font=self.subtitle_font,
                                          fg=self.valorant_white, bg=self.valorant_blue)
        self.team2_score_label.pack(side=tk.RIGHT, padx=50)

        # Prediction Display
        prediction_frame = tk.Frame(self.prediction_tab, bg=self.valorant_blue)
        prediction_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        prediction_label = tk.Label(prediction_frame, text="WIN PROBABILITY",
                                    font=self.title_font,
                                    fg=self.valorant_white, bg=self.valorant_blue)
        prediction_label.pack(pady=10)

        # Team probability bars
        self.probability_frame = tk.Frame(prediction_frame, bg=self.valorant_blue)
        self.probability_frame.pack(fill=tk.X, expand=True, padx=20, pady=10)

        # Team 1 probability
        team1_prob_frame = tk.Frame(self.probability_frame, bg=self.valorant_blue)
        team1_prob_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        team1_label = tk.Label(team1_prob_frame, text="Team 1",
                               font=self.subtitle_font,
                               fg=self.valorant_white, bg=self.valorant_blue)
        team1_label.pack(side=tk.LEFT, padx=5)

        self.team1_prob_var = tk.StringVar(value="N/A")
        self.team1_prob_label = tk.Label(team1_prob_frame,
                                         textvariable=self.team1_prob_var,
                                         font=self.subtitle_font,
                                         fg=self.valorant_white, bg=self.valorant_blue)
        self.team1_prob_label.pack(side=tk.RIGHT, padx=5)

        self.team1_bar = tk.Canvas(self.probability_frame, height=30, bg="#333333",
                                   highlightthickness=0)
        self.team1_bar.pack(fill=tk.X, padx=20, pady=5)

        # Team 2 probability
        team2_prob_frame = tk.Frame(self.probability_frame, bg=self.valorant_blue)
        team2_prob_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        team2_label = tk.Label(team2_prob_frame, text="Team 2",
                               font=self.subtitle_font,
                               fg=self.valorant_white, bg=self.valorant_blue)
        team2_label.pack(side=tk.LEFT, padx=5)

        self.team2_prob_var = tk.StringVar(value="N/A")
        self.team2_prob_label = tk.Label(team2_prob_frame,
                                         textvariable=self.team2_prob_var,
                                         font=self.subtitle_font,
                                         fg=self.valorant_white, bg=self.valorant_blue)
        self.team2_prob_label.pack(side=tk.RIGHT, padx=5)

        self.team2_bar = tk.Canvas(self.probability_frame, height=30, bg="#333333",
                                   highlightthickness=0)
        self.team2_bar.pack(fill=tk.X, padx=20, pady=5)

        # Round controls
        controls_frame = tk.Frame(self.prediction_tab, bg=self.valorant_blue)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        team1_win_btn = tk.Button(controls_frame, text="TEAM 1 WON ROUND",
                                  command=self.team1_won,
                                  bg=self.valorant_red, fg=self.valorant_white,
                                  font=self.subtitle_font,
                                  relief=tk.FLAT, padx=10, pady=5)
        team1_win_btn.pack(side=tk.LEFT, padx=10)

        team2_win_btn = tk.Button(controls_frame, text="TEAM 2 WON ROUND",
                                  command=self.team2_won,
                                  bg=self.valorant_red, fg=self.valorant_white,
                                  font=self.subtitle_font,
                                  relief=tk.FLAT, padx=10, pady=5)
        team2_win_btn.pack(side=tk.RIGHT, padx=10)

        reset_btn = tk.Button(controls_frame, text="RESET MATCH",
                              command=self.reset_match,
                              bg="#333333", fg=self.valorant_white,
                              font=self.subtitle_font,
                              relief=tk.FLAT, padx=10, pady=5)
        reset_btn.pack(side=tk.BOTTOM, pady=10)

    # Rest of methods remain unchanged
    def start_match(self):
        # Get selected agents for team 1
        self.team1_agents = [agent for agent, var in self.team1_vars.items() if var.get()]
        if not self.team1_agents:
            messagebox.showwarning("Warning", "Please select at least one agent for Team 1!")
            return
        if len(self.team1_agents) > 5:
            messagebox.showwarning("Warning", "Please select less than 6 agents for Team 1!")
            return

        # Get selected agents for team 2
        self.team2_agents = [agent for agent, var in self.team2_vars.items() if var.get()]
        if not self.team2_agents:
            messagebox.showwarning("Warning", "Please select at least one agent for Team 2!")
            return
        if len(self.team2_agents) > 5:
            messagebox.showwarning("Warning", "Please select less than 6 agents for Team 2!")
            return

        # Reset scores and round
        self.round_number = 1
        self.team1_score = 0
        self.team2_score = 0

        # Update UI
        self.update_score_display()

        # Make initial prediction
        self.make_prediction()

        # Switch to prediction tab
        self.notebook.select(self.prediction_tab)

    def update_score_display(self):
        self.round_label.config(text=f"Round: {self.round_number}")
        self.team1_score_label.config(text=f"Team 1: {self.team1_score}")
        self.team2_score_label.config(text=f"Team 2: {self.team2_score}")

    def make_prediction(self):
        # Format input data
        input_df = self.format_input(self.team1_agents, self.team2_agents,
                                     self.selected_map.get(),
                                     self.round_number,
                                     self.team1_score,
                                     self.team2_score)

        # Make prediction
        win_proba_team1 = self.rf_model.predict_proba(input_df)[0][1] * 100
        win_proba_team2 = 100 - win_proba_team1

        # Update UI with predictions
        self.team1_prob_var.set(f"{win_proba_team1:.2f}%")
        self.team2_prob_var.set(f"{win_proba_team2:.2f}%")

        # Update probability bars
        self.update_probability_bars(win_proba_team1, win_proba_team2)

    def update_probability_bars(self, team1_prob, team2_prob):
        bar_width = self.team1_bar.winfo_width()
        if bar_width <= 1:  # If not yet properly sized, wait a bit and retry
            self.after(100, lambda: self.update_probability_bars(team1_prob, team2_prob))
            return

        # Clear existing bars
        self.team1_bar.delete("all")
        self.team2_bar.delete("all")

        # Draw team 1 bar
        team1_width = int(bar_width * team1_prob / 100)
        self.team1_bar.create_rectangle(0, 0, team1_width, 30,
                                        fill=self.valorant_red, outline="")

        # Draw team 2 bar
        team2_width = int(bar_width * team2_prob / 100)
        self.team2_bar.create_rectangle(0, 0, team2_width, 30,
                                        fill=self.valorant_red, outline="")

    def team1_won(self):
        self.team1_score += 1
        self.round_number += 1
        self.update_score_display()
        self.make_prediction()

    def team2_won(self):
        self.team2_score += 1
        self.round_number += 1
        self.update_score_display()
        self.make_prediction()

    def reset_match(self):
        # Return to setup tab
        self.notebook.select(self.setup_tab)

    def format_input(self, team1_agents, team2_agents, map_to_predict, round_number, team1_score, team2_score):
        # One-hot encode agents for both teams
        team1_encoded = {f'team1_{agent}': 1 if agent in team1_agents else 0 for agent in self.all_agents}
        team2_encoded = {f'team2_{agent}': 1 if agent in team2_agents else 0 for agent in self.all_agents}

        # One-hot encode map
        map_encoded = {f"Map_{m}": 1 if m == map_to_predict else 0 for m in self.all_maps}

        # Combine into a single row
        input_row = {
            'RoundNumber': round_number,
            'Team1_RoundScore': team1_score,
            'Team2_RoundScore': team2_score,
            **team1_encoded,
            **team2_encoded,
            **map_encoded
        }

        # Convert to DataFrame and ensure correct column order
        input_df = pd.DataFrame([input_row])
        for col in self.expected_column_order:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[self.expected_column_order]
        return input_df


if __name__ == "__main__":
    app = ValorantMatchPredictor()
    app.mainloop()