class CandlestickInterval:
    MIN1 = "1m"
    MIN3 = "3m"
    MIN5 = "5m"
    MIN15 = "15m"
    MIN30 = "30m"
    HOUR1 = "1h"
    HOUR2 = "2h"
    HOUR4 = "4h"
    HOUR6 = "6h"
    HOUR8 = "8h"
    HOUR12 = "12h"
    DAY1 = "1d"
    DAY3 = "3d"
    WEEK1 = "1w"
    MON1 = "1M"
    INVALID = None


class OrderSide:
    BUY = "BUY"
    SELL = "SELL"
    INVALID = None


class TimeInForce:
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    INVALID = None


class TradeDirection:
    BUY = "buy"
    SELL = "sell"
    INVALID = None


class OrderType:
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_MARKET = "STOP_MARKET"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_RPOFIT_MARKET = "TAKE_RPOFIT_MARKET"
    INVALID = None

class OrderRespType:
    ACK = "ACK"
    RESULT = "RESULT"
    FULL = "FULL"
    INVALID = None


class AccountType:
    SPOT = "spot"
    MARGIN = "margin"
    OTC = "otc"
    POINT = "point"
    MINEPOLL = "minepool"
    ETF = "etf"
    AGENCY = "agency"
    SUPER_MARGIN = "super-margin"
    INVALID = None


class AccountState:
    WORKING = "working"
    LOCK = "lock"
    INVALID = None


class BalanceType:
    TRADE = "trade"
    FROZEN = "frozen"
    LOAN = "loan"
    INTEREST = "interest"
    LOAN_AVAILABLE = "loan-available"
    TRANSFER_OUT_AVAILABLE = "transfer-out-available"
    INVALID = None


class WithdrawState:
    SUBMITTED = "submitted"
    REEXAMINE = "reexamine"
    CANCELED = "canceled"
    PASS = "pass"
    REJECT = "reject"
    PRETRANSFER = "pre-transfer"
    WALLETTRANSFER = "wallet-transfer"
    WALEETREJECT = "wallet-reject"
    CONFIRMED = "confirmed"
    CONFIRMERROR = "confirm-error"
    REPEALED = "repealed"
    INVALID = None

class DepositWithdraw:
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class DepositState:
    CONFIRMING = "confirming"
    SAFE = "safe"
    CONFIRMED = "confirmed"
    ORPHAN = "orphan"
    INVALID = None


class LoanOrderState:
    CREATED = "created"
    ACCRUAL = "accrual"
    CLEARED = "cleared"
    FAILED = "failed"
    INVALID = None


class OrderSource:
    SYS = "sys"
    WEB = "web"
    API = "api"
    APP = "app"
    FL_SYS = "fl-sys"
    FL_MGT = "fl-mgt"
    SPOT_WEB = "spot-web"
    SPOT_API = "spot-api"
    SPOT_APP = "spot-app"
    MARGIN_API = "margin-api"
    MARGIN_WEB = "margin-web"
    MARGIN_APP = "margin-app"
    SUPER_MARGIN_API = "super-margin-api"
    SUPER_MARGIN_WEB = "super-margin-web"
    SUPER_MARGIN_APP = "super-margin-app"
    SUPER_MARGIN_FL_SYS = "super-margin-fl-sys"
    SUPER_MARGIN_FL_MGT = "super-margin-fl-mgt"
    INVALID = None


class OrderState:
    CREATED = "created"   #for stop loss order
    PRE_SUBMITTED = "pre-submitted"
    SUBMITTING = "submitting"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial-filled"
    CANCELLING = "cancelling"
    PARTIAL_CANCELED = "partial-canceled"
    FILLED = "filled"
    CANCELED = "canceled"
    FAILED = "failed"
    PLACE_TIMEOUT = "place_timeout"
    INVALID = None


class TransferMasterType:
    IN = "master-transfer-in"
    OUT = "master-transfer-out"
    POINT_IN = "master-point-transfer-in"
    POINT_OUT = "master-point-transfer-out"
    INVALID = None


class EtfStatus:
    NORMAL = "1"
    REBALANCING_START = "2"
    CREATION_AND_REDEMPTION_SUSPEND = "3"
    CREATION_SUSPEND = "4"
    REDEMPTION_SUSPEND = "5"
    INVALID = None


class EtfSwapType:
    IN = "1"
    OUT = "2"
    INVALID = None


class AccountChangeType:
    NEWORDER = "order.place"
    TRADE = "order.match"
    REFUND = "order.refund"
    CANCELORDER = "order.cancel"
    FEE = "order.fee-refund"
    TRANSFER = "margin.transfer"
    LOAN = "margin.loan"
    INTEREST = "margin.interest"
    REPAY = "margin.repay"
    OTHER = "other"
    INVALID = None


class BalanceMode:
    AVAILABLE = "0"
    TOTAL = "1"
    INVALID = None

class OperateMode:
    PING = "ping"
    PONG = "pong"
    INVALID = None

class QueryDirection:
    PREV = "prev"
    NEXT = "next"
    INVALID = None

class TransferFuturesPro:
    TO_PRO = "futures-to-pro"
    TO_FETURES ="pro-to-futures"

class MatchRole:
    MAKER = "maker"
    TAKER = "taker"

class DepthStep:
    STEP0 = "step0"
    STEP1 = "step1"
    STEP2 = "step2"
    STEP3 = "step3"
    STEP4 = "step4"
    STEP5 = "step5"


class ChainDepositStatus:
    ALLOWED = "allowed"
    PROHIBITED = "prohibited"
    INVALID = None

class ChainWithdrawStatus:
    ALLOWED = "allowed"
    PROHIBITED = "prohibited"
    INVALID = None

class InstrumentStatus:
    NORMAL = "normal"
    DELISTED = "delisted"
    INVALID = None

class SubscribeMessageType:
    RESPONSE = "response"
    PAYLOAD = "payload"


class MarginTransferType:
    IN = "1"
    OUT = "2"
    INVALID = None


class TransferType:
    ROLL_IN = "ROLL_IN"
    ROLL_OUT = "ROLL_OUT"
    INVALID = None


class SideEffectType:
    NO_SIDE_EFFECT = "NO_SIDE_EFFECT"
    MARGIN_BUY = "MARGIN_BUY"
    AUTO_REPAY = "AUTO_REPAY"
    INVALID = None


class WorkingType:
    MARK_PRICE = "MARK_PRICE"
    CONTRACT_PRICE = "CONTRACT_PRICE"
    INVALID = None


class FuturesMarginType:
    ISOLATED = "ISOLATED"
    CROSSED = "CROSSED"


class IncomeType:
    TRANSFER = "TRANSFER"
    WELCOME_BONUS = "WELCOME_BONUS"
    REALIZED_PNL = "REALIZED_PNL"
    FUNDING_FEE = "FUNDING_FEE"
    COMMISSION = "COMMISSION"
    INSURANCE_CLEAR = "INSURANCE_CLEAR"
    INVALID = None

class UpdateTime:
    NORMAL = ""
    FAST = "@100ms"
    REALTIME = "@0ms"
    INVALID = ""
