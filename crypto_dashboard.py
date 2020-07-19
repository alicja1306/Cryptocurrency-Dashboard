import pandas as pd
import numpy 
import requests
import datetime
import plotly.express as px
import plotly.graph_objs as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State


url = requests.get('https://min-api.cryptocompare.com/data/top/mktcapfull?limit=50&tsym=USD')
data = url.json()

coininfo = [] 
for item in data["Data"]:
    coininfo.append(item["CoinInfo"])  
    
    
names = [] 
for item in coininfo:
    names.append(item["Name"])  

app = dash.Dash()

df = pd.DataFrame() 
def get_data(crypto):
    crypto_data = []
    url = requests.get(f'https://min-api.cryptocompare.com/data/v2/histoday?fsym={crypto}&tsym=USD&allData=true')
    page = url.json()['Data']['Data']
    close_data = list(map(lambda x:x['close'], page))
    crypto_data.append(close_data)
    df[crypto] = crypto_data[0]

for name in names:
    get_data(name)

# adding a timestamp
time = []
page = requests.get(f'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&allData=true')
data = page.json()['Data']['Data']
timestamp = list(map(lambda x:x['time'], data))
time.append(timestamp)    

df['time'] = time[0]
df['time'] = [datetime.datetime.fromtimestamp(d) for d in df.time]

df.set_index('time',inplace=True) 
df.index = df.index.normalize()
   
feautures = df.columns   

text = 'Dashboard that allows users to monitor and compare historical prices of top 50 cryptocurrencies.'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = {
    'background': '#0d0d0d',
    'text': '#ffffff',
    'text2': '#000000',
    'dropdown': '#262626'
}

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

app.layout = html.Div(style={'backgroundColor': colors['background'] ,'color': colors['text'],'padding-left':24, 'padding-top':72, 'padding-bottom':72},
    children=[
        html.Div(className='row', children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('CRYPTOCURRENCY DASHBOARD'), 
                                 html.P(text),
                                 html.P('Pick one or more cryptocurrencies from the dropdown below.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='crypto_selector', options=[{'label':i,'value':i}for i in feautures],
                                                      multi=True, value=['BTC','XRP'],
                                                      style={'backgroundColor': colors['dropdown'], 'color': colors['text2'],'marginTop': 24, 'marginBottom': 24},
                                                     )]),
                                 
                                 html.Div([
                                 html.P('Select a start and end date:'),
                                 dcc.DatePickerRange(id='my_date_picker',
                                 min_date_allowed=df.index[0],
                                 max_date_allowed = df.index[-1],
                                 start_date = df.index[-1000],
                                 end_date = df.index[-1])]),
                                 
                                 html.Div([
                                 html.Button(id='submit-button',
                                 n_clicks=0,
                                 children = 'Submit',
                                 style={'color':'white','marginTop':24}
                                )])]),
            
                    html.Div(className='eight columns div-for-charts bg-grey',
                            children=[
                                dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True)
                             ])])])

@app.callback(Output('timeseries','figure'),
              [Input('submit-button','n_clicks')],
              [State('crypto_selector','value'),
               State('my_date_picker','start_date'),
               State('my_date_picker','end_date')
               ])

def update_graph(n_clicks, crypto_ticker, start_date, end_date):
    start= start_date
    end= end_date
   
    traces = []
    for crypto in crypto_ticker:
        data = df.loc[start:end,:]
        traces.append({'x': data.index,'y': data[crypto],'name': crypto})
        
    fig = {'data': traces,
           'layout': go.Layout(
                   colorway=['#ffffb3', '#99ffbb', '#ff5050', '#4da6ff', '#df80ff', '#ff794d'],
                   template='plotly_dark',
                   margin=dict(l=10, r=10, t=50, b=100),
                   height=700
          )}
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
