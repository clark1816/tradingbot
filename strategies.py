import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds



cerebro = bt.Cerebro()


class MyStrategy(bt.Strategy):

    def __init__(self):
        self.dataclose = self.datas[0]
        


    def next(self):
        if self.dataclose[0] > self.dataclose[-1]:

            if self.dataclose[-1] > self.dataclose[-2]:
                print(self.dataclose[0])
                self.buy
                pass



        # elif self.sma < self.feed.close:
        #     # Do something else
        #     pass