import logging
import sys
import api_data
import requests
import asyncio, signal, functools
from rich.logging import RichHandler


if 'win32' in sys.platform:
	# Windows specific event-loop policy & cmd
	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


SLEEP_INTERVAL = 3 # this sets the interval to check for new open positions (every n seconds)

#===============================================================================
# env args
#===============================================================================
ENVARGS = []
if len(sys.argv) >= 1:
	for n in range(1,len(sys.argv)):
		ENVARGS.append(sys.argv[n])
if "-h" in ENVARGS:
	print( "for testnet use 'TEST' on the parameters")
	print( "for any symbol other than BTC, it should be specified on the arguments")
	print( "to limit losses to a fixed amount of usdt put the number in parameters, i.e:")
	print( "autostoplimit.py xrp 100")
	print( "to limit losses to a %  amount of the position size use the number in paramenters, i.e:")
	print( "autostoplimit.py eth 10%")
	quit()
#===============================================================================
# env args end
#===============================================================================


#===============================================================================
# logger setup
#===============================================================================
logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
# handler = logging.StreamHandler()
test = RichHandler()
# test.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
# logger.addHandler(handler)
logger.addHandler(test)
# formatter = logging.Formatter('\x1b[80D\x1b[1A\x1b[K%(message)s')
# add formatter to console handler
# logger.setFormatter(formatter)
#===============================================================================
# logger setup end 
#===============================================================================

#########################
# testnet vs main account
#########################
from binance_f.model import *
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.base.printobject import *
from binance_f import RequestClient as rc 


if "TEST" in ENVARGS:
	api_key = api_data.binancetestnet["apiKey"]
	secret_key = api_data.binancetestnet["secret"]
	logger.info("using TESTNET credentials")
	shortname = "BINFUTTESTNET"
	base = "https://testnet.binancefuture.com"
	
else:
	api_key = api_data.binance["apiKey"]
	secret_key = api_data.binance["secret"]
	logger.info("using MAIN ACCOUNT credentials")
	shortname = "BINFUT"
	base = "https://fapi.binance.com"




request_client = rc(api_key=api_key, secret_key=secret_key,url=base)



def assetQuantityPrecision(symbol,value=2):
	for s in exchange_info["symbols"]:
		if s["symbol"] == symbol:
			value = s["quantityPrecision"]
			break

	return value

def assetPricePrecision(symbol,value=2):
	for s in exchange_info["symbols"]:
		if s["symbol"] == symbol:
			value = s["pricePrecision"]
			# print(symbol,value)
			break
	return value

def assetTickSize(symbol):
	for s in exchange_info["symbols"]:
		if s["symbol"] == symbol:
			sfilter = s["filters"]
			for f in sfilter:
				if f["filterType"] == "PRICE_FILTER":
					tickSize = f["tickSize"]

			break
	return float(tickSize)



exchange_info = requests.get(base+"/fapi/v1/exchangeInfo",timeout=10)
ei =exchange_info.json()
exchange_info = ei

#===============================================================================
# identify working symbol and amount from ENVARGS
#===============================================================================

symbols = [s["symbol"] for s in exchange_info["symbols"]]
main_symbol = False
order_amount = False
losslimit = False
percentagemode = False

for e in ENVARGS:
	if type(e) == str and e.upper() in symbols: 
		logger.info("working symbol: %s" % e.upper())
		main_symbol = e.upper()
		break
	elif type(e) == str and e.upper() + "USDT" in symbols: 
		logger.info("working symbol: %s" % e.upper() + "USDT")
		main_symbol = e.upper() + "USDT"
		break
	
	elif type(e) == str and "%" in e:
		logger.info("using percentage loss limit: %s" % e)
		losslimit = float(e[0:-1])
		try:
			losslimit = float(e[0:-1])
			percentagemode = True
		
		except:
			pass

	try:
		e = float(e)
		logger.info("using fixed loss limit: $ %s" % e)
		losslimit = float(e)

	except:
		pass




if main_symbol == False:
	logger.info("no symbol provided, default to BTCUSDT")
	main_symbol = "BTCUSDT"

aqp = assetQuantityPrecision(main_symbol)
app = assetPricePrecision(main_symbol)

tickSize = assetTickSize(main_symbol)

def error(e: 'BinanceApiException'):
	print(e.error_code + e.error_message)

def createPositionStop(**kwargs):
	amount = kwargs["actual_amount"]
	liquidationPrice=  kwargs["liquidationPrice"]
	symbol = kwargs["main_symbol"]
	mode = kwargs["mode"]
	entryPrice = kwargs["entryPrice"]
	leverage = kwargs["leverage"]


	try:
		orderside = "BID" if amount < 0 else "ASK"
		sideo = {"BID":OrderSide.BUY,"ASK":OrderSide.SELL}
		vol = float(amount)
		signal = -1 if vol < 0 else 1
		tickmult = 0.01 if liquidationPrice < 1 else 1 ### for currencies with very small prices, use the regular ticksize
		price = float(liquidationPrice) + (tickSize * 100 * signal * tickmult) #base liquidation price
		
		if losslimit != False and percentagemode == True:
			vol = abs(vol)
			losslimitprice = float(entryPrice) + (((float(entryPrice)/100) * (losslimit/leverage)) * (signal*-1))

		elif losslimit != False:
			vol = abs(vol)
			losslimitprice = entryPrice + ((losslimit/vol) * (signal)*-1) #limited loss price
			

		if losslimit != False:

			if signal == 1 and losslimitprice >= price: #sell orders
				price = losslimitprice #losslimit price will not liquidate position
			elif signal == -1 and losslimitprice <= price:
				price = losslimitprice
			else:
				logger.info("loss limit value too big, keeping base liquidation price")

	
		vol = abs(vol)
		p = assetPricePrecision(symbol)
		price = f"{price:0.{p}f}"
		p =  assetQuantityPrecision(symbol)
		vol = f"{vol:0.{p}f}"

		

		############################################
		# check for existing auto stop order
		############################################
		result = request_client.get_open_orders(symbol=main_symbol)
		exists = False

		if losslimit == False:
			typemode = "avoid liquidation fees"
		else:
			symbolm = "%" if percentagemode == True else "$"
			if losslimit > 0:
				typemode = "max loss: " + symbolm + str(losslimit)
			else:
				typemode = "take profit: " + symbolm + str(losslimit*-1)

		extra_name_for_profit = "profit" if losslimit < 0 else ""

		if result != []:
			for p in result:
				if p.clientOrderId == "autostopmarket"+symbol+mode+extra_name_for_profit:
					exists = True
					if p.side == sideo[orderside] and float(p.origQty) == float(vol) and float(p.stopPrice) == float(price):
						logger.info("auto stop order still valid, nothing to update. mode: " + typemode)
					else:
						request_client.cancel_order(symbol,origClientOrderId="autostopmarket"+symbol+mode+extra_name_for_profit)
						logger.info("canceling auto stop order for a update")


		if not exists:
			wt = WorkingType.MARK_PRICE
			if losslimit == False: #avoid liquidation with mark price
				logger.info("creating stop order, liquidation %s, amount %s, stop price %s, %s %s" % (liquidationPrice,vol, price,symbol, sideo[orderside] ))
			else:
				wt = WorkingType.CONTRACT_PRICE #stop market with contract true price
				symbolm = "%" if percentagemode == True else "$"
				if losslimit > 0:
					logger.info("creating stop order, max loss %s %s, amount %s, stop price %s, %s %s" % (symbolm, losslimit,vol, price,symbol, sideo[orderside] ))
				else:
					logger.info("creating take profit order, %s %s, amount %s, stop price %s, %s %s" % (symbolm, (losslimit*-1),vol, price,symbol, sideo[orderside] ))

			
			if mode == PositionSide.BOTH:
				result = request_client.post_order(symbol=symbol, side=sideo[orderside], positionSide=mode,ordertype=OrderType.STOP_MARKET, quantity=vol, stopPrice=price,reduceOnly="true",workingType=wt,newClientOrderId="autostopmarket"+symbol+mode+extra_name_for_profit)#timeInForce="GTX",
			else:
				result = request_client.post_order(symbol=symbol, side=sideo[orderside], positionSide=mode,ordertype=OrderType.STOP_MARKET, quantity=vol, stopPrice=price,workingType=wt,newClientOrderId="autostopmarket"+symbol+mode+extra_name_for_profit)#timeInForce="GTX",
		

	except:
		e = sys.exc_info()
		logger.error("EXCEPTION ERROR - line %s, %s, %s" % (e[-1].tb_lineno, type(e).__name__, e))


async def place_stoporder():
	while True:
		try:
			account = request_client.get_position()
			current_order_price = 0

			for p in account: #positions:
				actual_amount = 0
				if p.symbol == main_symbol:
					# PrintBasic.print_obj(p)
					actual_amount = p.positionAmt
					liquidationPrice = p.liquidationPrice
					mode = PositionSide.BOTH
					entryPrice = p.entryPrice
					leverage = p.leverage


					if p.positionSide == "BOTH":
						logger.info("current OPEN position amount: %s" % actual_amount)
					elif p.positionSide in ["LONG","SHORT"]: #HEDGE mode
						mode = PositionSide.LONG if p.positionSide == "LONG" else PositionSide.SHORT
						logger.info("current %s OPEN position amount: %s" % (p.positionSide, actual_amount))

					if actual_amount != 0:
						kwargs = {"actual_amount":actual_amount,"liquidationPrice":liquidationPrice,"main_symbol":main_symbol,"mode":mode,"entryPrice":entryPrice,"leverage":leverage}
						createPositionStop(**kwargs)
					else:
						logger.info("No OPEN positions, nothing to do!")

		except:
			e = sys.exc_info()
			logger.error("EXCEPTION ERROR - line %s, %s %s" % (e[-1].tb_lineno, type(e).__name__, e))
		finally:
			delay = await asyncio.sleep(SLEEP_INTERVAL)


#===============================================================================
# loop signal handler to exit with ctrl+c
#===============================================================================
def ask_exit(signame):
	logger.info("Got signal %s: exiting" % signame)
	loop.stop()
	try:
		request_client.cancel_order(main_symbol,origClientOrderId="buylimit")
	except:
		pass

loop = asyncio.get_event_loop()
for signame in ('SIGINT', 'SIGTERM'):
	try:
		loop.add_signal_handler(getattr(signal, signame),functools.partial(ask_exit, signame))
	except NotImplementedError:
   		pass  # Ignore if not implemented. Means this program is running in windows.


#===============================================================================
# end of loop signal handler
#===============================================================================

def auto_stop_market():
	asyncio.ensure_future(place_stoporder())  
	logger.info("Event loop running forever, press Ctrl+C to interrupt.")

	try:
		loop.run_forever()
	finally:
		loop.close()

if __name__ == '__main__':
	auto_stop_market()



