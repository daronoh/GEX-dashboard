import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def plot_gamma_exposure(
    gamma_all: pd.DataFrame,
    spot_price: float,
    gamma_next_expiry: pd.DataFrame = None,
    gamma_next_monthly: pd.DataFrame = None,
) -> None:
    """
    Plot total gamma exposure vs strike for all expiries, next expiry (green), and next monthly expiry (yellow).
    """
    fig = go.Figure()

    # All expiries (blue)
    gamma_all = gamma_all.sort_values('strike')
    fig.add_trace(go.Scatter(
        x=gamma_all['strike'],
        y=gamma_all['total_gamma_exposure'],
        mode='lines',
        name='All Expiries',
        line_shape='spline',
        line_width=1,
        line=dict(color='lightblue'),
        hovertemplate='Strike: %{x}<br>Gamma Exposure: %{y:.3f}B<extra></extra>'
    ))

    # Next expiry (green)
    if gamma_next_expiry is not None and not gamma_next_expiry.empty:
        gamma_next_expiry = gamma_next_expiry.sort_values('strike')
        fig.add_trace(go.Scatter(
            x=gamma_next_expiry['strike'],
            y=gamma_next_expiry['total_gamma_exposure'],
            mode='lines',
            name='Next Expiry',
            line_shape='spline',
            line=dict(color='green'),
            hovertemplate='Strike: %{x}<br>Next Expiry Gamma: %{y:.3f}B<extra></extra>'
        ))

    # Next monthly expiry (yellow)
    if gamma_next_monthly is not None and not gamma_next_monthly.empty:
        gamma_next_monthly = gamma_next_monthly.sort_values('strike')
        fig.add_trace(go.Scatter(
            x=gamma_next_monthly['strike'],
            y=gamma_next_monthly['total_gamma_exposure'],
            mode='lines',
            name='Next Monthly Expiry',
            line_shape='spline',
            line=dict(color='yellow'),
            hovertemplate='Strike: %{x}<br>Next Monthly Gamma: %{y:.3f}B<extra></extra>'
        ))

    # Spot vertical line
    fig.add_vline(
        x=spot_price,
        line_width=0.6,
        line_color='red',
        annotation_text=f"Spot {spot_price:.2f}",
        annotation_position="top"
    )

    fig.update_layout(
        title='Gamma Exposure vs Strike',
        xaxis_title='Strike',
        yaxis_title='Gamma Exposure (B per 1% move)',
        hovermode='x unified',
        xaxis=dict(showgrid=True, gridwidth=0.5),
        yaxis=dict(showgrid=True, gridwidth=0.5),
        height=800
    )

    st.plotly_chart(fig, use_container_width=True)