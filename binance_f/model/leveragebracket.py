#createdbyme


class Brackets:

	def __init__(self):
		self.bracket = 0  #Notianl bracket
		self.initialLeverage = 0
		self.notionalCap = 0
		self.notionalFloor = 0
		self.maintMarginRatio = 0



class LeverageBracket:


	def __init__(self):
		self.symbol = ""
		self.brackets = list()
	
	@staticmethod
	def json_parse(json_data):
		result = LeverageBracket()
		result.symbol = json_data.get_string("symbol")
		data_list = json_data.get_array("brackets")
		element_list = list()
		for item in data_list.get_items():
			element = Brackets()
			element.bracket = item.get_int("bracket")
			element.initialLeverage = item.get_int("initialLeverage")
			element.notionalCap = item.get_int("notionalCap")
			element.notionalFloor = item.get_int("notionalFloor")
			element.maintMarginRatio = item.get_float("maintMarginRatio")
			element_list.append(element)
		result.brackets = element_list



		return result




# [
# 	{
# 		"symbol": "ETHUSDT",
# 		"brackets": [
# 			{
# 				"bracket": 1,   // Notianl bracket
# 				"initialLeverage": 75,  // Max initial leverge for this bracket
# 				"notionalCap": 10000,  // Cap notional of this bracket
# 				"notionalFloor": 0,  // Notionl threshold of this bracket 
# 				"maintMarginRatio": 0.0065 // Maintenance ratio for this bracket
# 			},
# 		]
# 	}
# [