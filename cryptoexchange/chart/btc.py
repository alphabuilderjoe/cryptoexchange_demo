import io
import requests
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool, ResizeTool, SaveTool
from bokeh.models.widgets import TextInput, Button
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox
from time import gmtime, strftime
from time import mktime
from datetime import datetime

base_url = 'https://api.coindesk.com/v1/bpi/'
data = ColumnDataSource(dict(time=[], price=[]))
current_url = base_url + 'currentprice.json'


def get_last_price():
    
    #current_json = base_url + 'currentprice.json'
    
    raw = requests.get('https://blockchain.info/ticker')
    raw = io.BytesIO(raw.content)
    prices_df = pd.read_json(raw)
    #prices_df = pd.read_json('https://blockchain.info/ticker')
    print("Get last price called")
    last_price = prices_df["USD"]["last"]
    last_time = datetime.fromtimestamp(mktime(gmtime()))
    

    return (last_price, last_time)

def update_ticker():

    ticker = ticker_textbox.value

    data.data = dict(time=[], price=[])
    return

def update_price():
    last_price, last_time = get_last_price()

        
    data.stream(dict(time=[last_time], price=[last_price]), 10000)
    print("Price updated last price {} last time {}".format(last_price, last_time))
    print(data.data)
    return



hover = HoverTool(tooltips=[
    ("Time", "@time"),
    ("BTC Real-Time Price", "@price")
    ])


price_plot = figure(plot_width=800,
                    plot_height=400,
                    #x_axis_type='datetime',
                    tools=[hover, ResizeTool(), SaveTool()],
                    title="Real-Time Price Plot")

price_plot.line(source=data, x='time', y='price')
price_plot.xaxis.axis_label = "Time"
price_plot.yaxis.axis_label = "BTC Real-Time Price"
price_plot.title.text = "BTC Real Time Price" 

ticker_textbox = TextInput(placeholder="Ticker")
update = Button(label="Update")
update.on_click(update_ticker)

inputs = widgetbox([ticker_textbox, update], width=200)

curdoc().add_root(row(inputs, price_plot, width=1600))
curdoc().title = "Real-Time Price Plot BTC"
curdoc().add_periodic_callback(update_price, 1000)