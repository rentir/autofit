from . import Producer, JoinedSlot

Producer('black_scholes_calculator', [JoinedSlot('european_totem')], ['implied_fwd', 'implied_vol'], 0)
