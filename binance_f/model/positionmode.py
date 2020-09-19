#createdbyme
class PositionMode:
	def __init__(self):
		self.code = ""
		self.msg = ""
	
	@staticmethod
	def json_parse(json_data):
		print("parsing position data")
		result = PositionMode()
		result.code = json_data.get_string("code")
		result.msg = json_data.get_string("msg")

		return result