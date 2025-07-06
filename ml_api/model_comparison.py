import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import json
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class ModelComparison:
    def __init__(self):
        """Initialise la classe de comparaison des modèles"""
        self.algorithms = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'Decision Tree': DecisionTreeRegressor(
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=3,
                random_state=42
            )
        }
        self.results = {}
        self.best_models = {}

    def prepare_data(self, X, y, test_size=0.2, scale_features=False):
        """Prépare les données pour l'entraînement"""
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Normalisation optionnelle (recommandée pour certains algorithmes)
        if scale_features:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            return X_train_scaled, X_test_scaled, y_train, y_test, scaler

        return X_train, X_test, y_train, y_test, None

    def evaluate_model(self, model, X_train, X_test, y_train, y_test, model_name):
        """Évalue un modèle et retourne les métriques"""
        # Entraînement
        model.fit(X_train, y_train)

        # Prédictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        # Métriques sur l'ensemble de test
        mse = mean_squared_error(y_test, y_pred_test)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred_test)
        r2 = r2_score(y_test, y_pred_test)

        # Métriques sur l'ensemble d'entraînement (pour détecter l'overfitting)
        mse_train = mean_squared_error(y_train, y_pred_train)
        r2_train = r2_score(y_train, y_pred_train)

        # Validation croisée
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')

        metrics = {
            'model_name': model_name,
            'test_mse': mse,
            'test_rmse': rmse,
            'test_mae': mae,
            'test_r2': r2,
            'train_r2': r2_train,
            'cv_mean_r2': cv_scores.mean(),
            'cv_std_r2': cv_scores.std(),
            'overfitting_indicator': r2_train - r2  # Si > 0.1, possible overfitting
        }

        return metrics, model

    def compare_algorithms(self, X, y, model_type_name="Generic"):
        """Compare tous les algorithmes sur un jeu de données"""
        print(f"\n🔍 Comparaison des algorithmes pour : {model_type_name}")
        print("=" * 60)

        X_train, X_test, y_train, y_test, scaler = self.prepare_data(X, y)

        comparison_results = {}

        for name, algorithm in self.algorithms.items():
            print(f"\n📊 Entraînement de {name}...")

            try:
                metrics, trained_model = self.evaluate_model(
                    algorithm, X_train, X_test, y_train, y_test, name
                )

                comparison_results[name] = {
                    'metrics': metrics,
                    'model': trained_model,
                    'scaler': scaler
                }

                # Affichage des résultats
                print(f"   R² Score: {metrics['test_r2']:.4f}")
                print(f"   RMSE: {metrics['test_rmse']:.4f}")
                print(f"   MAE: {metrics['test_mae']:.4f}")
                print(f"   CV R² (moyenne): {metrics['cv_mean_r2']:.4f} (±{metrics['cv_std_r2']:.4f})")

                if metrics['overfitting_indicator'] > 0.1:
                    print(f"   ⚠️  Possible overfitting détecté!")

            except Exception as e:
                print(f"   ❌ Erreur lors de l'entraînement: {str(e)}")
                continue

        # Trouver le meilleur modèle
        if comparison_results:
            best_model_name = max(comparison_results.keys(),
                                  key=lambda x: comparison_results[x]['metrics']['test_r2'])

            print(f"\n🏆 Meilleur modèle: {best_model_name}")
            print(f"   R² Score: {comparison_results[best_model_name]['metrics']['test_r2']:.4f}")

            self.results[model_type_name] = comparison_results
            self.best_models[model_type_name] = {
                'name': best_model_name,
                'model': comparison_results[best_model_name]['model'],
                'metrics': comparison_results[best_model_name]['metrics']
            }

            return comparison_results

        return None

    def save_best_model(self, model_type_name, save_path):
        """Sauvegarde le meilleur modèle"""
        if model_type_name in self.best_models:
            best_model = self.best_models[model_type_name]['model']
            joblib.dump(best_model, save_path)
            print(f"💾 Meilleur modèle sauvegardé: {save_path}")

            # Sauvegarde aussi les métriques
            metrics_path = save_path.replace('.joblib', '_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(self.best_models[model_type_name]['metrics'], f, indent=2)

            return True
        return False

    def generate_comparison_report(self):
        """Génère un rapport de comparaison détaillé"""
        if not self.results:
            print("❌ Aucun résultat à rapporter")
            return

        print("\n" + "=" * 80)
        print("📈 RAPPORT DE COMPARAISON DES MODÈLES")
        print("=" * 80)

        for model_type, results in self.results.items():
            print(f"\n🎯 {model_type.upper()}")
            print("-" * 40)

            # Tableau des résultats
            print(f"{'Algorithme':<20} {'R² Score':<10} {'RMSE':<10} {'MAE':<10} {'CV R²':<10}")
            print("-" * 70)

            for algo_name, result in results.items():
                metrics = result['metrics']
                print(f"{algo_name:<20} {metrics['test_r2']:<10.4f} {metrics['test_rmse']:<10.4f} "
                      f"{metrics['test_mae']:<10.4f} {metrics['cv_mean_r2']:<10.4f}")

            # Recommandations
            best = self.best_models[model_type]
            print(f"\n✅ Recommandation: {best['name']}")

            if best['metrics']['overfitting_indicator'] > 0.1:
                print("⚠️  Attention: Possible overfitting détecté")

            if best['metrics']['test_r2'] < 0.5:
                print("⚠️  Attention: Score R² faible - considérer plus de features")


# Exemple d'utilisation
def example_usage():
    """Exemple d'utilisation de la classe ModelComparison"""

    # Données d'exemple (remplacez par vos vraies données)
    X_example = np.random.rand(1000, 4)  # 4 features
    y_example = np.random.rand(1000)  # Target

    # Initialisation
    comparator = ModelComparison()

    # Comparaison des algorithmes
    results = comparator.compare_algorithms(X_example, y_example, "New Cases")

    # Sauvegarde du meilleur modèle
    comparator.save_best_model("New Cases", "models/best_new_cases_model.joblib")

    # Génération du rapport
    comparator.generate_comparison_report()


if __name__ == "__main__":
    example_usage()