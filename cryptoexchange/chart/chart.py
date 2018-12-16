from flask import Flask, render_template, request
from bokeh.embed import components

app = Flask(__name__)


#coindesk price API
import requests
import datetime
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from pandas import DataFrame
import time


#/////////////////////////////////Chart Plotting///////////////////////////////////////

now = datetime.datetime.now()
base_url = 'https://api.coindesk.com/v1/bpi/'

# coindesk historical price
end_date = now.strftime("%Y-%m-%d")
historial_url = base_url + 'historical/close.json?start=2010-07-17&end=' + end_date

# coindesk current price update
current_url = base_url + 'currentprice.json'

#manipulating the historical prices
resp = requests.request("GET", historial_url).json()
# print(type(resp))
keys = []
for key, value in resp.items() :
    keys.append(key)
# print (keys)
# for key in keys:    
#     print key +" " + str(len(resp[key]))

bpiusd_hist = resp['bpi']
# print(len(bpiusd_hist))
# print(type(bpiusd_hist))

dataset = []
for key in sorted(bpiusd_hist.keys()):
#     print "%s: %s" % (key, bpiusd_hist[key])
    row = [key, bpiusd_hist[key]]
    dataset.append(row)

# print dataset

#converting dict(row by row) into a np array for plotting purposes
date = []
close = []
# for key, value in dataset[0].items() :
#     date.append(key)
#     close.append(value)
    


# df = pd.DataFrame(data = dataset, columns=['date', 'close'])

date = [i[0] for i in dataset]
close = [i[1] for i in dataset]

bpiusd_dates = np.array(date, dtype=np.datetime64)
bpiusd_close = np.array(close, dtype=np.float)


# plot bitcoin/USD prices
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, Slider, Select
from bokeh.plotting import curdoc, figure, output_file, show
from bokeh.driving import count

window_size = 30
window = np.ones(window_size)/float(window_size)

# output to static HTML file
# output_file("/assignment3.html", title="isabelle_assignment_price_websocket.py example")

# create a new plot with a datetime axis type
p = figure(width=800, height=350, x_axis_type="datetime")

# add renderers
p.line(bpiusd_dates,bpiusd_close, color='darkgrey', legend='close')

# customize by setting attributes
p.title.text = "Bitcoin/USD Daily Closing Price"
p.legend.location = "top_left"
p.grid.grid_line_alpha = 0
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Price'
p.ygrid.band_fill_color="blue"
p.ygrid.band_fill_alpha = 0.1

# show the results
show(p)




# //////////////////////Flask///////////////////////////////////////
# Index page
@app.route('/index')
def index():
	# Determine the selected feature
	current_feature_name = request.args.get("feature_name")
	if current_feature_name == None:
		current_feature_name = "Sepal Length"

	# Create the plot
	# plot = create_figure(current_feature_name, 10)
		
	# Embed plot into HTML via Flask Render
	script, div = components(p)
	return render_template("chart.html", script=script, div=div,
		feature_names=feature_names,  current_feature_name=current_feature_name)



@app.route('/analysis/news')
def analysis(news):
    # x = pd.DataFrame(np.random.randn(20, 5))
    return render_template("news.html", name=news, data=g_df)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=5000, debug=True)

