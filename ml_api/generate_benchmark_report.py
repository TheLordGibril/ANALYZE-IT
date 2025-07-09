import os
import json
from fpdf import FPDF

BENCHMARK_DIR = "benchmark"
OUTPUT_PDF = "../models_benchmark.pdf"


def get_best_model(metrics_dict):
    return max(metrics_dict.items(), key=lambda x: x[1].get("test_r2", float('-inf')))


def format_float(val):
    try:
        return f"{val:.4f}"
    except Exception:
        return str(val)


pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Rapport de benchmark des modèles IA", ln=True, align="C")
pdf.ln(10)

for filename in sorted(os.listdir(BENCHMARK_DIR)):
    if not filename.endswith(".json"):
        continue
    path = os.path.join(BENCHMARK_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        metrics_dict = json.load(f)
    cible = filename.replace("comparison_results_", "").replace(".json", "")
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Cible : {cible}", ln=True)
    pdf.set_font("Arial", "", 12)

    best_model, best_metrics = get_best_model(metrics_dict)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Modèle", 1)
    pdf.cell(25, 8, "R²", 1)
    pdf.cell(30, 8, "RMSE", 1)
    pdf.cell(30, 8, "MAE", 1)
    pdf.cell(30, 8, "CV R²", 1)
    pdf.cell(35, 8, "Overfitting", 1)
    pdf.ln()
    pdf.set_font("Arial", "", 11)
    for model, m in metrics_dict.items():
        is_best = (model == best_model)
        if is_best:
            pdf.set_text_color(0, 128, 0)
        else:
            pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 8, model, 1)
        pdf.cell(25, 8, format_float(m.get("test_r2")), 1)
        pdf.cell(30, 8, format_float(m.get("test_rmse")), 1)
        pdf.cell(30, 8, format_float(m.get("test_mae")), 1)
        pdf.cell(30, 8, format_float(m.get("cv_mean_r2")), 1)
        pdf.cell(35, 8, format_float(m.get("overfitting_indicator")), 1)
        pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(0, 128, 0)
    pdf.multi_cell(
        0, 8, f"Modèle retenu pour '{cible}' : {best_model} (R² = {format_float(best_metrics.get('test_r2'))})")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

pdf.output(OUTPUT_PDF)
print(f"✅ Rapport généré : {OUTPUT_PDF}")
