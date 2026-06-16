import numpy as np
import pandas as pd

def bond_price(face, coupon_rate, ytm, years, freq=2):
    n = int(max(1, round(years * freq)))
    r = ytm / freq
    c = face * coupon_rate / freq
    return sum((c if t < n else c + face) / ((1 + r) ** t) for t in range(1, n + 1))

def macaulay_duration(face, coupon_rate, ytm, years, freq=2):
    p = bond_price(face, coupon_rate, ytm, years, freq)
    n = int(max(1, round(years * freq)))
    r = ytm / freq
    c = face * coupon_rate / freq
    return sum((t / freq) * ((c if t < n else c + face) / ((1 + r) ** t)) for t in range(1, n + 1)) / p

def modified_duration(face, coupon_rate, ytm, years, freq=2):
    return macaulay_duration(face, coupon_rate, ytm, years, freq) / (1 + ytm / freq)

def convexity(face, coupon_rate, ytm, years, freq=2):
    p = bond_price(face, coupon_rate, ytm, years, freq)
    n = int(max(1, round(years * freq)))
    r = ytm / freq
    c = face * coupon_rate / freq
    numerator = sum(t * (t + 1) * ((c if t < n else c + face) / ((1 + r) ** t)) for t in range(1, n + 1))
    return numerator / (p * freq**2 * (1 + r)**2)

def portfolio_measures(df):
    mv = df['MarketValue_INR'].sum()
    w = df['MarketValue_INR'] / mv
    return {'market_value': mv, 'modified_duration': float((df['ModifiedDuration'] * w).sum()), 'effective_duration': float((df['EffectiveDuration'] * w).sum()), 'convexity': float((df['Convexity'] * w).sum()), 'dv01': float((df['DV01_Per100Face'] * df['Quantity'] / 100).sum())}

def parallel_price_impact(df, bps):
    dy = bps / 10000
    p = portfolio_measures(df)
    dur = -p['modified_duration'] * dy * p['market_value']
    conv = 0.5 * p['convexity'] * (dy**2) * p['market_value']
    return dur + conv, dur, conv

def monte_carlo(df, n_sims=1000, seed=42, vol_parallel=70, vol_twist=35, vol_butterfly=25):
    rng = np.random.default_rng(seed)
    parallel = rng.normal(0, vol_parallel / 10000, n_sims)
    twist = rng.normal(0, vol_twist / 10000, n_sims)
    butterfly = rng.normal(0, vol_butterfly / 10000, n_sims)
    maturity_factor = (df['YearsToMaturity'] - df['YearsToMaturity'].mean()) / max(df['YearsToMaturity'].std(), 1)
    belly_factor = -((df['YearsToMaturity'] - 7).abs()) / 10
    pnl = []
    for i in range(n_sims):
        dy_i = parallel[i] + twist[i] * maturity_factor + butterfly[i] * belly_factor
        dur = -(df['ModifiedDuration'] * dy_i * df['MarketValue_INR']).sum()
        conv = (0.5 * df['Convexity'] * (dy_i**2) * df['MarketValue_INR']).sum()
        pnl.append(float(dur + conv))
    out = pd.DataFrame({'Scenario': np.arange(1, n_sims+1), 'PnL_INR': pnl, 'ParallelShock_bps': parallel*10000})
    var95 = np.percentile(out['PnL_INR'], 5)
    cvar95 = out.loc[out['PnL_INR'] <= var95, 'PnL_INR'].mean()
    return out, float(var95), float(cvar95)

def key_rate_duration_table(df):
    order = ['3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y']
    total_mv = df['MarketValue_INR'].sum()
    out = df.groupby('TenorBucket').apply(lambda x: (x['ModifiedDuration'] * x['MarketValue_INR'] / total_mv).sum()).reindex(order).fillna(0)
    return out.reset_index(name='KRD')
