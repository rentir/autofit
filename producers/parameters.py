from . import Producer, JoinedSlot

Producer("synthetic_fwd_fitter", [JoinedSlot('implied_fwd')], ['dividends', 'product_rate'], 1)
Producer("vol_fitter", [JoinedSlot('implied_fwd'), JoinedSlot('implied_vol')], ['volatility'], 1)
Producer("trs_fitter", [JoinedSlot('trs_totem')], ['dividends', 'product_rate'], 1)
Producer("trs_fwd_fitter", [JoinedSlot('implied_fwd'),
                            JoinedSlot('trs_totem')], ['dividends', 'product_rate'], 2)
Producer("varswap_fitter", [JoinedSlot('volatility'), JoinedSlot('dividends'),
                            JoinedSlot('product_rate'), JoinedSlot('varswap_totem')], ['varswapvolbasis'], 1,
         delay=10)
Producer("proxy_vol_fitter", [JoinedSlot('tau'), JoinedSlot('implied_vol', exclusive=True)], ['volatility'],
         priority=0, delay=10)
