# campaign_generator.py
# Purpose: Automated campaign generation and management

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from backend.utils.logger import setup_logger
from backend.utils.config_loader import load_config
from backend.rules.rules_engine import RulesEngine

class CampaignGenerator:
    def __init__(self):
        # Step 1: Initialize campaign generator
        self.logger = setup_logger("CampaignGenerator")
        self.config = load_config()
        self.rules_engine = RulesEngine()

    def generate_campaigns_for_segment(self, segment_name: str,
                                       customers_df: pd.DataFrame,
                                       customer_features_df: pd.DataFrame) -> pd.DataFrame:
        # Step 1: Generate campaigns for a specific customer segment
        segment_customers = customers_df[customers_df['segment_name'] == segment_name]

        if segment_customers.empty:
            self.logger.warning(f"No customers found for segment: {segment_name}")
            return pd.DataFrame()

        # Step 2: Get customer features for the segment
        segment_customer_ids = segment_customers['customer_id'].tolist()
        segment_features = customer_features_df[customer_features_df['customer_id'].isin(segment_customer_ids)]

        # Step 3: Generate campaigns using rules engine
        campaigns_df = self.rules_engine.generate_bulk_campaigns(segment_customers, segment_features)

        # Step 4: Add segment information
        if campaigns_df:  # Handle both DataFrame and list
            if isinstance(campaigns_df, list):
                campaigns_df = pd.DataFrame(campaigns_df)

            campaigns_df['target_segment'] = segment_name
            campaigns_df['campaign_name'] = f"{segment_name}_{campaigns_df['campaign_type']}"

            self.logger.info(f"Generated {len(campaigns_df)} campaigns for segment: {segment_name}")
            return campaigns_df
        else:
            self.logger.warning(f"No campaigns generated for segment: {segment_name}")
            return pd.DataFrame()

    def generate_personalized_campaigns(self, customers_df,
                                        customer_features_df=None,
                                        transactions_df=None):
        # Handle both DataFrame and dict inputs for test compatibility
        if isinstance(customers_df, dict):
            # Single customer case
            customer_dict = customers_df
            customer_series = pd.Series(customer_dict)
            customer_transactions = transactions_df or pd.DataFrame([{
                'customer_id': customer_dict.get('customer_id', 'UNKNOWN'),
                'amount': 100,
                'category': 'Test',
                'transaction_date': datetime.now()
            }])

            campaigns = self._generate_customer_specific_campaigns(
                customer_series, customer_series, customer_transactions
            )
            # Apply personalization reason (list comprehension ensures mutation is captured)
            campaigns = [self._add_personalization_reason(c, customer_series, customer_series) for c in campaigns]
            return campaigns

        # Original DataFrame logic
        all_campaigns = []

        for _, customer_row in customers_df.iterrows():
            customer_id = customer_row['customer_id']

            # Get customer features and transactions
            customer_features = customer_features_df[customer_features_df['customer_id'] == customer_id]
            customer_transactions = transactions_df[transactions_df['customer_id'] == customer_id]

            if not customer_features.empty and not customer_transactions.empty:
                features_row = customer_features.iloc[0]

                campaigns = self._generate_customer_specific_campaigns(
                    customer_row, features_row, customer_transactions
                )
                campaigns = [self._add_personalization_reason(c, customer_row, features_row) for c in campaigns]
                all_campaigns.extend(campaigns)

        if all_campaigns:
            campaigns_df = pd.DataFrame(all_campaigns)
            campaigns_df = campaigns_df.sort_values('priority_score', ascending=False)
            self.logger.info(f"Generated {len(campaigns_df)} personalized campaigns")
            return campaigns_df
        else:
            return pd.DataFrame()

    # ---------------------------------------------------------------------------
    # Compatibility APIs expected by tests
    # ---------------------------------------------------------------------------

    def generate_segment_campaigns(self, customers_df: pd.DataFrame, segment_name: str) -> List[Dict]:
        """Return campaigns as list of dicts for test compatibility."""
        campaigns_df = self.generate_campaigns_for_segment(segment_name, customers_df, customers_df)
        return campaigns_df.to_dict('records') if not campaigns_df.empty else []

    def schedule_campaigns(self, campaigns_df, start_date: datetime) -> List[Dict]:
        """Add scheduling metadata to campaigns."""
        if isinstance(campaigns_df, list):
            if not campaigns_df:
                return []
            campaigns_df = pd.DataFrame(campaigns_df)
        elif campaigns_df.empty:
            return campaigns_df

        campaigns_df['scheduled_start'] = start_date
        campaigns_df['scheduled_end'] = start_date + timedelta(days=30)
        campaigns_df['scheduled_date'] = start_date
        campaigns_df['delivery_channel'] = 'email'

        return campaigns_df.to_dict('records')

    def _add_campaign_metadata(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        campaign['scheduled_date'] = datetime.now()
        campaign['delivery_channel'] = 'email'
        return campaign

    def _add_personalization_reason(self, campaign: Dict[str, Any], customer_data,
                                    customer_features) -> Dict[str, Any]:
        """Attach a personalization_reason field to a campaign dict."""
        total_spent = customer_features.get('total_spent', 0) if hasattr(customer_features, 'get') else 0
        recency_days = customer_features.get('recency_days', 0) if hasattr(customer_features, 'get') else 0

        if total_spent > 2000:
            campaign['personalization_reason'] = 'High-value customer'
        elif recency_days > 60:
            campaign['personalization_reason'] = 'Win-back opportunity'
        else:
            campaign['personalization_reason'] = 'Standard personalization'

        return campaign

    def predict_campaign_effectiveness(self, customer_dict: Dict[str, Any], campaign_type: str) -> Dict[str, Any]:
        """Simple heuristic effectiveness score based on campaign type and spend."""
        base = {
            'loyalty_reward': 0.7,
            'win_back': 0.6,
            'cross_sell': 0.5,
            'seasonal_promotion': 0.4
        }.get(campaign_type, 0.5)
        multiplier = 1.0
        if customer_dict.get('total_spent', 0) > 1000:
            multiplier += 0.1
        if customer_dict.get('recency_days', 999) < 30:
            multiplier += 0.05
        score = min(base * multiplier, 0.95)
        return {
            'campaign_type': campaign_type,
            'effectiveness_score': score,
            'response_probability': score * 0.8,
            'expected_revenue': score * 100,
            'roi_prediction': score * 0.15
        }

    # ---------------------------------------------------------------------------
    # Internal campaign generation logic
    # ---------------------------------------------------------------------------

    def _generate_customer_specific_campaigns(self, customer_data: pd.Series,
                                              customer_features: pd.Series,
                                              customer_transactions: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate all applicable campaigns for a single customer. Always returns at least one."""
        campaigns = []

        # High-value spend campaign
        if customer_features.get('total_spent', 0) > 2000:
            campaigns.append(self._create_high_value_campaign(customer_data, customer_features))

        # Category-specific campaign
        if 'primary_category' in customer_features:
            category_campaign = self._create_category_campaign(customer_data, customer_features)
            if category_campaign:
                campaigns.append(category_campaign)

        # Frequency-based campaign
        if customer_features.get('transaction_frequency', 0) > 0.1:
            campaigns.append(self._create_frequency_campaign(customer_data, customer_features))

        # Win-back campaign for inactive customers
        if customer_features.get('recency_days', 0) > 60:
            campaigns.append(self._create_win_back_campaign(customer_data, customer_features))

        # Seasonal campaign
        seasonal_campaign = self._create_seasonal_campaign(customer_data, customer_features)
        if seasonal_campaign:
            campaigns.append(seasonal_campaign)

        # Fallback — always guarantee at least one engagement campaign
        if not campaigns:
            campaigns.append(self._create_engagement_campaign(customer_data, customer_features))

        return campaigns

    def _create_high_value_campaign(self, customer_data: pd.Series,
                                    customer_features: pd.Series) -> Dict[str, Any]:
        return {
            'campaign_id': f"high_value_{customer_data.get('customer_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
            'customer_id': customer_data.get('customer_id', 'UNKNOWN'),
            'campaign_type': 'high_value_reward',
            'offer_description': f"Exclusive VIP treatment for {customer_data.get('first_name', 'Valued')} customer!",
            'discount_percentage': 20,
            'min_purchase': 150,
            'validity_days': 45,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active',
            'priority_score': 0.95,
            'target_segment': 'High-Value',
            'campaign_name': f"High-Value_{customer_data.get('first_name', 'Customer')}"
        }

    def _create_engagement_campaign(self, customer_data: pd.Series,
                                    customer_features: pd.Series) -> Dict[str, Any]:
        """Universal fallback campaign for customers who don't qualify for other campaign types."""
        return {
            'campaign_id': f"engagement_{customer_data.get('customer_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
            'customer_id': customer_data.get('customer_id', 'UNKNOWN'),
            'campaign_type': 'engagement_offer',
            'offer_description': f"Special offer for {customer_data.get('first_name', 'Valued')} - enjoy 10% off your next purchase!",
            'discount_percentage': 10,
            'min_purchase': 50,
            'validity_days': 30,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active',
            'priority_score': 0.4,
            'target_segment': 'General',
            'campaign_name': f"Engagement_{customer_data.get('first_name', 'Customer')}"
        }

    def _create_frequency_campaign(self, customer_data: pd.Series,
                                   customer_features: pd.Series) -> Dict[str, Any]:
        return {
            'campaign_id': f"frequency_{customer_data.get('customer_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
            'customer_id': customer_data.get('customer_id', 'UNKNOWN'),
            'campaign_type': 'frequency_reward',
            'offer_description': f"Reward for frequent shopping by {customer_data.get('first_name', 'Valued')} customer!",
            'discount_percentage': 12,
            'min_purchase': 70,
            'validity_days': 40,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active',
            'priority_score': 0.75,
            'target_segment': 'Frequent',
            'campaign_name': f"Frequency_{customer_data.get('first_name', 'Customer')}"
        }

    def _create_win_back_campaign(self, customer_data: pd.Series,
                                  customer_features: pd.Series) -> Dict[str, Any]:
        return {
            'campaign_id': f"winback_{customer_data.get('customer_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
            'customer_id': customer_data.get('customer_id', 'UNKNOWN'),
            'campaign_type': 'win_back',
            'offer_description': f"Welcome back {customer_data.get('first_name', 'Valued')} customer! Special comeback offer.",
            'discount_percentage': 30,
            'min_purchase': 40,
            'validity_days': 90,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active',
            'priority_score': 0.8,
            'target_segment': 'Win-Back',
            'campaign_name': f"WinBack_{customer_data.get('first_name', 'Customer')}"
        }

    def _create_seasonal_campaign(self, customer_data: pd.Series,
                                  customer_features: pd.Series) -> Optional[Dict[str, Any]]:
        """Return a seasonal campaign only for recognised seasonal months; None otherwise."""
        current_month = datetime.now().month
        seasonal_offers = {
            12: {'name': 'Holiday',      'discount': 25, 'min_purchase': 100},
            1:  {'name': 'New Year',     'discount': 15, 'min_purchase': 80},
            2:  {'name': 'Valentine',    'discount': 20, 'min_purchase': 60},
            6:  {'name': 'Summer',       'discount': 15, 'min_purchase': 70},
            10: {'name': 'Halloween',    'discount': 18, 'min_purchase': 65},
            11: {'name': 'Thanksgiving', 'discount': 22, 'min_purchase': 90},
        }

        if current_month not in seasonal_offers:
            return None

        offer = seasonal_offers[current_month]
        return {
            'campaign_id': f"seasonal_{customer_data.get('customer_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
            'customer_id': customer_data.get('customer_id', 'UNKNOWN'),
            'campaign_type': 'seasonal_promotion',
            'offer_description': f"{offer['name']} special for {customer_data.get('first_name', 'Valued')} customer!",
            'discount_percentage': offer['discount'],
            'min_purchase': offer['min_purchase'],
            'validity_days': 30,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active',
            'priority_score': 0.6,
            'target_segment': 'Seasonal',
            'campaign_name': f"Seasonal_{offer['name']}_{customer_data.get('first_name', 'Customer')}"
        }

    def _create_category_campaign(self, customer_data: pd.Series,
                                  customer_features: pd.Series) -> Optional[Dict[str, Any]]:
        primary_category = customer_features.get('primary_category')
        if not primary_category:
            return None

        return {
            'campaign_id': f"category_{customer_data.get('customer_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
            'customer_id': customer_data.get('customer_id', 'UNKNOWN'),
            'campaign_type': 'category_specific',
            'offer_description': f"Special offer on {primary_category} for {customer_data.get('first_name', 'Valued')} customer!",
            'discount_percentage': 15,
            'min_purchase': 80,
            'validity_days': 30,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active',
            'priority_score': 0.7,
            'target_segment': 'Category-Specific',
            'campaign_name': f"Category_{primary_category}_{customer_data.get('first_name', 'Customer')}",
            'category': primary_category
        }

    # ---------------------------------------------------------------------------
    # Portfolio optimisation & reporting
    # ---------------------------------------------------------------------------

    def optimize_campaign_portfolio(self, campaigns_df,
                                    budget_constraint: float = 10000,
                                    max_budget: float = None) -> Dict[str, Any]:
        # Handle both parameter names for compatibility
        if max_budget is not None:
            budget_constraint = max_budget

        if isinstance(campaigns_df, list):
            if not campaigns_df:
                return {'selected_campaigns': [], 'total_budget_used': 0, 'expected_roi': 0}
            campaigns_df = pd.DataFrame(campaigns_df)
        elif campaigns_df.empty:
            return {'selected_campaigns': [], 'total_budget_used': 0, 'expected_roi': 0}

        campaigns_df['expected_roi'] = campaigns_df['discount_percentage'] * campaigns_df['priority_score']
        campaigns_df['campaign_cost'] = campaigns_df['min_purchase'] * (campaigns_df['discount_percentage'] / 100)

        campaigns_df = campaigns_df.sort_values('expected_roi', ascending=False)

        cumulative_cost = 0
        selected_campaigns = []

        for _, campaign in campaigns_df.iterrows():
            if cumulative_cost + campaign['campaign_cost'] <= budget_constraint:
                selected_campaigns.append(campaign)
                cumulative_cost += campaign['campaign_cost']
            else:
                break

        total_roi = sum(c['expected_roi'] for c in selected_campaigns)

        self.logger.info(
            f"Optimized portfolio: {len(selected_campaigns)} campaigns selected with budget ${budget_constraint}"
        )

        return {
            'selected_campaigns': selected_campaigns,
            'total_budget_used': cumulative_cost,
            'expected_roi': total_roi
        }

    def generate_campaign_report(self, campaigns_df) -> Dict[str, Any]:
        if isinstance(campaigns_df, list):
            if not campaigns_df:
                return {
                    'total_campaigns': 0,
                    'campaign_types': {},
                    'total_budget': 0,
                    'segment_distribution': {}
                }
            campaigns_df = pd.DataFrame(campaigns_df)
        elif campaigns_df.empty:
            return {}

        return {
            'total_campaigns': len(campaigns_df),
            'campaigns_by_type': campaigns_df['campaign_type'].value_counts().to_dict(),
            'campaigns_by_segment': campaigns_df['target_segment'].value_counts().to_dict(),
            'campaign_types': campaigns_df['campaign_type'].value_counts().to_dict(),
            'total_budget': (campaigns_df['min_purchase'] * campaigns_df['discount_percentage'] / 100).sum(),
            'segment_distribution': campaigns_df['target_segment'].value_counts().to_dict(),
            'avg_discount_percentage': campaigns_df['discount_percentage'].mean(),
            'avg_priority_score': campaigns_df['priority_score'].mean(),
            'total_potential_revenue': campaigns_df['min_purchase'].sum(),
            'total_campaign_cost': (campaigns_df['min_purchase'] * campaigns_df['discount_percentage'] / 100).sum(),
            'campaigns_by_status': campaigns_df['status'].value_counts().to_dict(),
            'top_campaigns': campaigns_df.head(10)[['campaign_name', 'priority_score', 'discount_percentage']].to_dict('records')
        }