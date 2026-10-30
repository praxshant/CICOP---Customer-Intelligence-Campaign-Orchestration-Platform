"""The single navigation surface for the Streamlit application."""

from typing import Mapping, Sequence

import streamlit as st


def render_sidebar(pages: Sequence[str], stats: Mapping[str, int] | None = None) -> str:
    """Render product navigation and return the selected page name."""
    with st.sidebar:
        st.title("CICOP")
        st.caption("Customer intelligence workspace")
        selected = st.radio("Workspace", options=list(pages), label_visibility="collapsed")

        st.divider()
        if st.button("Refresh data", use_container_width=True):
            st.cache_data.clear()
            st.session_state.data_loaded = False
            st.rerun()

        st.caption("Local sample-data environment")
        if stats:
            st.success("Database connected")
            st.caption(
                f"{stats.get('customers', 0):,} customers · "
                f"{stats.get('transactions', 0):,} transactions"
            )
            segment_count = stats.get('customer_segments', 0)
            customer_count = stats.get('customers', 0)
            if segment_count and segment_count != customer_count:
                st.warning(
                    "Sample data tables are out of sync. Regenerate the local sample data "
                    "before relying on the Segments or Campaigns pages."
                )
        else:
            st.warning("Database statistics unavailable")

        st.divider()
        st.caption("Rule-based segments and campaigns are estimates, not live campaign results.")

    return selected
