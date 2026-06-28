import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (accuracy_score, mean_squared_error, precision_score,
                              recall_score, f1_score, confusion_matrix, r2_score,
                              silhouette_score)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
try:
    from xgboost import XGBClassifier, XGBRegressor
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False

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

        def log(msg):
            logs.append(msg)

        MODEL_KEYWORDS = ['rf', 'dt', 'gb', 'lr', 'xgb', 'auto', 'cluster']

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
                arg2 = stmt[2] if len(stmt) > 2 and stmt[2] and stmt[2] != 'all' else None
                arg3 = stmt[3] if len(stmt) > 3 and stmt[3] and stmt[3] != 'all' else 'auto'
                if arg2 and arg2.lower() in MODEL_KEYWORDS:
                    target_col = None
                    model_type = arg2.lower()
                else:
                    target_col = arg2
                    model_type = arg3 if arg3 else 'auto'
                logs.append(f"{i}. Training ML model...")
                if target_col is None:
                    target_col = self.data.columns[-1]
                    logs.append(f"[LOG] No target given. Using last column: '{target_col}'")
                logs.append(f"[ML] Selected model type: {model_type}")
                result = self.train_model(target_col, model_type=model_type)
                if result.get('task') == 'error':
                    logs.append(f"[ERROR] {result['error']}")
                else:
                    logs.append(f"[ML] Task detected: {result['task']}")
                    logs.append(f"[ML] Algorithm used: {result['algorithm']}")
                    logs.append(f"[ML] Training samples: {result['train_size']}, Test samples: {result['test_size']}")
                    logs.append(f"[ML] {result['metric'].upper()}: {result['score']}")
                    if result['task'] == 'classification':
                        logs.append(f"[ML] Precision: {result['precision']}")
                        logs.append(f"[ML] Recall: {result['recall']}")
                        logs.append(f"[ML] F1 Score: {result['f1']}")
                        logs.append(f"[ML] Cross-Val Score (5-fold): {result['cv_score']}")
                        logs.append(f"[ML] Classes: {result['classes']}")
                    elif result['task'] == 'regression':
                        logs.append(f"[ML] R2 Score: {result['r2']}")
                        logs.append(f"[ML] Cross-Val RMSE (5-fold): {result['cv_score']}")
                    elif result['task'] == 'clustering':
                        logs.append(f"[ML] Clusters: {result['n_clusters']}")
                        logs.append(f"[ML] Silhouette Score: {result['silhouette']}")
                    logs.append(f"[ML] Features used: {result['features']}")
                    logs.append(f"[ML] Feature count: {len(result['features'])}")
                    logs.append("[ML] Model training COMPLETE.")
                    self.last_metrics = {
                        'Task': result['task'],
                        'Algorithm': result['algorithm'],
                        result['metric'].upper(): str(result['score']),
                        'Features': str(len(result['features']))
                    }
                    if result['task'] == 'classification':
                        self.last_metrics['Precision'] = str(result['precision'])
                        self.last_metrics['Recall'] = str(result['recall'])
                        self.last_metrics['F1'] = str(result['f1'])
                        self.last_metrics['CV Score'] = str(result['cv_score'])
                    elif result['task'] == 'regression':
                        self.last_metrics['R2'] = str(result['r2'])
                        self.last_metrics['CV RMSE'] = str(result['cv_score'])
                    self.generate_ml_dashboard(result)

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

            elif action == 'DP_KAGGLE':
                dataset_slug = stmt[2] if len(stmt) > 2 and stmt[2] and stmt[2] != 'all' else None
                logs.append(f"{i}. Importing Kaggle Dataset...")
                if not dataset_slug:
                    logs.append("[ERROR] No dataset slug provided. Use format: username/dataset-name")
                else:
                    try:
                        from engine.kaggle_loader import download_kaggle_dataset, summarize_dataset
                        path = download_kaggle_dataset(dataset_slug)
                        self.data = pd.read_csv(path)
                        summary = summarize_dataset(self.data)
                        logs.append(f"[KAGGLE] Downloaded: {dataset_slug}")
                        logs.append(f"[KAGGLE] Rows: {summary['rows']}, Columns: {summary['columns']}")
                        logs.append(f"[KAGGLE] Column Names: {summary['column_names']}")
                        missing = {k: v for k, v in summary['missing_values'].items() if v > 0}
                        if missing:
                            logs.append(f"[KAGGLE] Missing Values: {missing}")
                        else:
                            logs.append(f"[KAGGLE] No missing values detected.")
                        for col, stats in summary['numeric_stats'].items():
                            logs.append(f"[KAGGLE] {col} → mean={stats['mean']}, min={stats['min']}, max={stats['max']}, std={stats['std']}")
                        for col, stats in summary['categorical_stats'].items():
                            logs.append(f"[KAGGLE] {col} → {stats['unique_values']} unique values, top: {list(stats['top_values'].keys())[:3]}")
                        logs.append(f"[KAGGLE] Dataset ready. Now use DP.Extract, DP.Train, DP.Report.")
                        data_preview = self.data.head(5).to_dict(orient='records')
                        self.last_table = self.data.head(20).to_dict(orient='records')
                    except Exception as e:
                        logs.append(f"[ERROR] Kaggle import failed: {str(e)}")

            elif action == 'DP_EXTRACT':
                col_arg = stmt[2] if len(stmt) > 2 and stmt[2] and stmt[2] != 'all' else None
                logs.append(f"{i}. Extracting subset from dataset...")
                try:
                    original_len = len(self.data)
                    result_df = self.data.copy()
                    if col_arg:
                        matched_cols = [c for c in self.data.columns if c.strip().lower() == col_arg.strip().lower()]
                        if matched_cols:
                            result_df = self.data[matched_cols]
                            logs.append(f"[EXTRACT] Column selected: {matched_cols}")
                        else:
                            try:
                                result_df = self.data.query(col_arg)
                                logs.append(f"[EXTRACT] Condition applied: {col_arg}")
                            except:
                                logs.append(f"[EXTRACT] '{col_arg}' not found. Using full dataset.")
                    self.data = result_df
                    logs.append(f"[EXTRACT] Original rows: {original_len}")
                    logs.append(f"[EXTRACT] Extracted rows: {len(self.data)}")
                    logs.append(f"[EXTRACT] Columns kept: {list(self.data.columns)}")
                    logs.append(f"[EXTRACT] Subset ready for SQL, ML and BI operations.")
                    data_preview = self.data.head(5).to_dict(orient='records')
                    self.last_table = self.data.head(20).to_dict(orient='records')
                except Exception as e:
                    logs.append(f"[ERROR] Extract failed: {str(e)}")

            elif action == 'DP_SQLCREATE':
                sql_code = stmt[2] if len(stmt) > 2 and stmt[2] and stmt[2] != 'all' else None
                logs.append(f"{i}. Creating dataset using SQL...")
                if not sql_code:
                    logs.append("[ERROR] No SQL provided.")
                else:
                    try:
                        from engine.sql_dataset_creator import create_table_from_sql, get_table_properties
                        result = create_table_from_sql(sql_code)
                        for log_line in result['logs']:
                            logs.append(log_line)
                        if result['tables']:
                            first_table = list(result['tables'].keys())[0]
                            self.data = result['tables'][first_table]['dataframe']
                            props = get_table_properties(self.data, first_table)
                            logs.append(f"[SQLCREATE] Table '{first_table}' loaded into DataPilot.")
                            logs.append(f"[SQLCREATE] Rows: {props['total_rows']}, Columns: {props['total_columns']}")
                            for col in props['columns']:
                                logs.append(f"[SQLCREATE] Column '{col['name']}' → dtype={col['dtype']}, unique={col['unique_count']}, nullable={col['nullable']}")
                                if 'min' in col:
                                    logs.append(f"[SQLCREATE]   Stats → min={col['min']}, max={col['max']}, mean={col['mean']}")
                            logs.append(f"[SQLCREATE] Table ready for ML and BI.")
                            data_preview = self.data.head(5).to_dict(orient='records')
                            self.last_table = self.data.head(20).to_dict(orient='records')
                        elif 'query_result' in result:
                            self.data = result['query_result']
                            logs.append(f"[SQLCREATE] Query result: {len(self.data)} rows returned.")
                            self.last_table = self.data.head(20).to_dict(orient='records')
                    except Exception as e:
                        logs.append(f"[ERROR] SQLCreate failed: {str(e)}")

            elif action == 'DP_SUMMARIZE':
                logs.append(f"{i}. Generating full dataset summary...")
                try:
                    from engine.kaggle_loader import summarize_dataset
                    summary = summarize_dataset(self.data)
                    logs.append(f"[SUMMARY] Rows: {summary['rows']}, Columns: {summary['columns']}")
                    logs.append(f"[SUMMARY] Column Names: {summary['column_names']}")
                    missing = {k: v for k, v in summary['missing_values'].items() if v > 0}
                    if missing:
                        logs.append(f"[SUMMARY] Missing Values: {missing}")
                    else:
                        logs.append(f"[SUMMARY] No missing values found.")
                    logs.append(f"[SUMMARY] --- Numeric Column Statistics ---")
                    for col, stats in summary['numeric_stats'].items():
                        logs.append(f"[SUMMARY] {col}: min={stats['min']}, max={stats['max']}, mean={stats['mean']}, std={stats['std']}, median={stats['median']}")
                    logs.append(f"[SUMMARY] --- Categorical Column Statistics ---")
                    for col, stats in summary['categorical_stats'].items():
                        logs.append(f"[SUMMARY] {col}: {stats['unique_values']} unique values")
                        logs.append(f"[SUMMARY]   Top values: {list(stats['top_values'].keys())[:5]}")
                    logs.append(f"[SUMMARY] Summary complete.")
                except Exception as e:
                    logs.append(f"[ERROR] Summarize failed: {str(e)}")

        return {
            "status": "success",
            "execution_logs": logs,
            "data_preview": data_preview,
            "metrics": self.last_metrics,
            "table": self.last_table
        }

    def train_model(self, target, model_type='auto'):
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
                'algorithm': 'none', 'train_size': 0, 'test_size': 0,
                'precision': 'N/A', 'recall': 'N/A', 'f1': 'N/A',
                'cv_score': 'N/A', 'classes': [], 'r2': 'N/A',
                'n_clusters': 0, 'silhouette': 'N/A'
            }
        target = target_match
        X = df.drop(columns=[target])
        y = df[target]

        for col in X.select_dtypes(include='object').columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

        if model_type == 'cluster':
            task = 'clustering'
        elif y.dtype == object or y.nunique() <= 10:
            task = 'classification'
        else:
            task = 'regression'

        classes = []
        if y.dtype == object:
            le_y = LabelEncoder()
            y = le_y.fit_transform(y)
            classes = list(le_y.classes_)
        elif task == 'classification':
            classes = [str(c) for c in list(y.unique())]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        if task == 'clustering':
            n_clusters = min(5, max(2, len(df) // 10))
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            model.fit(X_scaled)
            labels = model.labels_
            try:
                sil = round(silhouette_score(X_scaled, labels), 4) if len(set(labels)) > 1 else 0.0
            except:
                sil = 0.0
            self.trained_model = model
            return {
                'model': model, 'task': 'clustering', 'metric': 'silhouette',
                'score': sil, 'features': list(X.columns), 'algorithm': 'KMeans',
                'train_size': len(df), 'test_size': 0,
                'precision': 'N/A', 'recall': 'N/A', 'f1': 'N/A',
                'cv_score': 'N/A', 'classes': [], 'r2': 'N/A',
                'n_clusters': n_clusters, 'silhouette': sil,
                'X': X, 'labels': labels
            }

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if task == 'classification':
            model_map = {
                'rf':  RandomForestClassifier(n_estimators=100, random_state=42),
                'xgb': XGBClassifier(random_state=42, eval_metric='logloss') if XGBOOST_AVAILABLE else RandomForestClassifier(n_estimators=100, random_state=42),
                'lr':  LogisticRegression(max_iter=1000, random_state=42),
                'dt':  DecisionTreeClassifier(random_state=42),
                'gb':  GradientBoostingClassifier(random_state=42),
            }
            algo_names = {
                'rf': 'Random Forest', 'xgb': 'XGBoost',
                'lr': 'Logistic Regression', 'dt': 'Decision Tree',
                'gb': 'Gradient Boosting'
            }
            if model_type == 'auto':
                best_score = -1
                best_key = 'rf'
                for key, m in model_map.items():
                    try:
                        cv_n = min(3, len(X_train))
                        if cv_n < 2:
                            break
                        scores = cross_val_score(m, X_train, y_train, cv=cv_n, scoring='accuracy')
                        if scores.mean() > best_score:
                            best_score = scores.mean()
                            best_key = key
                    except:
                        pass
                model = model_map[best_key]
                algorithm = f"Auto-selected: {algo_names[best_key]}"
            else:
                key = model_type.lower()
                model = model_map.get(key, model_map['rf'])
                algorithm = algo_names.get(key, 'Random Forest')

            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = round(accuracy_score(y_test, preds), 4)
            precision = round(precision_score(y_test, preds, average='weighted', zero_division=0), 4)
            recall = round(recall_score(y_test, preds, average='weighted', zero_division=0), 4)
            f1 = round(f1_score(y_test, preds, average='weighted', zero_division=0), 4)
            try:
                cv_n = min(5, len(X))
                cv = cross_val_score(model, X, y, cv=cv_n, scoring='accuracy')
                cv_score = round(cv.mean(), 4)
            except:
                cv_score = 'N/A'
            metric = 'accuracy'
            r2 = 'N/A'

        else:
            model_map = {
                'rf':  RandomForestRegressor(n_estimators=100, random_state=42),
                'xgb': XGBRegressor(random_state=42) if XGBOOST_AVAILABLE else RandomForestRegressor(n_estimators=100, random_state=42),
                'lr':  Ridge(),
                'dt':  DecisionTreeRegressor(random_state=42),
                'gb':  GradientBoostingRegressor(random_state=42),
            }
            algo_names = {
                'rf': 'Random Forest', 'xgb': 'XGBoost',
                'lr': 'Ridge Regression', 'dt': 'Decision Tree',
                'gb': 'Gradient Boosting'
            }
            if model_type == 'auto':
                best_score = float('inf')
                best_key = 'rf'
                for key, m in model_map.items():
                    try:
                        cv_n = min(3, len(X_train))
                        if cv_n < 2:
                            break
                        scores = cross_val_score(m, X_train, y_train, cv=cv_n, scoring='neg_mean_squared_error')
                        rmse = np.sqrt(-scores.mean())
                        if rmse < best_score:
                            best_score = rmse
                            best_key = key
                    except:
                        pass
                model = model_map[best_key]
                algorithm = f"Auto-selected: {algo_names[best_key]}"
            else:
                key = model_type.lower()
                model = model_map.get(key, model_map['rf'])
                algorithm = algo_names.get(key, 'Random Forest')

            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = round(np.sqrt(mean_squared_error(y_test, preds)), 4)
            r2 = round(r2_score(y_test, preds), 4)
            try:
                cv_n = min(5, len(X))
                cv = cross_val_score(model, X, y, cv=cv_n, scoring='neg_mean_squared_error')
                cv_score = round(np.sqrt(-cv.mean()), 4)
            except:
                cv_score = 'N/A'
            precision = recall = f1 = 'N/A'
            metric = 'rmse'

        self.trained_model = model
        return {
            'model': model, 'task': task, 'metric': metric, 'score': score,
            'features': list(X.columns), 'algorithm': algorithm,
            'train_size': len(X_train), 'test_size': len(X_test),
            'precision': precision, 'recall': recall, 'f1': f1,
            'cv_score': cv_score, 'classes': classes, 'r2': r2,
            'n_clusters': 0, 'silhouette': 'N/A',
            'X': X, 'y_test': y_test, 'preds': preds
        }

    def generate_ml_dashboard(self, result):
        try:
            task = result['task']
            fig = plt.figure(figsize=(14, 10))
            fig.patch.set_facecolor('#0f0f1a')
            gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)
            colors = ['#61dafb', '#ff6b6b', '#ffd93d', '#6bcb77', '#a855f7']

            ax1 = fig.add_subplot(gs[0, 0])
            ax1.set_facecolor('#1a1a2e')
            if hasattr(result.get('model'), 'feature_importances_'):
                features = result['features']
                importance = result['model'].feature_importances_
                sorted_idx = np.argsort(importance)
                ax1.barh([features[i] for i in sorted_idx], importance[sorted_idx], color='#61dafb')
                ax1.set_title("Feature Importance", color='white', fontsize=10)
                ax1.set_xlabel("Importance Score", color='white', fontsize=8)
            else:
                ax1.text(0.5, 0.5, 'Feature importance\nnot available', color='white',
                         ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title("Feature Importance", color='white', fontsize=10)
            ax1.tick_params(colors='white', labelsize=7)
            for spine in ax1.spines.values():
                spine.set_edgecolor('#333')

            ax2 = fig.add_subplot(gs[0, 1])
            ax2.set_facecolor('#1a1a2e')
            if task == 'classification' and 'y_test' in result and 'preds' in result:
                cm = confusion_matrix(result['y_test'], result['preds'])
                ax2.imshow(cm, cmap='Blues')
                ax2.set_title("Confusion Matrix", color='white', fontsize=10)
                ax2.tick_params(colors='white', labelsize=7)
                for row in range(cm.shape[0]):
                    for col in range(cm.shape[1]):
                        ax2.text(col, row, str(cm[row, col]), ha='center', va='center', color='white', fontsize=8)
            elif task == 'regression' and 'y_test' in result and 'preds' in result:
                ax2.scatter(result['y_test'], result['preds'], color='#ffd93d', alpha=0.7, s=50)
                mn = min(float(min(result['y_test'])), float(min(result['preds'])))
                mx = max(float(max(result['y_test'])), float(max(result['preds'])))
                ax2.plot([mn, mx], [mn, mx], color='#ff6b6b', linewidth=2)
                ax2.set_title("Actual vs Predicted", color='white', fontsize=10)
                ax2.set_xlabel("Actual", color='white', fontsize=8)
                ax2.set_ylabel("Predicted", color='white', fontsize=8)
                ax2.tick_params(colors='white', labelsize=7)
            elif task == 'clustering' and 'X' in result and 'labels' in result:
                X_plot = result['X']
                labels = result['labels']
                cols = list(X_plot.columns)
                if len(cols) >= 2:
                    ax2.scatter(X_plot[cols[0]], X_plot[cols[1]], c=labels, cmap='tab10', s=60, alpha=0.8)
                    ax2.set_title(f"Clusters: {cols[0]} vs {cols[1]}", color='white', fontsize=10)
                    ax2.set_xlabel(cols[0], color='white', fontsize=8)
                    ax2.set_ylabel(cols[1], color='white', fontsize=8)
                    ax2.tick_params(colors='white', labelsize=7)
            for spine in ax2.spines.values():
                spine.set_edgecolor('#333')

            ax3 = fig.add_subplot(gs[1, 0])
            ax3.set_facecolor('#1a1a2e')
            metrics_to_show = {}
            if task == 'classification':
                metrics_to_show = {
                    'Accuracy':  float(result['score']),
                    'Precision': float(result['precision']) if result['precision'] != 'N/A' else 0,
                    'Recall':    float(result['recall']) if result['recall'] != 'N/A' else 0,
                    'F1 Score':  float(result['f1']) if result['f1'] != 'N/A' else 0,
                }
            elif task == 'regression':
                metrics_to_show = {
                    'R2 Score': float(result['r2']) if result['r2'] != 'N/A' else 0,
                }
            if metrics_to_show:
                bars = ax3.bar(list(metrics_to_show.keys()), list(metrics_to_show.values()), color=colors[:len(metrics_to_show)])
                ax3.set_title("Model Metrics", color='white', fontsize=10)
                ax3.set_ylim(0, 1.2)
                ax3.tick_params(colors='white', labelsize=7, rotation=15)
                for bar, val in zip(bars, metrics_to_show.values()):
                    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                             f'{val:.3f}', ha='center', color='white', fontsize=8)
            else:
                ax3.text(0.5, 0.5, f"Silhouette: {result.get('silhouette', 'N/A')}",
                         color='white', ha='center', va='center', transform=ax3.transAxes, fontsize=12)
                ax3.set_title("Clustering Score", color='white', fontsize=10)
            for spine in ax3.spines.values():
                spine.set_edgecolor('#333')

            ax4 = fig.add_subplot(gs[1, 1])
            ax4.set_facecolor('#1a1a2e')
            ax4.axis('off')
            summary_lines = [
                f"Task:       {result['task'].upper()}",
                f"Algorithm:  {result['algorithm']}",
                f"Train Size: {result['train_size']}",
                f"Test Size:  {result['test_size']}",
                f"Features:   {len(result['features'])}",
                f"Score:      {result['score']}",
                f"CV Score:   {result['cv_score']}",
            ]
            if task == 'regression':
                summary_lines.append(f"R2:         {result['r2']}")
            for j, line in enumerate(summary_lines):
                ax4.text(0.05, 0.92 - j * 0.12, line,
                         color='#61dafb' if j == 0 else 'white',
                         transform=ax4.transAxes, fontsize=9,
                         fontweight='bold' if j == 0 else 'normal',
                         fontfamily='monospace')
            ax4.set_title("Model Summary", color='white', fontsize=10)
            for spine in ax4.spines.values():
                spine.set_edgecolor('#333')

            plt.suptitle(f'DataPilot — ML Dashboard ({result["algorithm"]})',
                         color='#61dafb', fontsize=13, fontweight='bold')
            self.current_plt = plt
        except Exception as e:
            print(f"ML dashboard error: {e}")

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
