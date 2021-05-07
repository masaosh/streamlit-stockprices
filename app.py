import pandas as pd
import yfinance as yf
import streamlit as st
import altair as alt

st.title("株価チャートアプリ")
st.sidebar.write("""
# 株価
以下のオプションから表示日数を指定
""") 

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.slider("日数を指定してください",1,180,50)

st.write(f"""
## 過去 **{days}日間** の株価
""")

@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try:
    tickers = {
        'apple': 'AAPL',
        'facebook': 'FB',
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days=days, tickers=tickers)

    st.sidebar.write("""
    ## 株価範囲指定
    """)
    ymin, ymax = st.sidebar.slider("株価の範囲を指定してください",0.0 ,3500.0, (0.0,3500.0))

    companies = st.multiselect(
        "銘柄を選択してください",
        list(df.index),
        ['google','amazon','facebook','apple']
    )

    if not companies:
        st.error("1つ以上の銘柄を選んでください")
    else:
        data = df.loc[companies]
        st.write("""## 株価 (USD)""", data.sort_index())
        #show graph
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(columns={'value': 'Stock Prices(USD)'})

        chart = (
            alt.Chart(data).mark_line(opacity=0.8, clip=True).encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin,ymax])),
                color="Name:N"
            )
        )
        st.altair_chart(chart, use_container_width=True)

except:
    st.error("内部エラーが発生しました")
