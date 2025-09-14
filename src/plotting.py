from datetime import datetime, date
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from src.util import calcGammaEx, is_third_friday

def plot_call_put_gamma_exposure(
    gamma_df: pd.DataFrame,
    spot_price: float,
) -> None:
    """
    Bar chart of absolute call and put gamma exposures by strike.
    """
    fig = go.Figure()

    # Bar for Call Gamma
    fig.add_trace(go.Bar(
        x=gamma_df['strike'],
        y=gamma_df['call_gamma_exposure'],
        name='Call Gamma',
        marker_color='blue',
        opacity=0.7,
        hovertemplate='Strike: %{x}<br>Call Gamma: %{y:.3f}B<extra></extra>'
    ))

    # Bar for Put Gamma
    fig.add_trace(go.Bar(
        x=gamma_df['strike'],
        y=gamma_df['put_gamma_exposure'],
        name='Put Gamma',
        marker_color='orange',
        opacity=0.7,
        hovertemplate='Strike: %{x}<br>Put Gamma: %{y:.3f}B<extra></extra>'
    ))

    # Spot vertical line
    fig.add_vline(
        x=spot_price,
        line_width=1,
        line_color='red',
        annotation_text=f"Spot {spot_price:.2f}",
        annotation_position="top"
    )

    fig.update_layout(
        title='Absolute Gamma Exposure by Calls and Puts',
        xaxis_title='Strike',
        yaxis_title='Gamma Exposure (B per 1% move)',
        hovermode='x unified',
        xaxis=dict(showgrid=True, gridwidth=0.5),
        yaxis=dict(showgrid=True, gridwidth=0.5),
        barmode='overlay',
        height=800
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_total_gamma_exposure(
    gamma_all: pd.DataFrame,
    spot_price: float,
) -> None:
    """
    Plot total gamma exposure vs strike for all expiries.
    """
    fig = go.Figure()

    # All expiries (blue)
    gamma_all = gamma_all.sort_values('strike')
    fig.add_trace(go.Bar(
        x=gamma_all['strike'],
        y=gamma_all['total_gamma_exposure'],
        name='All Expiries',
        marker_color='lightblue',
        hovertemplate='Strike: %{x}<br>Gamma Exposure: %{y:.3f}B<extra></extra>'
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
        title='Absolute Gamma Exposure vs Strike',
        xaxis_title='Strike',
        yaxis_title='Gamma Exposure (B per 1% move)',
        hovermode='x unified',
        xaxis=dict(showgrid=True, gridwidth=0.5),
        yaxis=dict(showgrid=True, gridwidth=0.5),
        height=800
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_gamma_exposure_profile(
    options_data: pd.DataFrame,
    spot_price: float,
    reporting_date: date
) -> None:
    with st.spinner("Calculating gamma exposure profile..."):
        from_strike = 0.9 * spot_price
        to_strike = 1.1 * spot_price
        levels = np.linspace(from_strike, to_strike, 60)

        options_data['days_till_expiry'] = [1/262 if (np.busday_count(reporting_date, x)) == 0 else np.busday_count(reporting_date, x)/262 for x in options_data.expiry]
        
        next_expiry = options_data['expiry'].min()
        options_data['is_third_friday'] = options_data['expiry'].apply(is_third_friday)
        third_fridays = options_data[options_data['is_third_friday'] == True]
        next_monthly_expiry = third_fridays['expiry'].min()
        
        total_gamma = []
        total_gamma_ex_next = []
        total_gamma_ex_fri = []
        
        for level in levels:
            options_data['gamma_ex'] = options_data.apply(
                lambda row: calcGammaEx(
                    S=level,
                    K=row['strike'],
                    vol=row['iv'],
                    T=row['days_till_expiry'],
                    r=0,
                    q=0,
                    optType=row['option_type'],
                    OI=row['open_interest']
                ), axis=1
            )
            
            call_gamma = options_data.loc[options_data['option_type'] == 'C', 'gamma_ex'].sum()
            put_gamma = options_data.loc[options_data['option_type'] == 'P', 'gamma_ex'].sum()
            total_gamma.append(call_gamma - put_gamma)
            
            ex_next = options_data.loc[options_data['expiry'] != next_expiry]
            
            call_gamma_next = ex_next.loc[ex_next['option_type'] == 'C', 'gamma_ex'].sum()
            put_gamma_next = ex_next.loc[ex_next['option_type'] == 'P', 'gamma_ex'].sum()
            total_gamma_ex_next.append(call_gamma_next - put_gamma_next)
            
            ex_fri = options_data.loc[options_data['expiry'] != next_monthly_expiry]
            call_gamma_fri = ex_fri.loc[ex_fri['option_type'] == 'C', 'gamma_ex'].sum()
            put_gamma_fri = ex_fri.loc[ex_fri['option_type'] == 'P', 'gamma_ex'].sum()
            total_gamma_ex_fri.append(call_gamma_fri - put_gamma_fri)
            
        total_gamma = np.array(total_gamma) / 10**9
        total_gamma_ex_next = np.array(total_gamma_ex_next) / 10**9
        total_gamma_ex_fri = np.array(total_gamma_ex_fri) / 10**9

        zero_cross_idx = np.where(np.diff(np.sign(total_gamma)))[0]
        neg_gamma = total_gamma[zero_cross_idx]
        pos_gamma = total_gamma[zero_cross_idx + 1]
        neg_strike = levels[zero_cross_idx]
        pos_strike = levels[zero_cross_idx + 1]
        
        zero_gamma = pos_strike - ((pos_strike - neg_strike) * pos_gamma/(pos_gamma - neg_gamma))
        if len(zero_gamma) > 0:
            zero_gamma = zero_gamma[0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=levels,
            y=total_gamma,
            name="All Expiries",
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=levels,
            y=total_gamma_ex_next,
            name="Ex-Next Expiry",
            line=dict(color='yellow')
        ))
        fig.add_trace(go.Scatter(
            x=levels,
            y=total_gamma_ex_fri,
            name="Ex-Next Monthly Expiry",
            line=dict(color='orange')
        ))
        fig.add_trace(go.Scatter(
            x=[spot_price, spot_price],
            y=[min(total_gamma), max(total_gamma)],
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name=f"ES Spot: {spot_price:,.0f}"
        ))
        if len(zero_gamma) > 0:
            fig.add_trace(go.Scatter(
                x=[zero_gamma, zero_gamma],
                y=[min(total_gamma), max(total_gamma)],
                mode='lines',
                line=dict(color='green', width=2, dash='dash'),
                name=f"Gamma Flip: {zero_gamma:,.0f}"
            ))
        fig.update_layout(
            title=f"Gamma Exposure Profile, ES, {reporting_date.strftime('%d %b %Y')}",
            xaxis_title='Index Price',
            yaxis_title='Gamma Exposure ($ billions/1% move)',
            hovermode='x unified',
            xaxis=dict(showgrid=True, gridwidth=0.5),
            yaxis=dict(showgrid=True, gridwidth=0.5),
            height=800
        )
        st.plotly_chart(fig, use_container_width=True)