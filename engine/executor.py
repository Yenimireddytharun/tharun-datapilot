import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error, precision_score, recall_score, f1_score

class DataPilotExecutor:
    def __init__(self):
        self.data = pd.DataFrame()
        self.current_plt = None
        self.trained_model = None
        self.last_metrics = {}
        self.last_table = []

    def execute(self, ast, data_override=None):
        logs = []
        self.last_metrics = {}
        self.last_table = []
        self.current_plt = None

        if data_override is not None:
            self.data = data_override
            logs.append(f"[LOG] System using uploaded dataset ({len(self.data)} rows).")
        else:
            self.data = pd.DataFrame({"Item": ["Sample A", "Sample B"], "Value": [10, 20]})
            logs.append("[LOG] No file uploaded. Using default sample data.")

        data_preview = self.data.head(5).to_dict(orient='records')
        logs.append("[LOG] Parsing script... SUCCESS.")

        for i, stmt in enumerate(ast[1], 1):
            if stmt is None:
                continue
            action = stmt[0]

            if action == 'DP_QUERY':
                logs.append(f"{i}. Loading Data: Processing {len(self.data)} rows.")
                logs.append(f"[LOG] Columns: {list(self.data.columns)}")

            elif action == 'DP_DESCRIBE':
                logs.append(f"{i}. Dataset Info:")
                logs.append(f"[LOG] Rows: {len(self.data)}")
                logs.append(f"[LOG] Columns: {list(self.data.columns)}")
                for col in self.data.columns:
                    logs.append(f"[LOG] {col} → dtype: {self.data[col].dtype}, sample: {str(self.data[col].iloc[0])}")

            elif action == 'DP_VISUALIZE':
                chart_type = stmt[2] if len(stmt) > 2 and stmt[2] else 'bar_chart'
                logs.append(f"{i}. Visualizing: Generating {chart_type}...")
                self.generate_plot(chart_type)
                logs.append("[LOG] Chart generated. DONE.")

            elif action == 'DP_TRAIN':
                target_col = stmt[2] if len(stmt) > 2 and stmt[2] else None
                logs.append(f"{i}. Training ML model...")
                if target_col is None:
                    target_col = self.data.columns[-1]
                    logs.append(f"[LOG] No target given. Using last column: '{target_col}'")
                result = self.train_model(target_col)
                if result.get('task') == 'error':
                    logs.append(f"[ERROR] {result['error']}")
                else:
                    logs.append(f"[LOG] Task: {result['task']}")
                    logs.append(f"[LOG] {result['metric'].upper()}: {result['score']}")
                    if result['task'] == 'classification':
                        logs.append(f"[LOG] Precision: {result['precision']}")
                        logs.append(f"[LOG] Recall: {result['recall']}")
                        logs.append(f"[LOG] F1 Score: {result['f1']}")
                    logs.append(f"[LOG] Features: {result['features']}")
                    logs.append("[LOG] Model training COMPLETE.")
                    self.last_metrics = {
                        'Task': result['task'],
                        result['metric'].upper(): str(result['score']),
                        'Features': str(len(result['features']))
                    }
                    if result['task'] == 'classification':
                        self.last_metrics['Precision'] = str(result['precision'])
                        self.last_metrics['Recall'] = str(result['recall'])
                        self.last_metrics['F1'] = str(result['f1'])
                    self.generate_feature_importance(result)

            elif action == 'DP_FILTER':
                condition = stmt[2] if len(stmt) > 2 and stmt[2] else None
                if condition:
                    try:
                        self.data = self.data.query(condition)
                        logs.append(f"{i}. Filter applied: {condition} → {len(self.data)} rows remaining.")
                    except Exception as e:
                        logs.append(f"[ERROR] Filter failed: {str(e)}")

            elif action == 'DP_SQL':
                condition = stmt[2] if len(stmt) > 2 and stmt[2] else None
                logs.append(f"{i}. Executing SQL query...")
                try:
                    import duckdb
                    self.data.to_parquet('_temp_dp.parquet')
                    if condition and condition.lower() != 'all':
                        sql = f"SELECT * FROM read_parquet('_temp_dp.parquet') WHERE {condition}"
                    else:
                        sql = "SELECT * FROM read_parquet('_temp_dp.parquet')"
                    result_df = duckdb.query(sql).df()
                    self.data = result_df
                    logs.append(f"[SQL] Executed successfully.")
                    logs.append(f"[SQL] Result: {len(self.data)} rows returned.")
                    logs.append(f"[SQL] Columns: {list(self.data.columns)}")
                    self.last_table = self.data.head(20).to_dict(orient='records')
                except Exception as e:
                    logs.append(f"[ERROR] SQL failed: {str(e)}")

            elif action == 'DP_INSIGHT':
                logs.append(f"{i}. Generating AI Insights...")
                try:
                    numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
                    cat_cols = self.data.select_dtypes(include='object').columns.tolist()
                    logs.append(f"[AI] Dataset: {len(self.data)} rows, {len(self.data.columns)} columns.")
                    logs.append(f"[AI] Numeric columns: {numeric_cols}")
                    logs.append(f"[AI] Category columns: {cat_cols}")
                    for col in numeric_cols:
                        mean_val = round(self.data[col].mean(), 2)
                        max_val = self.data[col].max()
                        min_val = self.data[col].min()
                        std_val = round(self.data[col].std(), 2)
                        logs.append(f"[AI] {col} → Mean: {mean_val}, Max: {max_val}, Min: {min_val}, Std: {std_val}")
                    if numeric_cols and cat_cols:
                        top = self.data.groupby(cat_cols[0])[numeric_cols[0]].sum().idxmax()
                        top_val = self.data.groupby(cat_cols[0])[numeric_cols[0]].sum().max()
                        logs.append(f"[AI] Top performer in {cat_cols[0]}: {top} with {numeric_cols[0]} = {top_val}")
                        bottom = self.data.groupby(cat_cols[0])[numeric_cols[0]].sum().idxmin()
                        logs.append(f"[AI] Lowest performer: {bottom}")
                    logs.append("[AI] Insight generation COMPLETE.")
                except Exception as e:
                    logs.append(f"[ERROR] Insight failed: {str(e)}")

            elif action == 'DP_REPORT':
                logs.append(f"{i}. Generating PowerBI Dashboard...")
                try:
                    self.generate_powerbi_dashboard()
                    logs.append("[LOG] PowerBI Dashboard generated. DONE.")
                except Exception as e:
                    logs.append(f"[ERROR] Report failed: {str(e)}")

        return {
            "status": "success",
            "execution_logs": logs,
            "data_preview": data_preview,
            "metrics": self.last_metrics,
            "table": self.last_table
        }

    def train_model(self, target):
        df = self.data.copy().dropna()
        df.columns = df.columns.str.strip()
        actual_cols = list(df.columns)
        target_match = None
        for col in actual_cols:
            if col.strip().lower() == target.strip().lower():
                target_match = col
                break
        if target_match is None:
            return {
                'task': 'error',
                'error': f"Column '{target}' not found. Available: {actual_cols}",
                'metric': 'none', 'score': 0, 'features': [],
                'precision': 'N/A', 'recall': 'N/A', 'f1': 'N/A'
            }
        target = target_match
        X = df.drop(columns=[target])
        y = df[target]
        for col in X.select_dtypes(include='object').columns:
            X[col] = LabelEncoder().fit_transform(X[col].astype(str))
        task = 'classification' if y.dtype == object or y.nunique() <= 10 else 'regression'
        if y.dtype == object:
            y = LabelEncoder().fit_transform(y)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        if task == 'classification':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = round(accuracy_score(y_test, preds), 4)
            precision = round(precision_score(y_test, preds, average='weighted', zero_division=0), 4)
            recall = round(recall_score(y_test, preds, average='weighted', zero_division=0), 4)
            f1 = round(f1_score(y_test, preds, average='weighted', zero_division=0), 4)
            metric = 'accuracy'
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = round(np.sqrt(mean_squared_error(y_test, preds)), 4)
            precision = recall = f1 = 'N/A'
            metric = 'rmse'
        self.trained_model = model
        return {
            'model': model, 'task': task, 'metric': metric, 'score': score,
            'features': list(X.columns), 'precision': precision, 'recall': recall, 'f1': f1
        }

    def generate_feature_importance(self, result):
        try:
            model = result['model']
            features = result['features']
            importance = model.feature_importances_
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor('#0f0f1a')
            ax.set_facecolor('#1a1a2e')
            ax.barh(features, importance, color='#61dafb')
            ax.set_title("Feature Importance", color='white', fontsize=12)
            ax.set_xlabel("Importance Score", color='white')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#333')
            plt.tight_layout()
            self.current_plt = plt
        except Exception as e:
            print(f"Feature importance error: {e}")

    def generate_powerbi_dashboard(self):
        try:
            numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
            cat_cols = self.data.select_dtypes(include='object').columns.tolist()
            if not numeric_cols:
                return
            colors = ['#61dafb', '#ff6b6b', '#ffd93d', '#6bcb77', '#a855f7']
            fig = plt.figure(figsize=(14, 10))
            fig.patch.set_facecolor('#0f0f1a')
            gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.3)
            x_col = cat_cols[0] if cat_cols else None
            y_col = numeric_cols[0]

            ax1 = fig.add_subplot(gs[0, 0])
            ax1.set_facecolor('#1a1a2e')
            if x_col:
                ax1.bar(self.data[x_col].astype(str), self.data[y_col], color='#61dafb')
                ax1.set_title(f'{y_col} by {x_col}', color='white', fontsize=10)
                ax1.tick_params(colors='white', rotation=30)
            for spine in ax1.spines.values():
                spine.set_edgecolor('#333')

            ax2 = fig.add_subplot(gs[0, 1])
            ax2.set_facecolor('#1a1a2e')
            ax2.plot(range(len(self.data)), self.data[y_col], marker='o', color='#ff6b6b', linewidth=2)
            ax2.fill_between(range(len(self.data)), self.data[y_col], alpha=0.2, color='#ff6b6b')
            ax2.set_title(f'{y_col} Trend', color='white', fontsize=10)
            ax2.tick_params(colors='white')
            for spine in ax2.spines.values():
                spine.set_edgecolor('#333')

            ax3 = fig.add_subplot(gs[1, 0])
            ax3.set_facecolor('#1a1a2e')
            if x_col:
                ax3.pie(self.data[y_col], labels=self.data[x_col].astype(str), autopct='%1.1f%%', colors=colors)
            ax3.set_title(f'{y_col} Distribution', color='white', fontsize=10)

            ax4 = fig.add_subplot(gs[1, 1])
            ax4.set_facecolor('#1a1a2e')
            if len(numeric_cols) >= 2:
                ax4.scatter(self.data[numeric_cols[0]], self.data[numeric_cols[1]], color='#ffd93d', s=100, alpha=0.8)
                ax4.set_title(f'{numeric_cols[0]} vs {numeric_cols[1]}', color='white', fontsize=10)
                ax4.set_xlabel(numeric_cols[0], color='white')
                ax4.set_ylabel(numeric_cols[1], color='white')
            elif x_col:
                groups = self.data.groupby(x_col)[y_col].sum()
                ax4.barh(groups.index.astype(str), groups.values, color='#a855f7')
                ax4.set_title(f'Total {y_col} by {x_col}', color='white', fontsize=10)
            ax4.tick_params(colors='white')
            for spine in ax4.spines.values():
                spine.set_edgecolor('#333')

            plt.suptitle('DataPilot — PowerBI Dashboard', color='#61dafb', fontsize=14, fontweight='bold')
            self.current_plt = plt
        except Exception as e:
            print(f"PowerBI dashboard error: {e}")

    def generate_plot(self, chart_type='bar_chart'):
        try:
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#0f0f1a')
            ax.set_facecolor('#1a1a2e')
            numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
            cat_cols = self.data.select_dtypes(include='object').columns.tolist()
            x_col = cat_cols[0] if cat_cols else self.data.columns[0]
            y_col = numeric_cols[0] if numeric_cols else self.data.columns[1]
            if chart_type == 'bar_chart':
                ax.bar(self.data[x_col].astype(str), self.data[y_col], color='#61dafb')
                ax.set_title(f"DataPilot: {y_col} by {x_col}", color='white')
                ax.tick_params(colors='white', rotation=45)
            elif chart_type == 'line_chart':
                ax.plot(self.data[x_col].astype(str), self.data[y_col], marker='o', color='#ff6b6b', linewidth=2)
                ax.fill_between(range(len(self.data)), self.data[y_col], alpha=0.2, color='#ff6b6b')
                ax.set_title(f"DataPilot: {y_col} trend", color='white')
                ax.tick_params(colors='white', rotation=45)
            elif chart_type == 'pie_chart':
                ax.pie(self.data[y_col], labels=self.data[x_col].astype(str), autopct='%1.1f%%',
                       colors=['#61dafb','#ff6b6b','#ffd93d','#6bcb77','#a855f7'])
                ax.set_title(f"DataPilot: {y_col} distribution", color='white')
            elif chart_type == 'scatter':
                if len(numeric_cols) >= 2:
                    ax.scatter(self.data[numeric_cols[0]], self.data[numeric_cols[1]], color='#ffd93d', s=80)
                    ax.set_title(f"DataPilot: {numeric_cols[0]} vs {numeric_cols[1]}", color='white')
                ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#333')
            plt.tight_layout()
            self.current_plt = plt
        except Exception as e:
            print(f"Plot error: {e}")