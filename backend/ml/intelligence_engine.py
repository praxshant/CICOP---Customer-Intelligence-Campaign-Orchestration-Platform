import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.rules.action_policy import ActionPolicy

class IntelligenceEngine:
    """
    Core ML/Business Logic layer for CICOP Phase 4.
    Derives behavioral signals, calls the deterministic action policy,
    and produces the canonical customer intelligence object.
    """
    def __init__(self, action_policy: Optional[ActionPolicy] = None):
        self.action_policy = action_policy or ActionPolicy()
        self.signals_config = self.action_policy.signals_config

    def _generate_signals(self, row: pd.Series) -> Dict[str, Any]:
        """
        Derives deterministic customer-vs-self behavioral signals.
        """
        signals = {}
        history_days = max(float(row.get("FEATURE_customer_lifetime_days", 1)), 1.0)
        orders = max(float(row.get("FEATURE_purchase_order_count", 0)), 1.0)
        
        # 1. recency_elevated
        recency = float(row.get("FEATURE_recency_days", 0))
        normal_interval = history_days / orders
        recency_ratio = recency / max(normal_interval, 1.0)
        sig_cfg = self.signals_config.get("recency_elevated", {})
        threshold = sig_cfg.get("threshold", 2.0)
        
        is_elevated = bool(recency_ratio >= threshold and history_days >= 30 and orders >= 2)
        signals["recency_elevated"] = {
            "active": is_elevated,
            "value": round(recency_ratio, 2),
            "threshold": threshold,
            "message": f"Recency is {recency_ratio:.1f}x the customer's normal purchase interval." if is_elevated else ""
        }
        
        # 2. spend_declining
        spend_90d = float(row.get("FEATURE_net_spend_90d", 0))
        total_spend = float(row.get("FEATURE_total_net_spend", 0))
        baseline_90d_spend = (total_spend / max(history_days, 90.0)) * 90.0
        
        spend_ratio = spend_90d / max(baseline_90d_spend, 1.0)
        sig_cfg = self.signals_config.get("spend_declining", {})
        threshold = sig_cfg.get("threshold", 0.70)
        
        is_declining = bool(spend_ratio <= threshold and history_days >= 90 and total_spend > 0)
        signals["spend_declining"] = {
            "active": is_declining,
            "value": round(spend_ratio, 2),
            "threshold": threshold,
            "message": f"90-day spend is {int((1-spend_ratio)*100)}% below the customer's historical baseline." if is_declining else ""
        }
        
        # 3. frequency_declining
        freq_90d = float(row.get("FEATURE_purchase_order_count_90d", 0))
        baseline_90d_freq = (orders / max(history_days, 90.0)) * 90.0
        
        freq_ratio = freq_90d / max(baseline_90d_freq, 1.0)
        sig_cfg = self.signals_config.get("frequency_declining", {})
        threshold = sig_cfg.get("threshold", 0.50)
        
        is_freq_declining = bool(freq_ratio <= threshold and history_days >= 90 and orders >= 3)
        signals["frequency_declining"] = {
            "active": is_freq_declining,
            "value": round(freq_ratio, 2),
            "threshold": threshold,
            "message": "Recent 90-day purchase frequency is materially below historical cadence." if is_freq_declining else ""
        }
        
        # 4. return_risk
        return_rate = float(row.get("FEATURE_return_rate", 0))
        sig_cfg = self.signals_config.get("return_risk", {})
        threshold = sig_cfg.get("threshold", 0.15)
        
        has_return_risk = bool(return_rate > threshold and float(row.get("FEATURE_return_line_count", 0)) > 0)
        signals["return_risk"] = {
            "active": has_return_risk,
            "value": round(return_rate, 3),
            "threshold": threshold,
            "message": f"Return rate of {return_rate:.1%} is above normal operating thresholds." if has_return_risk else ""
        }
        
        return signals

    def process_customer(self, row: pd.Series) -> Dict[str, Any]:
        """
        Process a single customer to produce the canonical intelligence object.
        """
        customer_id = str(row["customer_id"])
        
        # Use string representation of date if timestamp
        as_of = row["observation_date"]
        if hasattr(as_of, "strftime"):
            as_of_date_str = as_of.strftime("%Y-%m-%d")
        else:
            as_of_date_str = str(as_of).split(" ")[0]
            
        segment = str(row["segment"])
        propensity_band = str(row["propensity_band"])
        prop_score = float(row["propensity_score"])
        history_days = float(row.get("FEATURE_customer_lifetime_days", 1))
        
        # Generate Signals
        signals = self._generate_signals(row)
        
        # Evaluate Action Policy
        policy_result = self.action_policy.evaluate(segment, propensity_band, signals)
        
        # Calculate Confidence
        confidence = self.action_policy.get_confidence(policy_result["policy_rule_id"], signals, history_days)
        
        # Build Evidence and Why
        why_list = []
        evidence_list = []
        
        for sig_name, sig_data in signals.items():
            if sig_data["active"]:
                why_list.append(sig_data["message"])
                evidence_list.append({
                    "signal": sig_name,
                    "value": sig_data["value"],
                    "threshold": sig_data["threshold"],
                    "message": sig_data["message"]
                })
        
        # Determine evidence status
        evidence_status = "EVIDENCE_PRESENT"
        if not evidence_list:
            if history_days < 30:
                evidence_status = "INSUFFICIENT_HISTORY"
            else:
                evidence_status = "NO_ACTIVE_SIGNALS"
                
        # Format active signals bool map
        active_signals = {k: v["active"] for k, v in signals.items()}
        
        # Canonical Object
        return {
            "customer_id": customer_id,
            "as_of_date": as_of_date_str,
            "segment": segment,
            "purchase_probability_30d": round(prop_score, 4),
            "propensity_band": propensity_band,
            
            "recommendation": policy_result["recommendation"],
            "recommendation_confidence": confidence,
            "policy_rule_id": policy_result["policy_rule_id"],
            
            "why": why_list,
            "evidence": evidence_list,
            "evidence_status": evidence_status,
            "behavioral_signals": active_signals
        }

    def process_batch(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Process a dataframe of customers and return a list of intelligence objects.
        """
        results = []
        # iterrows is fine for 5k rows, could vectorize if needed
        for _, row in df.iterrows():
            results.append(self.process_customer(row))
        return results
