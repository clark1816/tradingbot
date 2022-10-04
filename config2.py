import yfinance as yf
import numpy as np
import backtrader as bt
import strategies


cerebro = bt.Cerebro()

data =yf.download('AAPL', start='2021-01-01', interval="1d",rounding = True)

feed = bt.feeds.PandasData(dataname=data)

cerebro.adddata(feed)

# print(feed)


cerebro.addstrategy(strategies.MyStrategy)
print(cerebro.broker.getvalue())
cerebro.run()
print(cerebro.broker.getvalue())
def saveplots(cerebro, numfigs=1, iplot=True, start=None, end=None,
            width=16, height=9, dpi=300, tight=True, use=None, file_path = '', **kwargs):

    from backtrader import plot
    if cerebro.p.oldsync:
        plotter = plot.Plot_OldSync(**kwargs)
    else:
        plotter = plot.Plot(**kwargs)

    figs = []
    for stratlist in cerebro.runstrats:
        for si, strat in enumerate(stratlist):
            rfig = plotter.plot(strat, figid=si * 100,
                                numfigs=numfigs, iplot=iplot,
                                start=start, end=end, use=use)
            figs.append(rfig)

    for fig in figs:
        for f in fig:
            f.savefig(file_path, bbox_inches='tight')
    return figs

saveplots(cerebro, file_path = 'static/savefig.jpg')