# customer_segmentation.py
# Purpose: Perform customer segmentation using clustering algorithms.
#
# Phase 4.5 Note:
#   This class retains a legacy fit-predict path (perform_segmentation) used by
#   the legacy /segmentation API endpoint and by the unit test suite.
#
#   For production intelligence use, the FROZEN Phase 2 artifact is loaded via
#   load_frozen_artifact() and predictions are made via predict_with_frozen_artifact().
#   This is the canonical path going forward. The legacy path must not be invoked for
#   new customer intelligence lookups.

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.decomposition import PCA
import joblib
import pickle
import os
from typing import Dict, List, Tuple, Optional, Any
from backend.utils.logger import setup_logger
from backend.utils.config_loader import load_ml_config

# Canonical paths for the frozen Phase 2 segmentation artifacts
_FROZEN_SEG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "training", "experiments", "segmentation"
)
FROZEN_MODEL_PATH = os.path.join(_FROZEN_SEG_DIR, "segmentation_model.pkl")
FROZEN_SCALER_PATH = os.path.join(_FROZEN_SEG_DIR, "segmentation_scaler.pkl")
FROZEN_LABELS_PATH = os.path.join(_FROZEN_SEG_DIR, "cluster_labels.json")


class CustomerSegmentation:
    def __init__(self):
        # Step 1: Initialize segmentation model with configuration
        self.logger = setup_logger("CustomerSegmentation")
        self.config = load_ml_config()
        self.scaler = StandardScaler()
        self.model = None
        self.feature_columns = None
        self.segment_profiles = {}

        # Frozen Phase 2 artifact state (loaded via load_frozen_artifact)
        self._frozen_model = None
        self._frozen_scaler = None
        self._frozen_labels: Dict[int, str] = {}  # cluster_id -> segment_name
        self._frozen_artifact_loaded = False

    def prepare_features(self, customer_features_df: pd.DataFrame) -> pd.DataFrame:
        # Step 1: Select relevant features for clustering
        feature_columns = [
            'total_spent', 'avg_transaction_amount', 'transaction_count',
            'avg_monthly_spend', 'transaction_frequency', 'recency_days',
            'unique_merchants'
        ]

        # Step 2: Filter to only include available columns
        available_features = [col for col in feature_columns if col in customer_features_df.columns]
        self.feature_columns = available_features

        # Step 3: Create feature matrix
        feature_matrix = customer_features_df[available_features].copy()

        # Step 4: Handle missing values
        feature_matrix = feature_matrix.fillna(feature_matrix.median())

        # Step 5: Log transformation for skewed features
        skewed_features = ['total_spent', 'avg_transaction_amount', 'avg_monthly_spend']
        for feature in skewed_features:
            if feature in feature_matrix.columns:
                feature_matrix[feature] = np.log1p(feature_matrix[feature])

        self.logger.info(f"Prepared {len(available_features)} features for clustering")
        return feature_matrix

    def find_optimal_clusters(self, X: pd.DataFrame, max_clusters: int = 10) -> Dict[str, Any]:
        # Step 1: Scale the features
        X_scaled = self.scaler.fit_transform(X)

        # Step 2: Test different numbers of clusters
        cluster_range = range(2, max_clusters + 1)
        inertias = []
        silhouette_scores = []

        for n_clusters in cluster_range:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            inertias.append(kmeans.inertia_)
            sil_score = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(sil_score)

        # Step 3: Find optimal number using elbow + silhouette
        optimal_clusters = self._find_elbow_point(inertias, cluster_range)
        best_silhouette_idx = np.argmax(silhouette_scores)
        best_silhouette_clusters = cluster_range[best_silhouette_idx]
        optimal_n_clusters = min(optimal_clusters, best_silhouette_clusters)

        results = {
            'optimal_clusters': optimal_n_clusters,
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'cluster_range': list(cluster_range)
        }
        self.logger.info(f"Optimal number of clusters: {optimal_n_clusters}")
        return results

    def perform_segmentation(self, customer_features_df: pd.DataFrame, n_clusters: Optional[int] = None) -> pd.DataFrame:
        """Legacy fit-predict path. Used by the /segmentation API endpoint and unit tests.
        Do NOT call this for production customer intelligence — use predict_with_frozen_artifact().
        """
        # Step 1: Validate
        if customer_features_df is None or customer_features_df.empty:
            raise ValueError("customer_features_df must be a non-empty DataFrame")

        # Step 2: Prepare features for clustering
        feature_matrix = self.prepare_features(customer_features_df)
        if feature_matrix.shape[1] == 0:
            raise ValueError("No valid feature columns found in customer_features_df")

        # Step 3: Find optimal number of clusters if not specified
        if n_clusters is None:
            optimal_results = self.find_optimal_clusters(feature_matrix)
            n_clusters = optimal_results['optimal_clusters']

        # Step 4: Scale features
        X_scaled = self.scaler.fit_transform(feature_matrix)

        # Step 5: Perform clustering
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = self.model.fit_predict(X_scaled)

        # Step 6: Create segmentation results
        segmentation_results = customer_features_df.copy()
        segmentation_results['segment_id'] = cluster_labels

        # Step 7: Generate segment names and profiles
        segment_names = self._generate_segment_names(segmentation_results, n_clusters)
        segmentation_results['segment_name'] = segmentation_results['segment_id'].map(segment_names)

        # Step 8: Create segment profiles
        self.segment_profiles = self._create_segment_profiles(segmentation_results)

        # Add last_updated for API compatibility
        segmentation_results['last_updated'] = pd.Timestamp.now()
        self.logger.info(f"Completed segmentation with {n_clusters} clusters")
        return segmentation_results

    # ------------------------------------------------------------------
    # Backward-compatibility helpers expected by tests
    # ------------------------------------------------------------------

    def _prepare_features(self, customer_features_df: pd.DataFrame) -> np.ndarray:
        """Return scaled numpy array to align with tests."""
        features_df = self.prepare_features(customer_features_df)
        return self.scaler.fit_transform(features_df)

    def _engineer_features(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Basic feature engineering mirroring DataPreprocessor.create_customer_features."""
        df = transactions_df.copy()
        if 'merchant' not in df.columns:
            df['merchant'] = ''
        grouped = df.groupby('customer_id').agg({
            'amount': ['sum', 'mean', 'count'],
            'transaction_date': ['min', 'max'],
            'merchant': 'nunique'
        }).reset_index()
        grouped.columns = [
            'customer_id', 'total_spent', 'avg_transaction_amount', 'transaction_count',
            'first_transaction', 'last_transaction', 'unique_merchants'
        ]
        grouped['avg_monthly_spend'] = grouped['total_spent'] / (
            (pd.to_datetime(grouped['last_transaction']) - pd.to_datetime(grouped['first_transaction']))
            .dt.days.clip(lower=1) / 30
        )
        grouped['transaction_frequency'] = grouped['transaction_count'] / (
            (pd.to_datetime(grouped['last_transaction']) - pd.to_datetime(grouped['first_transaction']))
            .dt.days.clip(lower=1)
        )
        grouped['recency_days'] = (
            pd.Timestamp.now() - pd.to_datetime(grouped['last_transaction'])
        ).dt.days
        return grouped

    def _assign_segment_names(self, segments_df: pd.DataFrame, centers: np.ndarray) -> pd.DataFrame:
        """Assign names based on center heuristics."""
        names = {}
        for idx, center in enumerate(centers):
            total_spent, avg_tx, tx_count, avg_monthly, tx_freq, recency, unique_merchants = center
            spend_level = 'High Value' if total_spent >= np.max(centers[:, 0]) else (
                'Medium Value' if total_spent >= np.median(centers[:, 0]) else 'Low Value')
            freq_level = 'Frequent' if tx_freq >= np.median(centers[:, 4]) else 'Occasional'
            rec_level = 'Recent' if recency <= np.median(centers[:, 5]) else 'Inactive'
            names[idx] = f"{spend_level} - {freq_level} - {rec_level}"
        segments_df['segment_name'] = segments_df['segment_id'].map(names)
        return segments_df

    def _find_elbow_point(self, inertias: List[float], cluster_range: range) -> int:
        """Calculate the rate of change in inertia to find the elbow point."""
        inertia_changes = np.diff(inertias)
        inertia_change_rates = np.diff(inertia_changes)
        elbow_idx = np.argmax(inertia_change_rates) + 2  # +2 because of double diff
        return cluster_range[elbow_idx]

    def generate_segment_profiles(self, customer_features_df: pd.DataFrame, segments_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate segment profiles for test compatibility."""
        profiles = {}
        for segment_id in segments_df['segment_id'].unique():
            segment_data = segments_df[segments_df['segment_id'] == segment_id]
            segment_name = segment_data['segment_name'].iloc[0]
            profile = {
                'segment_id': segment_id,
                'segment_name': segment_name,
                'size': len(segment_data),
                'avg_total_spent': segment_data['total_spent'].mean(),
                'avg_transaction_count': segment_data['transaction_count'].mean(),
                'characteristics': {
                    'spending_pattern': 'high' if segment_data['total_spent'].mean() > 3000 else 'medium' if segment_data['total_spent'].mean() > 1500 else 'low',
                    'frequency': 'high' if segment_data['transaction_count'].mean() > 50 else 'medium' if segment_data['transaction_count'].mean() > 25 else 'low',
                    'recency': 'recent' if segment_data['recency_days'].mean() < 30 else 'moderate' if segment_data['recency_days'].mean() < 90 else 'inactive'
                }
            }
            profiles[segment_name] = profile
        return profiles

    def _find_silhouette_optimal(self, prepared_features) -> Dict[str, Any]:
        """Find optimal number of clusters using silhouette score."""
        best_score = -1
        best_k = 2
        scores = {}

        for k in range(2, min(11, len(prepared_features) // 2 + 1)):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(prepared_features)
                score = silhouette_score(prepared_features, cluster_labels)
                scores[k] = score
                if score > best_score:
                    best_score = score
                    best_k = k
            except Exception:
                continue

        return {'optimal_clusters': best_k, 'scores': scores}

    def _find_optimal_clusters(self, prepared_features) -> int:
        """Use elbow method as default."""
        cluster_range = range(2, min(11, len(prepared_features) // 2 + 1))
        inertias = []
        for k in cluster_range:
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(prepared_features)
                inertias.append(kmeans.inertia_)
            except Exception:
                inertias.append(0)
        return self._find_elbow_point(inertias, cluster_range)

    def _generate_segment_names(self, segmentation_results: pd.DataFrame, n_clusters: int) -> Dict[int, str]:
        """Analyse each segment to generate descriptive names."""
        segment_names = {}
        for segment_id in range(n_clusters):
            segment_data = segmentation_results[segmentation_results['segment_id'] == segment_id]
            avg_spend = segment_data['total_spent'].mean() if 'total_spent' in segment_data.columns else 0
            avg_frequency = segment_data['transaction_frequency'].mean() if 'transaction_frequency' in segment_data.columns else 0
            avg_recency = segment_data['recency_days'].mean() if 'recency_days' in segment_data.columns else 0

            if avg_spend > segmentation_results['total_spent'].quantile(0.75):
                spend_level = "High-Value"
            elif avg_spend > segmentation_results['total_spent'].quantile(0.5):
                spend_level = "Medium-Value"
            else:
                spend_level = "Low-Value"

            if avg_frequency > segmentation_results['transaction_frequency'].quantile(0.75):
                frequency_level = "Frequent"
            elif avg_frequency > segmentation_results['transaction_frequency'].quantile(0.5):
                frequency_level = "Regular"
            else:
                frequency_level = "Occasional"

            if avg_recency < segmentation_results['recency_days'].quantile(0.25):
                recency_level = "Recent"
            elif avg_recency < segmentation_results['recency_days'].quantile(0.5):
                recency_level = "Active"
            else:
                recency_level = "Inactive"

            segment_names[segment_id] = f"{spend_level}-{frequency_level}-{recency_level}"
        return segment_names

    def _create_segment_profiles(self, segmentation_results: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Create detailed profiles for each segment."""
        profiles = {}
        for segment_id in segmentation_results['segment_id'].unique():
            segment_data = segmentation_results[segmentation_results['segment_id'] == segment_id]
            segment_name = segment_data['segment_name'].iloc[0]
            profile = {
                'size': len(segment_data),
                'percentage': len(segment_data) / len(segmentation_results) * 100,
                'avg_total_spent': segment_data['total_spent'].mean() if 'total_spent' in segment_data.columns else None,
                'avg_transaction_amount': segment_data['avg_transaction_amount'].mean() if 'avg_transaction_amount' in segment_data.columns else None,
                'avg_transaction_count': segment_data['transaction_count'].mean() if 'transaction_count' in segment_data.columns else None,
                'avg_recency_days': segment_data['recency_days'].mean() if 'recency_days' in segment_data.columns else None,
                'avg_monthly_spend': segment_data['avg_monthly_spend'].mean() if 'avg_monthly_spend' in segment_data.columns else None,
                'primary_categories': segment_data['primary_category'].value_counts().head(3).to_dict() if 'primary_category' in segment_data.columns else {}
            }
            profiles[segment_name] = profile
        return profiles

    # ------------------------------------------------------------------
    # PHASE 2 FROZEN ARTIFACT — CANONICAL PRODUCTION PATH (Phase 4.5)
    # ------------------------------------------------------------------

    def load_frozen_artifact(
        self,
        model_path: str = FROZEN_MODEL_PATH,
        scaler_path: str = FROZEN_SCALER_PATH,
        labels_path: str = FROZEN_LABELS_PATH,
    ) -> None:
        """Load the frozen Phase 2 segmentation artifact.

        This is the ONLY sanctioned path for production segment predictions.
        Call once at startup; then use predict_with_frozen_artifact().

        Raises:
            FileNotFoundError: if any required artifact file is missing.
            RuntimeError: if the artifact fails to deserialize.
        """
        import json
        import warnings

        for path, name in [(model_path, "model"), (scaler_path, "scaler"), (labels_path, "labels")]:
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Frozen Phase 2 segmentation {name} not found at: {path}\n"
                    "Re-run the Phase 2 notebook to regenerate frozen artifacts."
                )
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._frozen_model = joblib.load(model_path)
                self._frozen_scaler = joblib.load(scaler_path)
            with open(labels_path, "r") as f:
                raw = json.load(f)
            self._frozen_labels = {int(k): v for k, v in raw.items()}
            self._frozen_artifact_loaded = True
            self.logger.info(
                f"Frozen Phase 2 segmentation artifact loaded. "
                f"Clusters: {len(self._frozen_labels)}"
            )
        except Exception as exc:
            self._frozen_artifact_loaded = False
            raise RuntimeError(f"Failed to load frozen segmentation artifact: {exc}") from exc

    def predict_with_frozen_artifact(
        self, feature_df: pd.DataFrame, feature_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Predict customer segments using the frozen Phase 2 KMeans artifact.

        Args:
            feature_df: DataFrame with customer features.
            feature_cols: ordered list of feature column names. If None, uses
                          the legacy feature set from prepare_features().

        Returns:
            Copy of feature_df with 'frozen_cluster_id' and 'frozen_segment_name'.

        Raises:
            RuntimeError: if load_frozen_artifact() has not been called first.
        """
        if not self._frozen_artifact_loaded:
            raise RuntimeError(
                "Frozen artifact not loaded. Call load_frozen_artifact() first."
            )
        if feature_cols is None:
            feature_cols = [
                'total_spent', 'avg_transaction_amount', 'transaction_count',
                'avg_monthly_spend', 'transaction_frequency', 'recency_days',
                'unique_merchants',
            ]
        available = [c for c in feature_cols if c in feature_df.columns]
        X = feature_df[available].fillna(feature_df[available].median()).copy()
        X_scaled = self._frozen_scaler.transform(X)
        cluster_ids = self._frozen_model.predict(X_scaled)
        result = feature_df.copy()
        result['frozen_cluster_id'] = cluster_ids
        result['frozen_segment_name'] = [
            self._frozen_labels.get(int(cid), f"Cluster_{cid}") for cid in cluster_ids
        ]
        return result

    @property
    def frozen_artifact_loaded(self) -> bool:
        """True if the frozen Phase 2 artifact has been successfully loaded."""
        return self._frozen_artifact_loaded

    # ------------------------------------------------------------------
    # LEGACY PERSISTENCE (used by legacy API endpoint + test_segmentation)
    # ------------------------------------------------------------------

    def save_model(self, model_path: str = "data/models/segmentation_model.pkl"):
        """Save the legacy-trained model state to disk."""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'segment_profiles': self.segment_profiles
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        self.logger.info(f"Model saved to {model_path}")

    def load_model(self, model_path: str = "data/models/segmentation_model.pkl"):
        """Load a legacy-trained model state from disk."""
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            self.segment_profiles = model_data['segment_profiles']
            self.logger.info(f"Model loaded from {model_path}")
        else:
            self.logger.warning(f"Model file not found: {model_path}")

    def predict_segment(self, customer_features: pd.DataFrame) -> pd.DataFrame:
        """Predict using the legacy-trained model (used after load_model())."""
        feature_matrix = customer_features[self.feature_columns].copy()
        feature_matrix = feature_matrix.fillna(feature_matrix.median())

        skewed_features = ['total_spent', 'avg_transaction_amount', 'avg_monthly_spend']
        for feature in skewed_features:
            if feature in feature_matrix.columns:
                feature_matrix[feature] = np.log1p(feature_matrix[feature])

        X_scaled = self.scaler.transform(feature_matrix)
        cluster_labels = self.model.predict(X_scaled)

        result_df = customer_features.copy()
        result_df['segment_id'] = cluster_labels
        segment_names = {i: name for i, name in enumerate(self.segment_profiles.keys())}
        result_df['segment_name'] = result_df['segment_id'].map(segment_names)
        return result_df