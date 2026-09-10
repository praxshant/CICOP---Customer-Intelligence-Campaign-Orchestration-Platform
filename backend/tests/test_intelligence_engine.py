import pytest
import pandas as pd
from datetime import datetime
from backend.ml.intelligence_engine import IntelligenceEngine
from backend.rules.action_policy import ActionPolicy
import json
import os
from pathlib import Path

@pytest.fixture
def test_config(tmp_path):
    config = {
        "signals": {
            "test_signal": {"threshold": 2.0}
        },
        "rules": [
            {
                "rule_id": "TEST_01",
                "priority": 100,
                "conditions": {
                    "segment": "Active High-Value",
                    "propensity_bands": ["3_HIGH", "4_VERY_HIGH"],
                    "signals": {"recency_elevated": True}
                },
                "recommendation": "High priority test action"
            },
            {
                "rule_id": "TEST_02",
                "priority": 50,
                "conditions": {
                    "segment": "Active High-Value",
                    "propensity_bands": ["3_HIGH", "4_VERY_HIGH"]
                },
                "recommendation": "Medium priority test action"
            },
            {
                "rule_id": "DEFAULT_01",
                "priority": 0,
                "conditions": {},
                "recommendation": "Standard engagement"
            }
        ],
        "confidence_rules": {
            "HIGH": {"min_history_days": 90},
            "MEDIUM": {"min_history_days": 30},
            "LOW": {"min_history_days": 0}
        }
    }
    
    config_path = tmp_path / "test_policy.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
        
    return config_path

@pytest.fixture
def engine(test_config):
    policy = ActionPolicy(config_path=test_config)
    # We will override the signals_config in engine for standard logic tests
    engine = IntelligenceEngine(action_policy=policy)
    engine.signals_config = {
        "recency_elevated": {"threshold": 2.0},
        "spend_declining": {"threshold": 0.70},
        "frequency_declining": {"threshold": 0.50},
        "return_risk": {"threshold": 0.15}
    }
    return engine

def test_determinism(engine):
    row = pd.Series({
        "customer_id": "123",
        "observation_date": datetime(2011, 8, 31),
        "segment": "Active High-Value",
        "propensity_band": "4_VERY_HIGH",
        "propensity_score": 0.85,
        "FEATURE_customer_lifetime_days": 100,
        "FEATURE_purchase_order_count": 5,
        "FEATURE_recency_days": 60, # 60 / (100/5) = 3.0x -> elevated
        "FEATURE_net_spend_90d": 100,
        "FEATURE_total_net_spend": 1000,
        "FEATURE_purchase_order_count_90d": 1,
        "FEATURE_return_rate": 0.0,
        "FEATURE_return_line_count": 0
    })
    
    res1 = engine.process_customer(row)
    res2 = engine.process_customer(row)
    
    assert res1 == res2
    assert res1["policy_rule_id"] == "TEST_01"
    assert res1["recommendation"] == "High priority test action"
    assert res1["recommendation_confidence"] == "High"
    assert res1["behavioral_signals"]["recency_elevated"] is True

def test_rule_precedence(engine):
    # Same row, but not elevated recency, should fall back to TEST_02
    row = pd.Series({
        "customer_id": "123",
        "observation_date": datetime(2011, 8, 31),
        "segment": "Active High-Value",
        "propensity_band": "4_VERY_HIGH",
        "propensity_score": 0.85,
        "FEATURE_customer_lifetime_days": 100,
        "FEATURE_purchase_order_count": 5,
        "FEATURE_recency_days": 10, # not elevated
        "FEATURE_net_spend_90d": 1000,
        "FEATURE_total_net_spend": 1000,
        "FEATURE_purchase_order_count_90d": 5,
        "FEATURE_return_rate": 0.0,
        "FEATURE_return_line_count": 0
    })
    
    res = engine.process_customer(row)
    assert res["policy_rule_id"] == "TEST_02"
    assert res["recommendation"] == "Medium priority test action"

def test_fallback_handling(engine):
    row = pd.Series({
        "customer_id": "123",
        "observation_date": datetime(2011, 8, 31),
        "segment": "Unknown Segment",
        "propensity_band": "1_LOW",
        "propensity_score": 0.10,
        "FEATURE_customer_lifetime_days": 10,
        "FEATURE_purchase_order_count": 1,
        "FEATURE_recency_days": 10,
    })
    
    res = engine.process_customer(row)
    assert res["policy_rule_id"] == "DEFAULT_01"
    assert res["recommendation"] == "Standard engagement"
    assert res["recommendation_confidence"] == "Low"

def test_json_serialization(engine):
    row = pd.Series({
        "customer_id": "123",
        "observation_date": datetime(2011, 8, 31),
        "segment": "Active High-Value",
        "propensity_band": "4_VERY_HIGH",
        "propensity_score": 0.85,
    })
    res = engine.process_customer(row)
    # Should not throw exception
    json_str = json.dumps(res)
    assert "Active High-Value" in json_str

def test_no_leakage_with_target(engine):
    row = pd.Series({
        "customer_id": "123",
        "observation_date": datetime(2011, 8, 31),
        "segment": "Active High-Value",
        "propensity_band": "4_VERY_HIGH",
        "propensity_score": 0.85,
        "TARGET_next_purchase_30d": 1 # Target exists
    })
    res = engine.process_customer(row)
    # The output intelligence object must NOT include the target
    assert "TARGET_next_purchase_30d" not in res
    assert "TARGET_next_purchase_30d" not in json.dumps(res)
