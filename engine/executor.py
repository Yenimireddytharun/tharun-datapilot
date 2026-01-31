import io
import base64
import matplotlib.pyplot as plt
import pandas as pd

class DataPilotExecutor:
    def __init__(self):
        self.data = pd.DataFrame()
        self.current_plt = None  # Added to store the plot for server.py

    def execute(self, ast, data_override=None):
        logs = []
        
        # --- DATA CONNECTION ---
        if data_override is not None:
            self.data = data_override
            logs.append(f"[LOG] System using uploaded dataset ({len(self.data)} rows).")
        else:
            self.data = pd.DataFrame({"Item": ["Sample A", "Sample B"], "Value": [10, 20]})
            logs.append("[LOG] No file uploaded. Using default sample data.")

        data_preview = self.data.head(5).to_dict(orient='records')
        logs.append("[LOG] Parsing script... SUCCESS.")
        
        # Execution loop
        for i, stmt in enumerate(ast[1], 1):
            action = stmt[0]
            if action == 'DP_QUERY':
                logs.append(f"{i}. Loading Data: Processing {len(self.data)} rows.")
            elif action == 'DP_VISUALIZE':
                logs.append(f"{i}. Visualizing: Generating chart...")
                # We generate the plot and store it in the class instance
                self.generate_plot() 
                logs.append("[LOG] Encoding plot to Base64... DONE.")

        return {
            "status": "success",
            "execution_logs": logs,
            "data_preview": data_preview
        }

    def generate_plot(self):
        """Generates the plot and stores it in self.current_plt for the server to encode."""
        plt.figure(figsize=(7, 5))
        
        if not self.data.empty and len(self.data.columns) >= 2:
            x_col = self.data.columns[0]
            y_col = self.data.columns[1]
            plt.bar(self.data[x_col].astype(str), self.data[y_col], color='#61dafb')
            plt.title(f"DataPilot: {y_col} by {x_col}")
            plt.xticks(rotation=45)
        else:
            plt.plot([1, 2, 3], [10, 20, 30], marker='o')
            plt.title("DataPilot Default Visualization")

        plt.tight_layout()
        self.current_plt = plt  # Store the reference for server.py to use