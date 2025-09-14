import pandas as pd

def calculate_gamma_exposure(
    data: pd.DataFrame,
    spot_price: float
) -> pd.DataFrame:
    data = data.copy()
    factor = (spot_price ** 2) * 0.01 * 100

    data['gamma_exposure'] = data['gamma'] * data['open_interest'] * factor

    grouped = (
        data.groupby(['strike', 'option_type'], as_index=False)
        .agg({'gamma_exposure': 'sum'})
    )

    pivoted = grouped.pivot(index='strike', columns='option_type', values='gamma_exposure').fillna(0)
    pivoted['call_gamma_exposure'] = pivoted.get('C', 0) / 1e9
    pivoted['put_gamma_exposure'] = - pivoted.get('P', 0) / 1e9
    pivoted['total_gamma_exposure'] = pivoted['call_gamma_exposure'] + pivoted['put_gamma_exposure']

    result = pivoted.reset_index()[['strike', 'call_gamma_exposure', 'put_gamma_exposure', 'total_gamma_exposure']]
    return result