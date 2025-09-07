import re
import pandas as pd

def calculate_gamma_exposure(
    data: pd.DataFrame,
    spot_price: float
) -> pd.DataFrame:
    # Per‑contract gamma exposure (per 1% underlying move)
    data = data.copy()
    factor = (spot_price ** 2) * 0.01 * 100

    data['gamma_exposure'] = data['gamma'] * data['open_interest'] * factor

    grouped = (
        data.groupby(['strike', 'option_type'], as_index=False)
        .agg({'gamma_exposure': 'sum'})
    )

    pivoted = grouped.pivot(index='strike', columns='option_type', values='gamma_exposure').fillna(0)
    pivoted['total_gamma_exposure'] = pivoted.get('C', 0) - pivoted.get('P', 0)
    pivoted['total_gamma_exposure'] = pivoted['total_gamma_exposure'] / 1e9

    result = pivoted.reset_index()[['strike', 'total_gamma_exposure']]
    return result
