import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

    def execute(self, ast, data_override=None):
        logs = []

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
                logs.append("[LOG] Encoding plot to Base64... DONE.")

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
                    self.generate_feature_importance(result)

            elif action == 'DP_FILTER':
                condition = stmt[2] if len(stmt) > 2 and stmt[2] else None
                if condition:
                    try:
                        self.data = self.data.query(condition)
                        logs.append(f"{i}. Filter applied: {condition} → {len(self.data)} rows remaining.")
                    except Exception as e:
                        logs.append(f"[ERROR] Filter failed: {str(e)}")

        return {
            "status": "success",
            "execution_logs": logs,
            "data_preview": data_preview
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
                'error': f"Column '{target}' not found. Available columns: {actual_cols}",
                'metric': 'none',
                'score': 0,
                'features': [],
                'precision': 'N/A',
                'recall': 'N/A',
                'f1': 'N/A'
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
            'model': model,
            'task': task,
            'metric': metric,
            'score': score,
            'features': list(X.columns),
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def generate_feature_importance(self, result):
        try:
            model = result['model']
            features = result['features']
            importance = model.feature_importances_
            plt.figure(figsize=(7, 5))
            plt.barh(features, importance, color='#61dafb')
            plt.title("Feature Importance")
            plt.xlabel("Importance Score")
            plt.tight_layout()
            self.current_plt = plt
        except Exception as e:
            print(f"Feature importance error: {e}")

    def generate_plot(self, chart_type='bar_chart'):
        try:
            plt.figure(figsize=(7, 5))
            numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
            cat_cols = self.data.select_dtypes(include='object').columns.tolist()
            x_col = cat_cols[0] if cat_cols else self.data.columns[0]
            y_col = numeric_cols[0] if numeric_cols else self.data.columns[1]
            if chart_type == 'bar_chart':
                plt.bar(self.data[x_col].astype(str), self.data[y_col], color='#61dafb')
                plt.title(f"DataPilot: {y_col} by {x_col}")
                plt.xticks(rotation=45)
            elif chart_type == 'line_chart':
                plt.plot(self.data[x_col].astype(str), self.data[y_col], marker='o', color='#61dafb')
                plt.title(f"DataPilot: {y_col} trend")
                plt.xticks(rotation=45)
            elif chart_type == 'pie_chart':
                plt.pie(self.data[y_col], labels=self.data[x_col].astype(str), autopct='%1.1f%%')
                plt.title(f"DataPilot: {y_col} distribution")
            elif chart_type == 'scatter':
                if len(numeric_cols) >= 2:
                    plt.scatter(self.data[numeric_cols[0]], self.data[numeric_cols[1]], color='#61dafb')
                    plt.title(f"DataPilot: {numeric_cols[0]} vs {numeric_cols[1]}")
            plt.tight_layout()
            self.current_plt = plt
        except Exception as e:
            print(f"Plot error: {e}")