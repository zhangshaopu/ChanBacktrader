import backtrader as bt
import pandas as pd
import datetime

from trade.strategies.chan_strategy import Chan_Strategy
from trade.constant import Interval
from trade.object import BarData,Exchange

def dataframe_to_csv_feed(df, file='XAUUSD-1M-2021.1.1-2023.6.30.csv'):
    '''
    take AKshare of dataframe Data conversion to csv of datafeed
    :param df: AKshare of dataframe data
    :param file: csv Cache file
    :return:
    '''
    fromdate = datetime.datetime(2021,1,4,1,0,0)  # Start date of data
    todate = datetime.datetime(2021,1,5,1,0,0)  # Start date of data
    
    feed = bt.feeds.GenericCSVData(
        dataname=file,
        dtformat=('%Y-%m-%d %H:%M:%S'),  # Date format
        fromdate=fromdate,  # Start date
        todate=todate,  # End date
        timeframe=bt.TimeFrame.Minutes, 
        compression=1,
        sessionstart=datetime.time(9, 0), # 交易日开始时间
        sessionend=datetime.time(17, 30), # 交易日结束时间
    )
    return feed

# csv文件格式化 只需要执行一次
def formatcsv(file):
    df = pd.read_csv(file)
    df['datetime'] = pd.to_datetime(df['<DTYYYYMMDD>'].astype(str) + ' ' + df['<TIME>'].astype(str).str.zfill(6), format='%Y%m%d %H%M%S')
    df.index = pd.to_datetime(df.datetime)
    df['openinterest'] = 0
    df = df.rename(columns={'<OPEN>': 'open',
                        '<HIGH>': 'high',
                        '<LOW>': 'low',
                        '<CLOSE>':'close',
                        '<VOL>':'volume'}
                )
    df = df[['open','high','low','close','volume','openinterest']]
    df.to_csv(file)
    return df

""""
# 创建策略继承bt.Strategy 
class TestStrategy(bt.Strategy): 

    params=(
        ('maperiod',20)
    ),
    
    def log(self, txt, dt=None): 
        # 记录策略的执行日志  
        dt = dt or self.datas[0].datetime.datetime(0) 
        print('%s, %s' % (dt.isoformat(), txt)) 

    def __init__(self):
        # 保存收盘价的引用  
        self.dataclose = self.datas[0].close 
        self.order = None
        self.ma = bt.indicators.SimpleMovingAverage(self.datas[0] , period = self.params.maperiod)
    #每个bar都会执行一次，回测的每个日期都会执行一次
    def next(self):
        # 记录收盘价  
        self.log('Close, %.2f' % self.dataclose[0]) 
        #判断是否有交易指令正在进行
        if(self.order):
            return
        #空仓
        if(not self.position):
            if self.datas[0].close[0] > self.ma[0]:
                self.order = self.buy(size=200)
        else:
            if self.datas[0].close[0] < self.ma[0]:
                self.order = self.sell(size=200)

"""



class ChanStrategy(bt.Strategy): 
    def __init__(self):
        self.order = None
        setting = {'include': True, 'interval': Interval.MINUTE, 'include_feature': True, 'qjt': True, 'gz': True, 'build_pivot': False, 'time_interval': 10}
        self.chan = Chan_Strategy(engine = 'CHANTU"',strategy_name = 'chantu' , vt_symbol = '600809',setting = setting , BacktraderBuy = self.buy , BacktraderSell = self.sell)
        pass
    def log(self, txt, dt=None):
        """
        输出日期
        :param txt:
        :param dt:
        :return:
        """
        # dt = dt or self.datas[0].datetime.datetime(0) 
        # print('%s , %s' % (dt.isoformat(), txt))

        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # bar = BarData(datetime=row[0], high_price=row[2], low_price=row[3], close_price=row[4])
        bar = BarData(
            symbol="XAUUSD",
            exchange=Exchange.SSE,
            interval=Interval.MINUTE,
            datetime=self.datas[0].datetime.datetime(0),
            open_price=self.datas[0].open[0],
            high_price=self.datas[0].high[0],
            low_price=self.datas[0].low[0],
            close_price=self.datas[0].close[0],
            # volume=row["volume"],
            # open_interest=row.get("open_interest", 0)
        )
        self.order = self.chan.on_bar(bar) # bar 是1min级别数据
        # if self.order is not None :
        #     print(self.order)
        pass 

    def notify_order(self, order):
 
        if order.status == order.Submitted:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER SUBMITTED', dt=order.created.dt)
            self.order = order
            return
 
        if order.status == order.Accepted:
            self.log('ORDER ACCEPTED', dt=order.created.dt)
            self.order = order
            return
 
        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')
 
        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.log(f'BUY DATA INFO HIGH:{self.data.high[0]};'
                         f'CLOSE:{self.data.close[0]}'
                         f'')
 
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
 
        # Sentinel to None: new orders allowed
        self.order = None
     
    

def runstart():
    cerebro = bt.Cerebro()
    # stock_df = get_data()
    
    # fromdate = datetime.datetime(2021,1,4,1,0,0)
    # todate = datetime.datetime(2021,1,5,1,0,0)
    # data = bt.feeds.PandasData(
    #     dataname = stock_df , 
    #     fromdate = fromdate , 
    #     todate = todate , 
    #     timeframe = bt.TimeFrame.Minutes
    # )
    data = dataframe_to_csv_feed(df = pd.read_csv('XAUUSD-1M-2021.1.1-2023.6.30.csv'))

    # cerebro.adddata(data)
    # 创建 1 分钟的时间框架并进行重采样
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=1)
    # 创建 5 分钟的时间框架并进行重采样
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5)
    # 创建 30 分钟的时间框架并进行重采样
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=30)
    # 创建 60 分钟的时间框架并进行重采样
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)
    
    cerebro.addstrategy(ChanStrategy)
    cerebro.broker.setcash(100000.0) 
    #设置手续费
    cerebro.broker.setcommission(0.0002)
    # 引擎运行前打印期出资金  
    print('组合期初资金: %.2f' % cerebro.broker.getvalue()) 
    cerebro.run() 
    cerebro.plot(style='bar')
    # 引擎运行后打期末资金  
    print('组合期末资金: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    runstart()



