# main.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from model import AnomalyModel
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Alarm Anomaly Detector - Examensarbete")
        self.root.geometry("1200x900")
        
        self.model = AnomalyModel()
        self.data = None
        self.full_df = None

        # --- Layout ---
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, fill="x")
        
        tk.Button(top_frame, text="1. Ladda CSV", command=self.load_data, bg="#3498db", fg="white", width=12).pack(side="left", padx=10)
        
        tk.Label(top_frame, text="Modell:").pack(side="left", padx=5)
        self.model_var = tk.StringVar(value="Isolation Forest")
        self.model_var.trace("w", self.create_param_ui)
        tk.OptionMenu(top_frame, self.model_var, "Isolation Forest", "One-Class SVM").pack(side="left", padx=5)

        self.run_btn = tk.Button(top_frame, text="2. Kör Analys", command=self.run_model, state="disabled", bg="#2ecc71", fg="white", width=12)
        self.run_btn.pack(side="left", padx=10)
        
        tk.Button(top_frame, text="3. Exportera", command=self.export_results, bg="#95a5a6", width=10).pack(side="left", padx=10)
        
        self.file_label = tk.Label(top_frame, text="Ingen fil laddad", fg="gray")
        self.file_label.pack(side="left", padx=10)

        # Parameter Panel
        self.param_frame = tk.LabelFrame(root, text="Modellinställningar & Känslighet", padx=10, pady=10)
        self.param_frame.pack(fill="x", padx=10, pady=5)
        
        self.controls_subframe = tk.Frame(self.param_frame)
        self.controls_subframe.pack(fill="x")
        self.create_param_ui()

        tk.Label(self.param_frame, text="Manuell tröskeljustering (Threshold Tuning):").pack(anchor="w", pady=(10,0))
        self.threshold_slider = tk.Scale(self.param_frame, from_=-0.5, to=0.5, resolution=0.01, orient="horizontal", command=self.update_by_threshold)
        self.threshold_slider.set(0.0) 
        self.threshold_slider.pack(fill="x")

        # Tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.stats_tab = ttk.Frame(self.notebook)
        self.anomaly_tab = ttk.Frame(self.notebook)
        self.graph_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.stats_tab, text="Resultat & KPI")
        self.notebook.add(self.anomaly_tab, text="Detekterade Avvikelser")
        self.notebook.add(self.graph_tab, text="Visualisering")

        # Setup Trees
        self.stats_tree = ttk.Treeview(self.stats_tab, columns=("Metric", "Value"), show='headings')
        self.stats_tree.heading("Metric", text="Mätetal"); self.stats_tree.heading("Value", text="Värde")
        self.stats_tree.pack(expand=True, fill="both")

        self.anomaly_tree = ttk.Treeview(self.anomaly_tab, columns=("Time", "ID", "Value", "Factor"), show='headings')
        for col in ("Time", "ID", "Value", "Factor"): self.anomaly_tree.heading(col, text=col)
        self.anomaly_tree.pack(side="left", expand=True, fill="both")
        self.anomaly_tree.bind("<<TreeviewSelect>>", self.show_detail_view)

        self.detail_box = tk.Text(self.anomaly_tab, width=45, bg="#f8f9fa", font=("Arial", 10), padx=10, pady=10)
        self.detail_box.pack(side="right", fill="y", padx=5)

    def create_param_ui(self, *args):
        for widget in self.controls_subframe.winfo_children(): widget.destroy()
        if self.model_var.get() == "Isolation Forest":
            tk.Label(self.controls_subframe, text="Contamination (0.0-0.5):").grid(row=0, column=0)
            self.contam_entry = tk.Entry(self.controls_subframe); self.contam_entry.insert(0, "0.1"); self.contam_entry.grid(row=0, column=1)
        else:
            tk.Label(self.controls_subframe, text="Nu:").grid(row=0, column=0)
            self.nu_entry = tk.Entry(self.controls_subframe); self.nu_entry.insert(0, "0.1"); self.nu_entry.grid(row=0, column=1)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.data = pd.read_csv(file_path)
            self.file_label.config(text=f"Laddad: {os.path.basename(file_path)}", fg="green")
            self.run_btn.config(state="normal")

    def run_model(self):
        try:
            params = {'contamination': float(self.contam_entry.get())} if self.model_var.get() == "Isolation Forest" else {'nu': float(self.nu_entry.get())}
            _, metrics, self.full_df = self.model.train_and_evaluate(self.data, self.model_var.get(), params)
            self.refresh_ui()
            messagebox.showinfo("Framgång", "Analys genomförd med dynamisk kolumnanpassning!")
        except Exception as e:
            messagebox.showerror("Fel", f"Kunde inte köra modellen: {str(e)}")

    def update_by_threshold(self, val):
        if self.full_df is not None:
            self.full_df['Predicted_Anomaly'] = np.where(self.full_df['Anomaly_Score'] < float(val), 1, 0)
            self.refresh_ui()

    def refresh_ui(self):
        # Dynamisk mappning för visning i GUI
        t_col = 'timestamp' if 'timestamp' in self.full_df.columns else 'Timestamp'
        id_col = 'alarm_type' if 'alarm_type' in self.full_df.columns else 'Alarm_ID'
        v_col = 'response_time' if 'response_time' in self.full_df.columns else 'Value'
        target = 'anomaly' if 'anomaly' in self.full_df.columns else 'is_anomaly'

        y_true = self.full_df[target]
        y_pred = self.full_df['Predicted_Anomaly']
        
        # Mätetal
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        metrics = {
            "Accuracy": accuracy_score(y_true, y_pred),
            "F1-Score": f1_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred),
            "Recall": recall_score(y_true, y_pred),
            "---": "---",
            "True Positives (Hittade fel)": tp,
            "False Positives (Falsklarm)": fp
        }

        for i in self.stats_tree.get_children(): self.stats_tree.delete(i)
        for m, v in metrics.items():
            val = f"{v:.4f}" if isinstance(v, float) else v
            self.stats_tree.insert("", "end", values=(m, val))

        for i in self.anomaly_tree.get_children(): self.anomaly_tree.delete(i)
        anoms = self.full_df[self.full_df['Predicted_Anomaly'] == 1]
        for _, row in anoms.head(100).iterrows():
            self.anomaly_tree.insert("", "end", values=(row[t_col], row[id_col], round(row[v_col], 2), row['Main_Factor']))

        self.plot_graph(self.full_df, {"TP": tp, "FP": fp, "TN": tn, "FN": fn}, v_col)

    def show_detail_view(self, event):
        selected = self.anomaly_tree.focus()
        if not selected: return
        vals = self.anomaly_tree.item(selected)['values']
        self.detail_box.delete("1.0", tk.END)
        self.detail_box.insert("1.0", f"--- DJUPANALYS ---\n\nID: {vals[1]}\nTid: {vals[0]}\n\n"
                                      f"Huvudorsak: {vals[3]}\n\nFörklaring:\n"
                                      f"Detta larm avviker mest i kolumnen '{vals[3]}'. "
                                      f"Värdet ligger statistiskt sett utanför det normala "
                                      f"intervallet baserat på träningsdatan.")

    def plot_graph(self, df, cm_data, v_col):
        plt.close('all')
        for widget in self.graph_tab.winfo_children(): widget.destroy()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        anom = df[df['Predicted_Anomaly'] == 1]
        norm = df[df['Predicted_Anomaly'] == 0]
        ax1.scatter(norm.index, norm[v_col], c='#3498db', alpha=0.3, s=10, label="Normal")
        ax1.scatter(anom.index, anom[v_col], c='#e74c3c', s=25, label="Anomali")
        ax1.set_title(f"Spridning: {v_col}")
        ax1.legend()

        ax2.bar(['TP', 'FP', 'TN', 'FN'], [cm_data['TP'], cm_data['FP'], cm_data['TN'], cm_data['FN']], color=['#2ecc71','#f39c12','#34495e','#e74c3c'])
        ax2.set_title("Confusion Matrix")

        canvas = FigureCanvasTkAgg(fig, master=self.graph_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def export_results(self):
        if self.full_df is not None:
            path = filedialog.asksaveasfilename(defaultextension=".csv")
            if path: self.full_df[self.full_df['Predicted_Anomaly'] == 1].to_csv(path, index=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()