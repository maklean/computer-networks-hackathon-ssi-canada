import streamlit as st
import plotly.express as px

from constants import RSSI_CRITICAL_THRESHOLD, RSSI_WARNING_THRESHOLD


def rssi_status(avg_rssi: float) -> str:
    # RSSI closer to 0 is better (less negative)
    if avg_rssi < RSSI_CRITICAL_THRESHOLD:
        return "Critical"
    if avg_rssi < RSSI_WARNING_THRESHOLD:
        return "Weak"
    return "Good"


def render_dashboard(df_all):
    st.title("Network Console")

    total_days = len(df_all["date"].unique())
    total_packets = len(df_all)
    avg_rssi = df_all["rssi"].mean()

    # packet loss from fCnt gaps
    df_all["prev_fCnt"] = df_all["fCnt"].shift(1)
    loss_mask = (df_all["fCnt"] - df_all["prev_fCnt"]) > 1
    total_loss = (df_all[loss_mask]["fCnt"] - df_all[loss_mask]["prev_fCnt"] - 1).sum()
    reliability = 100 * (1 - (total_loss / (total_packets + total_loss)))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Monitoring Period",
        f"{total_days} days",
        help="Unique days with at least one received packet.",
    )

    col2.metric(
        "Total Packets",
        f"{total_packets:,}",
        help="Count of payloads received by the gateway.",
    )

    # reliability: compact + hover-only details
    rel_status = "Excellent" if reliability > 98 else "Needs attention"
    col3.metric(
        "Network Reliability",
        f"{reliability:.2f}%",
        delta=rel_status,
        delta_color="off",  # neutral (since Streamlit can't do yellow)
        help="Estimated from frame count gaps (fCnt jumps imply missing packets).",
    )

    # avg RSSI: compact label + hover-only explanation
    rssi_label = rssi_status(avg_rssi)
    col4.metric(
        "Avg Signal (RSSI)",
        f"{avg_rssi:.1f} dBm",
        delta=rssi_label,
        delta_color="normal" if rssi_label == "Good" else "off",
        help=(
            "RSSI closer to 0 is better.\n\n"
            "-30 to -80: Strong\n"
            "-80 to -110: Good\n"
            "<-115: Critical/Unstable"
        ),
    )

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader(
            "Battery lifecycle",
            help="Voltage over time.",
        )
        fig_batt = px.line(df_all.iloc[::50], x="time", y="battery", title="Voltage depletion trend")
        fig_batt.update_layout(height=350, template="plotly_dark")
        st.plotly_chart(fig_batt, use_container_width=True)

    with c2:
        st.subheader(
            "Signal consistency",
            help="RSSI over time, colored by SNR.",
        )
        fig_rssi = px.scatter(
            df_all.iloc[::20],
            x="time",
            y="rssi",
            color="snr",
            title="Signal vs noise",
            color_continuous_scale="Viridis",
        )
        fig_rssi.update_layout(height=350, template="plotly_dark")
        st.plotly_chart(fig_rssi, use_container_width=True)
