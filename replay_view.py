import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import time
from constants import SIMULATION_DELAY_SECONDS

from network_logic import process_packet, get_tank_html


def render_replay(df_all):
    """
    Replay traffic for a selected day.
    """
    if df_all.empty:
        st.error("No data found.")
        st.stop()

    available_dates = sorted(df_all["date"].unique())

    selected_date = st.sidebar.selectbox(
        "Audit date",
        options=available_dates,
        index=0,
    )

    day_df = df_all[df_all["date"] == selected_date].copy().reset_index(drop=True)

    st.title(f"Forensic Replay: {selected_date}")

    # daily stats
    day_df["prev_fCnt"] = day_df["fCnt"].shift(1)
    loss_mask = (day_df["fCnt"] - day_df["prev_fCnt"]) > 1
    loss_count = (day_df[loss_mask]["fCnt"] - day_df[loss_mask]["prev_fCnt"] - 1).sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Received packets", len(day_df))
    m2.metric("Lost packets", int(loss_count), delta_color="inverse")
    m3.metric("Avg signal", f"{day_df['rssi'].mean():.1f} dBm")
    m4.metric("Battery start", f"{day_df.iloc[0]['battery']}V")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Tank status", help="Tank level from the distance reading.")
        tank_ui = st.empty()

        initial_results = process_packet(day_df.iloc[0], None)
        initial_html = get_tank_html(initial_results["fill_pct"], initial_results["confidence"])
        with tank_ui:
            components.html(initial_html, height=350)

        conf_ui = st.empty()

    with col_right:
        st.subheader(
            "Telemetry",
            help=(
                "X: time\n"
                "Y: RSSI (dBm)\n\n"
                "Red X markers show detected packet loss."
            ),
        )
        chart_ui = st.empty()
        log_ui = st.empty()

    if st.sidebar.button("Playback", type="primary"):
        prev_fCnt = None
        history = []
        progress_bar = st.progress(0)

        for i in range(len(day_df)):
            packet = day_df.iloc[i]
            results = process_packet(packet, prev_fCnt)

            packet_data = packet.to_dict()
            packet_data["is_lost"] = results["is_lost"]
            history.append(packet_data)

            if len(history) > 40:
                history.pop(0)

            hist_df = pd.DataFrame(history)

            # tank
            tank_html = get_tank_html(results["fill_pct"], results["confidence"])
            with tank_ui:
                components.html(tank_html, height=350)

            # confidence
            conf_ui.metric(
                "Network confidence",
                f"{results['confidence']}%",
                delta="Stable" if not results["alerts"] else results["alerts"][0],
                delta_color="normal" if results["confidence"] > 70 else "inverse",
            )

            # chart
            with chart_ui:
                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=hist_df["time"],
                        y=hist_df["rssi"],
                        mode="lines+markers",
                        line=dict(color="#00c6ff", width=2),
                        name="Signal",
                    )
                )

                loss_points = hist_df[hist_df["is_lost"] == True]
                if not loss_points.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=loss_points["time"],
                            y=loss_points["rssi"],
                            mode="markers",
                            marker=dict(symbol="x", color="red", size=12, line=dict(width=2)),
                            name="Loss",
                        )
                    )

                fig.add_hline(y=-115, line_dash="dot", line_color="red")

                fig.update_layout(
                    title=f"Live signal ({packet['time'].strftime('%H:%M:%S')})",
                    height=300,
                    yaxis_range=[-130, -50],
                    margin=dict(l=20, r=20, t=40, b=20),
                    template="plotly_dark",
                    showlegend=True,
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                )

                st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")

            # log
            with log_ui:
                if results["alerts"]:
                    for a in results["alerts"]:
                        st.error(f"{packet['time'].strftime('%H:%M:%S')} - {a}")
                else:
                    st.info(f"{packet['time'].strftime('%H:%M:%S')} - Packet {packet['fCnt']} OK")

            progress_bar.progress((i + 1) / len(day_df))
            prev_fCnt = packet["fCnt"]
            time.sleep(SIMULATION_DELAY_SECONDS)
