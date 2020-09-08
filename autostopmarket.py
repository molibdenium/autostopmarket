import logging
import sys
import api_data
import requests
import asyncio, signal, functools


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
	quit()
#===============================================================================
# env args end
#===============================================================================


#===============================================================================
# logger setup
#===============================================================================
logger = logging.getLogger("binance-futures")
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
#===============================================================================
# logger setup end 
#===============================================================================

#########################
# testnet vs main account
#########################
if "TEST" in ENVARGS:
	api_key = api_data.binancetestnet["apiKey"]
	secret_key = api_data.binancetestnet["secret"]
	from binance_f.model import *
	from binance_f.exception.binanceapiexception import BinanceApiException
	from binance_f.base.printobject import *
	from binance_f import RequestClient as rc 
	from binance_f import SubscriptionClient as sc
	logger.info("using TESTNET credentials")
	shortname = "BINFUTTESTNET"
	base = "https://testnet.binancefuture.com"
	
else:
	api_key = api_data.binance["apiKey"]
	secret_key = api_data.binance["secret"]
	from binance_f_main.constant.test import *
	from binance_f_main.model import *
	from binance_f_main.exception.binanceapiexception import BinanceApiException
	from binance_f_main.base.printobject import *
	from binance_f_main import RequestClient as rc 
	from binance_f_main import SubscriptionClient as sc
	logger.info("using MAIN ACCOUNT credentials")
	shortname = "BINFUT"
	base = "https://fapi.binance.com"

request_client = rc(api_key=api_key, secret_key=secret_key,server_url=base)



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


			# print(symbol,tickSize)
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
for e in ENVARGS:
	if type(e) == str and e.upper() in symbols: 
		logger.info("working symbol: %s" % e.upper())
		main_symbol = e.upper()
		break
	elif type(e) == str and e.upper() + "USDT" in symbols: 
		logger.info("working symbol: %s" % e.upper() + "USDT")
		main_symbol = e.upper() + "USDT"
		break

if main_symbol == False:
	logger.info("no symbol provided, default to BTCUSDT")
	main_symbol = "BTCUSDT"

aqp = assetQuantityPrecision(main_symbol)
app = assetPricePrecision(main_symbol)

tickSize = assetTickSize(main_symbol)

def error(e: 'BinanceApiException'):
	print(e.error_code + e.error_message)

def createPositionStop(amount,liquidationPrice, symbol):
	try:
		orderside = "BID" if amount < 0 else "ASK"
		sideo = {"BID":OrderSide.BUY,"ASK":OrderSide.SELL}
		vol = float(amount)


		signal = -1 if vol < 0 else 1 
		price = float(liquidationPrice) + (tickSize * 100 * signal)
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
		if result != []:
			for p in result:
				if p.clientOrderId == "autostopmarket"+symbol:
					exists = True
					if p.side == sideo[orderside] and float(p.origQty) == float(vol) and float(p.stopPrice) == float(price):
						logger.info("currently auto stop order still valid, nothing to update.")
					else:
						request_client.cancel_order(symbol,origClientOrderId="autostopmarket"+symbol)
						logger.info("canceling auto stop order for a update")


		if not exists:
			logger.info("creating stop order, liquidation %s, amount %s, stop price %s, %s %s" % (liquidationPrice,vol, price,symbol, sideo[orderside] ))
			result = request_client.post_order(symbol=symbol, side=sideo[orderside], ordertype=OrderType.STOP_MARKET, quantity=vol, stopPrice=price, reduceOnly="true",workingType=WorkingType.MARK_PRICE,newClientOrderId="autostopmarket"+symbol)#timeInForce="GTX",
	except:
		e = sys.exc_info()
		logger.error("EXCEPTION ERROR - line %s, %s, %s" % (e[-1].tb_lineno, type(e).__name__, e))


async def place_stoporder():

	while True:
		try:
			account = request_client.get_position()
			current_order_price = 0

			for p in account:#.positions:
				if p.symbol == main_symbol:
					actual_amount = p.positionAmt
					liquidationPrice = p.liquidationPrice

			logger.info("current OPEN position amount: %s" % actual_amount)
			if actual_amount != 0:
				createPositionStop(actual_amount,liquidationPrice,main_symbol)
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
	print("Event loop running forever, press Ctrl+C to interrupt.")

	try:
		loop.run_forever()
	finally:
		loop.close()

if __name__ == '__main__':
	auto_stop_market()



