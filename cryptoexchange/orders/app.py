"""
Example python app with the Flask framework: http://flask.pocoo.org/
"""

from os import environ

from flask import Flask, request
from flask import render_template


#ORDER MATCHING ENGINE BEGINS#############################################################################################

import pandas as pd

order_structure = ["OrderID","UserID","BS", "Size", "Ticker", "OrderPrice"]
fill_structure = ["FillID","UserID","BS", "FillSize", "Ticker", "FillPrice", "MarketValue"]

starting_cash = 1000000.00

openbuys_df = pd.DataFrame([], columns=order_structure)
opensells_df = pd.DataFrame([], columns=order_structure)
filled_buys = pd.DataFrame([], columns=fill_structure)
filled_sells = pd.DataFrame([], columns=fill_structure)
trader_list = []

order_id = []
next_order_id = 1000



def create_trader(trader_id,cash,position):

    global trader_list
    
    trader_id = int(trader_id)
    if len(trader_list) == 0:
        trader_list.append([trader_id, starting_cash, position])
        reply = "Trader ID {} created successfully.".format(trader_id)
        
    else:
        trader_col1 = [item[0] for item in trader_list]
        if trader_id not in trader_col1:
            trader_list.append([trader_id, starting_cash, position])
            reply = "Trader ID {} created successfully.".format(trader_id)
        else:
            reply = "Trader ID {} already taken.".format(trader_id)
        
    print(reply)
    return reply

def _update_trader_filled(trader_id, buy_sell, fill_size, fill_price):
    if buy_sell == "B":
        for trader in trader_list:
            if trader[0] == trader_id:
                trader[1] -= fill_size*fill_price
                trader[2] += fill_size
    if buy_sell == "S":
        for trader in trader_list:
            if trader[0] == trader_id:
                trader[1] += fill_size*fill_price
                trader[2] -= fill_size
         

def _sort_orderbook():
    global opensells_df, openbuys_df
    
    if not opensells_df.empty:
        opensells_df.sort_values("OrderPrice",ascending=True, inplace=True)
            
    if not openbuys_df.empty:
        openbuys_df.sort_values("OrderPrice",ascending=False, inplace=True)
        openbuys_df.reset_index(drop=True)
        #openbuys_df = openbuys_df[["OrderID", "UserID", "BS", "Size", "Ticker", "OrderPrice"]]


#RPC function for traders to add_orders to order book
def add_order(trader_id,buy_sell,size,ticker,order_price):
    #trader_id,buy_sell,size,ticker,order_price = s.upper().split(" ")
    trader_id = int(trader_id)
    initial_size = size

    size = float(size)
    order_price = float(order_price)
    
    global openbuys_df, opensells_df, filled_buys, filled_sells
    global next_order_id
    

    #Checking valid trader user id
    if len(trader_list) == 0:
      res = "Error: No traders created yet"
      return "Error: No traders created yet"
        
    else:
        trader_col1 = [item[0] for item in trader_list]
        if trader_id not in trader_col1:
          res = "Error: Trader ID {} not found.".format(trader_id)
          return "Error: Trader ID {} not found.".format(trader_id)


    
    #Handling a buy order
    if buy_sell == "B":
        if opensells_df.empty:
            openbuys_df = openbuys_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index=order_structure), ignore_index = True)
            next_order_id += 1
            print("No offers in market so new buy order for {} lots placed at {}".format(size,order_price))

            
        else:
            opensells_df.sort_values("OrderPrice",ascending=True, inplace=True)
            if order_price < opensells_df["OrderPrice"].iloc[0]:
                
                openbuys_df = openbuys_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index=order_structure), ignore_index=True)
                next_order_id += 1
                print("No matching offer so new buy order for {} lots placed at {}".format(size,order_price))
            else:
                counter = 0
                while (size > 0):
                    if opensells_df.empty:
                        openbuys_df = openbuys_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index=order_structure), ignore_index = True)
                        next_order_id += 1
                        print("No offers in market so new buy order for {} lots placed at {}".format(size,order_price))
                        size = 0
                    
                    elif (order_price >= opensells_df["OrderPrice"].iloc[0]):
                        if (size >= opensells_df["Size"].iloc[0]):
                            print("Buy order size larger or equal to size of best offer now.")
                            fill_size = float(opensells_df["Size"].iloc[0])
                            fill_price = float(opensells_df["OrderPrice"].iloc[0])
                            filled_buys = filled_buys.append(pd.Series([(next_order_id*10+counter),trader_id,buy_sell,fill_size,ticker,fill_price,fill_size*fill_price], index=fill_structure), ignore_index=True)
                            
                            _update_trader_filled(trader_id, buy_sell, fill_size, fill_price)
                            
                            
                            filled_sells = filled_sells.append(pd.Series([(opensells_df["OrderID"].iloc[0]*10+counter),
                                                 opensells_df["UserID"].iloc[0],
                                                 "S",fill_size,
                                                 opensells_df["Ticker"].iloc[0],
                                                 fill_price, fill_size*fill_price], index=fill_structure), ignore_index = True)
                            _update_trader_filled(opensells_df["UserID"].iloc[0], "S", fill_size, fill_price)
                            size = size - fill_size
                            opensells_df.drop(opensells_df.index[0], inplace=True)
                            if not opensells_df.empty:
                                opensells_df.sort_values("OrderPrice",ascending=True, inplace=True)
                            counter += 1
                            print("Bought {} units at {}".format(fill_size,fill_price))
                            print("Still working buy for {} units at {}".format(size,order_price))
                        else:
                            print("Buy order size smaller than size of best offer now.")
                            prev_offer_size = opensells_df["Size"].iloc[0]
                            fill_size = size
                            size = 0
                            fill_price = opensells_df["OrderPrice"].iloc[0]
                            filled_buys = filled_buys.append(pd.Series([(next_order_id*10+counter),trader_id,buy_sell,fill_size,ticker,fill_price, fill_size*fill_price], index=fill_structure), ignore_index=True)
                            
                            _update_trader_filled(trader_id, buy_sell, fill_size, fill_price)
                            filled_sells = filled_sells.append(pd.Series([(opensells_df["OrderID"].iloc[0]*10+counter),
                                                 opensells_df["UserID"].iloc[0],
                                                 "S",fill_size,
                                                 opensells_df["Ticker"].iloc[0],
                                                 fill_price, fill_size * fill_price], index=fill_structure), ignore_index=True)               
                            _update_trader_filled(opensells_df["UserID"].iloc[0], "S", fill_size, fill_price)
                            opensells_df.at[0, "Size"]  = float(prev_offer_size) - float(fill_size)
                    else:
                        openbuys_df = openbuys_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index=order_structure), ignore_index=True)
                        next_order_id += 1
                        print("No matching offer so new buy order for {} lots placed at {}".format(size,order_price))
                        size = 0
                    
    #Handling a sell order
    if buy_sell == "S":
        if openbuys_df.empty:
            opensells_df = opensells_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index = order_structure), ignore_index=True)
            print("No bids in market so new sell order for {} lots placed at {}".format(size,order_price))
            next_order_id += 1

            
        else:
            openbuys_df.sort_values("OrderPrice",ascending=False, inplace=True)
            if order_price > openbuys_df["OrderPrice"].iloc[0]:
                
                opensells_df = opensells_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index = order_structure), ignore_index=True)
                next_order_id += 1
                print("No matching bid so new sell order for {} lots placed at {}".format(size,order_price))
            else:
                counter = 0
                while (size > 0) :
                    if openbuys_df.empty:
                        opensells_df = opensells_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index = order_structure), ignore_index=True)
                        print("No bids in market so new sell order for {} lots placed at {}".format(size,order_price))
                        next_order_id += 1
                        size = 0
                    
                    elif (order_price <= openbuys_df["OrderPrice"].iloc[0]):
                        if (size >= openbuys_df["Size"].iloc[0]):
                            print("Sell order size larger or equal to size of best bid now.")
                            fill_size = float(openbuys_df["Size"].iloc[0])
                            
                            fill_price = float(openbuys_df["OrderPrice"].iloc[0])
                            filled_sells = filled_sells.append(pd.Series([(next_order_id*10+counter),trader_id,buy_sell,fill_size,ticker,fill_price, fill_size*fill_price], index = fill_structure), ignore_index=True)
                            
                            _update_trader_filled(trader_id, buy_sell, fill_size, fill_price)
                           
                            
                            
                            filled_buys = filled_buys.append(pd.Series([(openbuys_df["OrderID"].iloc[0]*10+counter),
                                                 openbuys_df["UserID"].iloc[0],
                                                 "B",fill_size,
                                                 openbuys_df["Ticker"].iloc[0],
                                                 fill_price, fill_size*fill_price], index=fill_structure), ignore_index=True)
        
                            _update_trader_filled(openbuys_df["UserID"].iloc[0], "B", fill_size, fill_price)

                            size = size - fill_size
                            print("Adjusted balance size")
                            openbuys_df.drop(openbuys_df.index[0], inplace=True)
                            counter += 1
                            print("Sold {} units at {}".format(fill_size,fill_price))
                            print("Still working sell for {} units at {}".format(size,order_price))
                            
                            if not openbuys_df.empty:
                                openbuys_df.sort_values("OrderPrice",ascending=False, inplace=True)
                        else:
                            print("Sell order size smaller than size of best bid now.")
                            prev_bid_size = openbuys_df["Size"].iloc[0]
                            fill_size = size
                            size = 0
                            fill_price = openbuys_df["OrderPrice"].iloc[0]
                            filled_sells = filled_sells.append(pd.Series([(next_order_id*10+counter),trader_id,buy_sell,fill_size,ticker,fill_price, fill_size*fill_price], index = fill_structure), ignore_index=True)
                            _update_trader_filled(trader_id, buy_sell, fill_size, fill_price)
                            
                            filled_buys = filled_buys.append(pd.Series([(openbuys_df["OrderID"].iloc[0]*10+counter),
                                                 openbuys_df["UserID"].iloc[0],
                                                 "B",fill_size,
                                                 openbuys_df["Ticker"].iloc[0],
                                                 fill_price, fill_size*fill_price], index = fill_structure), ignore_index = True)      
                            _update_trader_filled(openbuys_df["UserID"].iloc[0], "B", fill_size, fill_price)
                            openbuys_df.at[0, "Size"] = float(prev_bid_size) - float(fill_size)            
                            
                            
                    else:
                        opensells_df = opensells_df.append(pd.Series([next_order_id,trader_id,buy_sell,size,ticker,order_price], index = order_structure), ignore_index=True)
                        next_order_id += 1
                        print("No matching bid so new sell order for {} lots placed at {}".format(size,order_price))
                        size = 0


    res = ("Received order from trader {}, to {} {} lots of {} at {}".format(trader_id, buy_sell, initial_size, ticker, order_price))
    
    _sort_orderbook()
    return res


def show_all_status():
    _sort_orderbook()
    
    print("Open sells:")
    print(opensells_df)
    print("Open buys:")
    print(openbuys_df)
    print("Filled sells:")
    print(filled_sells)
    print("Filled buys:")
    print(filled_buys)    
    print("")
    for trader in trader_list:
        print("Trader ID : {}, Cash : {}, Bitcoin : {}".format(trader[0], trader[1], trader[2]))


def trader_exists_index(trader_id):
    if len(trader_list) == 0:
        return -1
    else:
        trader_col1 = [item[0] for item in trader_list]
        trader_id = int(trader_id)
        
        print(trader_col1)
        print(trader_col1[0])
        if trader_id not in trader_col1:
        
            return -1
        else:
            trader_index = trader_col1.index(trader_id)
            return trader_index
  











#RPC function for traders to cancel_orders in order book
#Exact same syntax as placing an order
def cancel_order(trader_id,buy_sell,size,ticker,order_price):
    
    trader_id = int(trader_id)
    size = float(size)
    order_price = float(order_price)
    global openbuys_df, opensells_df
    cancel_status = ""
    
    if buy_sell == "B":
        if not (((openbuys_df.loc[openbuys_df["UserID"] == trader_id]).loc[openbuys_df["Size"] == size]).loc[openbuys_df["OrderPrice"] == order_price]).empty :
            id_to_delete = int((((openbuys_df.loc[openbuys_df["UserID"] == trader_id]).loc[openbuys_df["Size"] == size]).loc[openbuys_df["OrderPrice"] == order_price])["OrderID"])
            openbuys_df = openbuys_df[openbuys_df["OrderID"] != id_to_delete]
            print("Succesfully deleted")
            cancel_status = "Succesfully deleted"
        else:
            print("Order not found")
            cancel_status = "Order not found"
            
    if buy_sell == "S":
        if not (((opensells_df.loc[opensells_df["UserID"] == trader_id]).loc[opensells_df["Size"] == size]).loc[opensells_df["OrderPrice"] == order_price]).empty :
            id_to_delete = int((((opensells_df.loc[opensells_df["UserID"] == trader_id]).loc[opensells_df["Size"] == size]).loc[opensells_df["OrderPrice"] == order_price])["OrderID"])
            opensells_df = opensells_df[opensells_df["OrderID"] != id_to_delete]
            print("Succesfully deleted")
            cancel_status = "Succesfully deleted"
        else:
            print("Order not found")
            cancel_status = "Order not found"
    return cancel_status
        

#ORDER MATCHING ENGINE END############################################################################################





app = Flask(__name__)


@app.route('/')
def indexshortcut():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/createtraderform')
def createtraderform():
    return render_template('createtraderform.html')    
            
@app.route('/createtrader', methods=['POST'])
def createtrader():
        
    user_id = request.form['userID']
    user_id = int(user_id)
    trader_index = trader_exists_index(user_id)
    if trader_index != -1: #trader already exists
        print("trader already exists")
        return render_template('createtradererror.html', res=user_id)
    else:
        cash = request.form['cash']
        position = request.form['position']
        cash = float(cash)
        position = float(position)
        
        create_trader(user_id, cash, position)
        show_all_status()
        
        return render_template('createtrader.html', user_id=user_id)


@app.route('/orderform')
def orderform():
    return render_template('orderform.html')    
						
@app.route('/submitorder', methods=['POST'])
def submitorder():
  user_id = request.form['userID']
  b_s = request.form['buy_sell']
  size = request.form['size']
  ticker = request.form['ticker']
  order_price = request.form['order_price']
  
  res = add_order(user_id, b_s, size, ticker, order_price)
  show_all_status()
  return render_template('submitorder.html', res=res)



@app.route('/cancelform')
def cancelform():
    return render_template('cancelform.html')    
            
@app.route('/cancelorder', methods=['POST'])
def cancelorder():
  user_id = request.form['userID']
  b_s = request.form['buy_sell']
  size = request.form['size']
  ticker = request.form['ticker']
  order_price = request.form['order_price']
  print ("Cancelling order from trader {}, to {} {} lots of {} at {}".format(user_id, b_s, size, ticker, order_price))
  res = cancel_order(user_id, b_s, size, ticker, order_price)
  show_all_status()

  return render_template('cancelorder.html', res=res)




						   
@app.route('/viewtraderstatus')
def viewtraderstatus():
    return render_template('viewtraderstatus.html')

@app.route('/viewtraderstatusresult', methods=['POST'])
def viewtraderstatusresult():
    user_id = request.form['userID']
    user_id = int(user_id)
    trader_index = trader_exists_index(user_id)
    print("Trader Index : {}".format(trader_index))
    
    if trader_index == -1: #trader doesn't exists
        return render_template('viewtraderstatuserror.html', res=user_id)
    else:       
        trader_df = pd.DataFrame([trader_list[trader_index]], columns=["TraderID", "Cash", "Position"])

        new_opensells_df = opensells_df.loc[opensells_df['UserID'] == user_id]
        
        print(opensells_df['UserID'] == user_id)
        print(opensells_df.loc[opensells_df['UserID'] == user_id])
        
        
        new_openbuys_df = openbuys_df.loc[openbuys_df['UserID'] == user_id]
        new_filledsells_df = filled_sells.loc[filled_sells['UserID'] == user_id]
        new_filledbuys_df = filled_buys.loc[filled_buys['UserID'] == user_id]
        
        return render_template('viewtraderstatusresult.html',tables=[trader_df.to_html(), new_opensells_df.to_html(), new_openbuys_df.to_html(), new_filledsells_df.to_html(), new_filledbuys_df.to_html()],
    titles = ['na', 'Trader Status', 'Sell orders', 'Buy orders', 'Filled sell orders', 'Filled buy orders'])




@app.route('/viewallstatus')
def viewallstatus():
    trader_df = pd.DataFrame(trader_list, columns=["TraderID", "Cash", "Position"])
    #


    return render_template('viewallstatus.html',tables=[trader_df.to_html(), opensells_df.to_html(), openbuys_df.to_html(), filled_sells.to_html(), filled_buys.to_html()],
    titles = ['na', 'Trader Statuses', 'Sell orders', 'Buy orders', 'Filled sell orders', 'Filled buy orders'])



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(environ.get('PORT', 5020))
    app.run(host='0.0.0.0', port=port)














