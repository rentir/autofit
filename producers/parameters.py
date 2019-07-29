from . import Producer, JoinedSlot

Producer("synthetic_fwd_fitter", [JoinedSlot('implied_fwd')], ['dividends', 'product_rate'], 1)
Producer("vol_fitter", [JoinedSlot('implied_fwd'), JoinedSlot('implied_vol')], ['volatility'], 1)
Producer("trs_fitter", [JoinedSlot('trs_totem'), JoinedSlot('implied_fwd')], ['dividends', 'product_rate'], 2)
Producer("varswap_fitter", [JoinedSlot('volatility'), JoinedSlot('dividends'),
                            JoinedSlot('product_rate'), JoinedSlot('varswap_totem')], ['varswapvolbasis'], 1,
         delay=0)
Producer("proxy_vol_fitter", [JoinedSlot('tau_risk'), JoinedSlot('implied_vol', exclusive=True)], ['volatility'],
         priority=0, delay=10)
Producer("proxy_varswap", [JoinedSlot('varswapvolbasis_risk'), JoinedSlot('varswapvolbasis', exclusive=True)],
         ['varswapvolbasis'], priority=0, delay=10)
