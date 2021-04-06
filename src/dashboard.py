import os
import io
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from google.cloud import secretmanager


@st.cache
def get_crypto_compare_api_key():
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(
        request={"name": os.environ.get('SECRET_NAME')})
    return response.payload.data.decode("UTF-8")


@st.cache
def fetch_historical_quote(instrument, timestamp):
    dt = datetime.combine(timestamp, datetime.min.time())
    headers = {'authorization': 'Apikey ' + get_crypto_compare_api_key()}
    term, base = instrument.split('-')
    full_url = \
        f"https://min-api.cryptocompare.com/data/pricehistorical?fsym={term}&tsyms={base}&ts={str(dt.timestamp())}"
    historical_quote = requests.get(full_url, headers=headers).content.decode('utf-8')
    return json.loads(historical_quote)


@st.cache
def fetch_quote(instrument):
    quote_url = f"https://api.uphold.com/v0/ticker/{instrument}"
    quote_json = requests.get(quote_url).content.decode('utf-8')
    return json.loads(quote_json)


@st.cache
def fetch_asset_list():
    ticker_url = "https://api.uphold.com/v0/assets"
    ticker_json = json.loads(requests.get(ticker_url).content.decode('utf-8'))
    return sorted([item['code'] for item in ticker_json if item['type'] in ['cryptocurrency', 'utility_token']])


def build_portfolio():
    if portfolio_name == 'explore':
        base_investment = float(
            st.sidebar.slider('Investment CHF/asset: ', 100, 5000, 500, 100))
        asset_list = fetch_asset_list()
        monitoring = ('BTC', 'DOGE', 'XRP', 'ETH', 'LTC', 'DOT', 'SOL')
        exploratory_assets = st.sidebar.multiselect('Select assets', asset_list, default=monitoring)
        portfolio_open_date = st.sidebar.date_input('Portfolio opening date:')
        portfolio = pd.DataFrame()
        if len(exploratory_assets) == 0:
            st.stop()
        for asset in exploratory_assets:
            instrument_name = f"{asset}-CHF"
            quote = fetch_historical_quote(instrument_name, portfolio_open_date)
            if float(quote[asset]['CHF']) == 0:
                st.text(f"No historical data available for {asset}")
                continue
            portfolio = portfolio.append(
                pd.DataFrame({'amount': base_investment / float(quote[asset]['CHF']), 'value': base_investment,
                              'direction': 'long'}, index=[instrument_name]))

        return portfolio
    else:
        url = st.experimental_get_query_params().get('portfolio_url')[0]
        s = requests.get(url).content
        return pd.read_csv(io.StringIO(s.decode('utf-8')), header=0, index_col=0)


def valuate_asset(asset):
    quote = fetch_quote(asset)
    if 'code' in quote.keys():
        st.text(f"asset -> {asset} Not found")
        return
    asset_entry = portfolio.loc[portfolio.index == asset]
    quote_part = 'bid'
    if asset_entry['direction'][0] == 'long':
        quote_part = 'ask'

    position_size = asset_entry['amount'][0]
    return [asset, pd.Series(position_size * float(quote[quote_part]), name='value')]


def valuate_portfolio(portfolio):
    total = pd.DataFrame()
    for asset in portfolio.index:
        asset, valuation = valuate_asset(asset)
        total[asset] = valuation

    total = total.T
    total.columns = ['value']
    return total


st.title('Crypto portfolio valuation and exploration')

if st.experimental_get_query_params().get('portfolio_url'):
    portfolio_name = st.sidebar.selectbox("Pick portfolio: ", ('portfolio', 'explore'))
else:
    portfolio_name = 'explore'

portfolio = build_portfolio()
portfolio_cost = int(portfolio.get('value').sum())

evaluated_portfolio = valuate_portfolio(portfolio)

st.text(f"Portfolio current value in CHF: {'%.2f' % evaluated_portfolio.get('value').sum()}")

portfolio_value = evaluated_portfolio.get('value').sum()
st.text(f"P&L: CHF {'%.2f' % (portfolio_value - portfolio_cost)}" +
        f"({'%.2f' % ((portfolio_value - portfolio_cost) / portfolio_cost * 100)}%)")

st.text('Portfolio')
st.dataframe(portfolio)
st.text('Per asset in CHF')
st.dataframe(evaluated_portfolio)
