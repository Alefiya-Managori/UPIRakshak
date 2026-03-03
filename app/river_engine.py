from river import anomaly, compose, preprocessing, stats, drift
import math

class RiverAdaptiveEngine:
    def __init__(self):
        # LAYER 3: Behavioral Anomaly Detection
        # HalfSpaceTrees learns your spending patterns incrementally
        self.model = compose.Pipeline(
            preprocessing.MinMaxScaler(),
            anomaly.HalfSpaceTrees(n_trees=10, height=8, window_size=250)
        )
        
        # LAYER 6: Statistical Outlier Detection
        # Tracks the mean and variance of your transaction history
        self.amount_mean = stats.Mean()
        self.amount_var = stats.Var()
        self.q1 = stats.Quantile(q=0.25)
        self.q3 = stats.Quantile(q=0.75)
        
        # DRIFT DETECTION: Monitors if fraud patterns are evolving
        self.drifter = drift.ADWIN()

        # Numeric features for calculation
        self.numeric_features = [
            'amount', 'hour_of_day', 'pin_entry_time_ms', 
            'is_rooted', 'is_emulator', 'mock_location_enabled', 
            'is_on_call', 'is_malicious_link'
        ]

    def _filter_numeric(self, x: dict):
        """Cleans input data to ensure only numbers are processed"""
        clean_x = {}
        for key in self.numeric_features:
            if key in x:
                try:
                    clean_x[key] = float(x[key])
                except (TypeError, ValueError):
                    continue
        return clean_x

    def get_risk_score(self, x: dict):
        """Calculates a normalized risk score between 0.0 and 1.0"""
        numeric_x = self._filter_numeric(x)
        amount = numeric_x.get('amount', 0)
        
        # 1. Z-Score Calculation with Sigmoid Normalization
        # This prevents the '7993.0' error by squashing extreme outliers
        std = self.amount_var.get()**0.5
        raw_z = abs(amount - self.amount_mean.get()) / std if std > 0 else 0
        
        # Sigmoid squashes raw_z into a 0.0 - 1.0 range
        z_risk = 1 / (1 + math.exp(-raw_z / 10)) 

        # 2. IQR Calculation (Outlier Probability)
        q1_val = self.q1.get()
        q3_val = self.q3.get()
        
        if q1_val is not None and q3_val is not None:
            iqr = q3_val - q1_val
            upper_bound = q3_val + (1.5 * iqr)
            # Binary risk: 1.0 if way outside normal range, else 0.0
            iqr_risk = 1.0 if amount > upper_bound else 0.0
        else:
            iqr_risk = 0.0
        
        # 3. River ML Score (Behavioral DNA)
        # Inherently returns a value between 0.0 and 1.0
        ml_score = self.model.score_one(numeric_x)
        
        # 4. Final Weighted Aggregate Risk
        # Weights: ML (50%), IQR Outlier (30%), Z-Stats (20%)
        final_risk = (z_risk * 0.2) + (iqr_risk * 0.3) + (ml_score * 0.5)
        
        # Safety clamp to ensure jury never sees a number outside 0-1
        return min(max(final_risk, 0.0), 1.0)

    def learn_one(self, x: dict, is_fraud: int = None):
        """Updates the online learning model weights in real-time"""
        numeric_x = self._filter_numeric(x)
        amount = numeric_x.get('amount', 0)

        # Update statistical benchmarks
        self.amount_mean.update(amount)
        self.amount_var.update(amount)
        self.q1.update(amount)
        self.q3.update(amount)
        
        # Incrementally train the behavioral model
        self.model.learn_one(numeric_x)
        
        # Update the ADWIN drift detector
        if is_fraud is not None:
            self.drifter.update(is_fraud)