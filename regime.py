import matplotlib
matplotlib.use('TkAgg')
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from hmmlearn import hmm

# Configuration
plt.style.use('ggplot')
plt.rcParams['font.family'] = 'DejaVu Sans'
np.random.seed(42)

# Ticker Configuration
PREDICTORS = ['^VIX', 'GC=F', 'EURUSD=X', '^TNX']
TARGET = '^GSPC'

def get_sp500_dates():
    """Get S&P 500 trading days without timezone"""
    df = yf.Ticker(TARGET).history(period="max", start="2016-01-01", end="2023-01-01")
    dates = df.index.tz_localize(None).normalize()  # Convert to naive datetime
    print(f"📅 S&P 500 trading days: {len(dates)}")
    return dates

def fetch_aligned_data(sp500_dates):
    """Fetch data aligned to S&P 500 dates with validation"""
    data = {}
    start_date = sp500_dates[0].strftime('%Y-%m-%d')
    end_date = sp500_dates[-1].strftime('%Y-%m-%d')
    
    # Fetch target
    target = yf.Ticker(TARGET).history(start=start_date, end=end_date)
    target.index = target.index.tz_localize(None)
    data['TARGET'] = target['Close'].reindex(sp500_dates).ffill().bfill()
    
    # Fetch and align predictors
    for ticker in PREDICTORS:
        try:
            df = yf.Ticker(ticker).history(start=start_date, end=end_date)
            df.index = df.index.tz_localize(None)
            aligned = df['Close'].reindex(sp500_dates).ffill().bfill()
            key = f"PRED_{ticker.replace('^','').replace('=','_')}"
            data[key] = aligned
            print(f"✅ {key}: {aligned.notna().sum()}/{len(aligned)} valid values")
        except Exception as e:
            print(f"❌ Error processing {ticker}: {str(e)}")
            raise
    
    combined = pd.DataFrame(data).dropna()
    print(f"\n📊 Final dataset: {len(combined)} days")
    return combined

def main():
    # 1. Get S&P 500 dates
    print("\n🔍 Fetching S&P 500 calendar (2016-2023)...")
    sp500_dates = get_sp500_dates()
    
    # 2. Fetch and align data
    print("\n📥 Aligning data to S&P dates...")
    price_df = fetch_aligned_data(sp500_dates)
    
    # 3. Calculate returns
    print("\n📈 Calculating returns...")
    returns_df = price_df.pct_change().dropna()
    
    # 4. Train HMM
    print("\n🎯 Training HMM...")
    model = hmm.GaussianHMM(
        n_components=3,
        covariance_type="full",
        n_iter=1000,
        random_state=42
    )
    model.fit(returns_df.filter(like='PRED_').values)
    returns_df['Regime'] = model.predict(returns_df.filter(like='PRED_').values)
    
    # 5. Visualize
    print("\n🎨 Generating visualization...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)
    
    # Price plot
    ax1.plot(price_df.index, price_df['TARGET'], color='navy', lw=1)
    ax1.set_ylabel('S&P 500 Price')
    ax1.grid(alpha=0.3)
    
    # Regime plot
    colors = ['green', 'blue', 'red']
    for regime in range(3):
        mask = returns_df['Regime'] == regime
        ax2.scatter(returns_df.index[mask], 
                   returns_df['TARGET'][mask],
                   color=colors[regime],
                   s=30,
                   label=f'Regime {regime}')
    ax2.set_ylabel('Daily Returns')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.suptitle('S&P 500 Market Regimes (2016-2023)')
    plt.tight_layout()
    plt.savefig('sp500_regimes.png', dpi=300)
    plt.show()

    # 6. Statistics
    print("\n📊 Regime Statistics:")
    stats = returns_df.groupby('Regime').agg({
        'TARGET': ['mean', 'std', 'count'],
        **{col: 'mean' for col in returns_df.filter(like='PRED_').columns}
    })
    print(stats.to_markdown(floatfmt=".4f"))

if __name__ == "__main__":
    main()