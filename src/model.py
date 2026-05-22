# model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

class AnomalyModel:
    def __init__(self):
        self.scaler = StandardScaler()

    def train_and_evaluate(self, df, model_type="Isolation Forest", params=None):
        """
        Tränar vald modell med dynamisk kolumnvalidering och statistisk utvärdering.
        """
        # 1. Dynamisk identifiering av målvariabel och features
        # Känner av om filen använder 'anomaly' (ny fil) eller 'is_anomaly' (gammal fil)
        target_col = 'anomaly' if 'anomaly' in df.columns else 'is_anomaly'
        y_true = df[target_col]

        # Välj alla numeriska kolumner som features (men exkludera målvariabeln)
        features = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in features: features.remove(target_col)
        
        # Exkludera ID-liknande kolumner som inte ska påverka träningen
        for col_to_remove in ['Alarm_ID', 'alarm_id', 'staff_present', 'double_alarm']:
            if col_to_remove in features: features.remove(col_to_remove)
            
        X_raw = df[features]

        # 2. Scaling (Standardisering)
        # Detta gör att t.ex. 'response_time' och 'door_open_time' kan jämföras rättvist
        X_scaled = self.scaler.fit_transform(X_raw)

        # 3. Modellval
        if model_type == "Isolation Forest":
            clf = IsolationForest(
                contamination=params.get('contamination', 0.1), 
                random_state=42
            )
        else:
            clf = OneClassSVM(
                nu=params.get('nu', 0.1), 
                kernel="rbf", 
                gamma=params.get('gamma', 0.1)
            )

        # 4. Träning och prediktion
        clf.fit(X_scaled)
        # scores: Ju lägre värde, desto mer avvikande (anomalt)
        scores = clf.decision_function(X_scaled) 
        preds = clf.predict(X_scaled)
        y_pred = np.where(preds == -1, 1, 0)

        # 5. Skapa resultat-DataFrame
        df_results = df.copy()
        df_results['Predicted_Anomaly'] = y_pred
        df_results['Anomaly_Score'] = scores
        
        # 6. Statistisk "Main Factor" via Z-Score
        # Vi räknar ut vilken feature som avviker mest från normalvärdet (Z-score)
        normal_data = X_raw[y_true == 0]
        means = normal_data.mean()
        stds = normal_data.std() + 1e-6 # Undvik division med noll

        def get_main_factor(row):
            # Beräkna Z-score för alla features och välj den högsta
            z_scores = {feat: abs(row[feat] - means[feat]) / stds[feat] for feat in features}
            return max(z_scores, key=z_scores.get)

        df_results['Main_Factor'] = df_results.apply(get_main_factor, axis=1)
        
        # 7. Beräkna mätetal (KPIs för examensarbetet)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        metrics = {
            "Vald Modell": model_type,
            "F1-Score": f1_score(y_true, y_pred),
            "Accuracy": accuracy_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred),
            "Recall": recall_score(y_true, y_pred),
            "---": "---",
            "True Positives (TP)": tp,
            "False Positives (FP)": fp,
            "True Negatives (TN)": tn,
            "False Negatives (FN)": fn,
            "Antal Anomalier": np.sum(y_pred)
        }
        
        return df_results[y_pred == 1].copy(), metrics, df_results