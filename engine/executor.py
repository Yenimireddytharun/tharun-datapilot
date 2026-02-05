import matplotlib.pyplot as plt
import pandas as pd

class DataPilotExecutor:
    def __init__(self):
        self.data = pd.DataFrame()
        self.current_plt = None

    def execute(self, ast, data_override=None):
        logs = []

        if data_override is not None:
            self.data = data_override
            logs.append(f"[LOG] Using uploaded dataset ({len(self.data)} rows).")
        else:
            self.data = pd.DataFrame({"Item": ["A", "B"], "Value": [10, 20]})
            logs.append("[LOG] Using default dataset.")

        logs.append("[LOG] Parsing script... SUCCESS.")

        for i, stmt in enumerate(ast[1], 1):
            if stmt[0] == "DP_VISUALIZE":
                logs.append(f"{i}. Generating visualization...")
                self.generate_plot()

        return {"execution_logs": logs}

    def generate_plot(self):
        plt.figure(figsize=(7, 5))
        x, y = self.data.columns[:2]
        plt.bar(self.data[x].astype(str), self.data[y])
        plt.tight_layout()
        self.current_plt = plt