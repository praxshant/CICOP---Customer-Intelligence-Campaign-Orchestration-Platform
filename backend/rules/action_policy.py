import json
from pathlib import Path
from typing import Dict, Any, Optional

class ActionPolicy:
    """
    Deterministic action policy engine that maps Segment, Propensity, and
    Behavioral Signals to a specific recommended action.
    """
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            # Default to the canonical config path
            config_path = Path(__file__).parent.parent / "config" / "intelligence_action_policy.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        self.signals_config = self.config.get("signals", {})
        self.rules = self.config.get("rules", [])
        self.confidence_rules = self.config.get("confidence_rules", {})
        
        # Sort rules by priority descending
        self.rules = sorted(self.rules, key=lambda x: x.get("priority", 0), reverse=True)

    def evaluate(self, segment: str, propensity_band: str, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate customer state against loaded rules and return the highest priority match.
        """
        for rule in self.rules:
            if self._matches(rule, segment, propensity_band, signals):
                return {
                    "recommendation": rule["recommendation"],
                    "policy_rule_id": rule["rule_id"],
                    "priority": rule.get("priority", 0)
                }
                
        # Should always match the DEFAULT_01 rule if configured correctly
        return {
            "recommendation": "Standard engagement",
            "policy_rule_id": "FALLBACK_00",
            "priority": -1
        }
        
    def _matches(self, rule: Dict[str, Any], segment: str, propensity_band: str, signals: Dict[str, Any]) -> bool:
        conditions = rule.get("conditions", {})
        if not conditions:
            return True # Empty conditions match everything (e.g., default rule)
            
        # Check segment
        if "segment" in conditions:
            if conditions["segment"] != segment:
                return False
                
        # Check propensity band
        if "propensity_bands" in conditions:
            if propensity_band not in conditions["propensity_bands"]:
                return False
                
        # Check signals
        if "signals" in conditions:
            for sig_name, required_val in conditions["signals"].items():
                # If a signal is required but missing, or doesn't match required boolean state, fail
                if signals.get(sig_name, {}).get("active") != required_val:
                    return False
                    
        return True
        
    def get_confidence(self, matched_rule_id: str, signals: Dict[str, Any], history_days: float) -> str:
        """
        Determine confidence deterministically.
        """
        if matched_rule_id in ["DEFAULT_01", "FALLBACK_00"]:
            return "Low"
            
        active_signals = sum(1 for s in signals.values() if s.get("active"))
        
        # Check HIGH rules
        high_cfg = self.confidence_rules.get("HIGH", {})
        if history_days >= high_cfg.get("min_history_days", 90):
            # Either we matched a specific rule with decent history, or we have active signals
            return "High"
            
        # Check MEDIUM rules
        med_cfg = self.confidence_rules.get("MEDIUM", {})
        if history_days >= med_cfg.get("min_history_days", 30):
            return "Medium"
            
        return "Low"
