# Star Trader by Dave Kaufman, 1974
# Python version by Peter Sovietov, 2017

from __future__ import division
import sys
import math
from random import random as rnd

nl = "\n"
tab = lambda n: " " * n

def out(*args):
  for a in args:
    sys.stdout.write(str(a))
  sys.stdout.flush()

def typo():
  out("WATCH YOUR TYPING -- TRY AGAIN", nl)

def get_text():
  s = sys.stdin.readline().upper().strip()
  while s == "":
    typo()
    s = sys.stdin.readline().upper().strip()
  return s

def get_oneof(words):
  s = get_text()
  while s not in words:
    typo()
    s = get_text()
  return s

def get_int():
  try:
    return int(get_text())
  except ValueError:
    return None

def get_gteq(m):
  n = get_int()
  while n == None or n < m:
    typo()
    n = get_int()
  return n

def get_range(lo, hi):
  n = get_int()
  while n == None or n < lo or n > hi:
    typo()
    n = get_int()
  return n

def sgn(x):
  if x < 0:
    return -1
  return 1 if x > 0 else 0

rint = lambda x: int(round(x))

INTRO = """
     THE DATE IS JAN 1, 2070 AND INTERSTELLAR FLIGHT
HAS EXISTED FOR 70 YEARS.  THERE ARE SEVERAL STAR
SYSTEMS THAT HAVE BEEN COLONIZED.  SOME ARE ONLY
FRONTIER SYSTEMS, OTHERS ARE OLDER AND MORE DEVELOPED.

     EACH OF YOU IS THE CAPTAIN OF TWO INTERSTELLAR
TRADING SHIPS.  YOU WILL TRAVEL FROM STAR SYSTEM TO
STAR SYSTEM, BUYING AND SELLING MERCHANDISE.  IF YOU
DRIVE A GOOD BARGAIN YOU CAN MAKE LARGE PROFITS.

     AS TIME GOES ON, EACH STAR SYSTEM WILL SLOWLY
GROW, AND ITS NEEDS WILL CHANGE.  A STAR SYSTEM THAT
HOW IS SELLING MUCH URANIUM AND RAW METALS CHEAPLY
MAY NOT HAVE ENOUGH FOR EXPORT IN A FEW YEARS.

     YOUR SHIPS CAN TRAVEL ABOUT TWO LIGHTYEARS IN A
WEEK AND CAN CARRY UP TO %s TONS OF CARGO.  ONLY
CLASS I AND CLASS II STAR SYSTEMS HAVE BANKS ON THEM.
THEY PAY 5%% INTEREST AND ANY MONEY YOU DEPOSIT ON ONE
PLANET IS AVAILABLE ON ANOTHER - PROVIDED THERE'S A LOCAL
BANK.
"""

REPORT = """
STAR SYSTEM CLASSES:
     I  COSMOPOLITAN
    II  DEVELOPED
   III  UNDERDEVELOPED
    IV  FRONTIER


MERCHANDISE:
    UR  URANIUM
   MET  METALS
    HE  HEAVY EQUIPMENT
   MED  MEDICINE
  SOFT  COMPUTER SOFTWARE
  GEMS  STAR GEMS


     EACH TRADING SHIP CAN CARRY MAX %s TONS CARGO.
STAR GEMS AND COMPUTER SOFTWARE, WHICH AREN'T SOLD BY THE
TON, DON'T COUNT.
"""

ADVICE = """
ALL SHIPS START AT SOL
ADVICE;  VISIT THE CLASS III AND IV SYSTEMS -
SOL AND THE CLASS II STARS PRODUCE ALOT OF HE,MED AND
SOFT, WHICH THE POORER STAR SYSTEMS (CLASS III AND
IV) NEED.  ALSO, THE POOR STARS PRODUCE THE RAW GOODS -
UR,MET,GEMS THAT YOU CAN BRING BACK TO SOL AND
THE CLASS II SYSTEMS IN TRADE

STUDY THE MAP AND CURRENT PRICE CHARTS CAREFULLY -
CLASS I AND II STARS MAKE EXCELLENT TRADING PARTNERS
WITH CLASS III OR IV STARS.
"""

COSMOPOLITAN = 15
DEVELOPED = 10
UNDERDEVELOPED = 5
FRONTIER = 0

STAR_NAMES = [
  "SOL", "YORK", "BOYD", "IVAN", "REEF", "HOOK", "STAN", "TASK", "SINK",
  "SAND", "QUIN", "GAOL", "KIRK", "KRIS", "FATE"
]

MONTHS = [
  "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT",
  "NOV", "DEC"
]

GOODS_NAMES = ["UR", "MET", "HE", "MED", "SOFT", "GEMS"]
GOODS_TITLE = "%5s %5s %5s %5s %5s %5s" % tuple(GOODS_NAMES)

PRICES = [5000, 3500, 4000, 4500, 3000, 3000]

# *** DATA FOR ECONOMETRIC MODEL FOLLOWS ***
# [slope, y-intercept]

LINE_SLOPE = 0
LINE_Y = 1

ECONOMIC = [
  [[-0.1, 1], [-0.2, 1.5], [-0.1, 0.5]],
  [[0, 0.75], [-0.1, 0.75], [-0.1, 0.75]],
  [[0, -0.75], [0.1, -0.75], [0.1, -0.75]],
  [[-0.1, -0.5], [0.1, -1.5], [0, 0.5]],
  [[0.1, -1], [0.2, -1.5], [0.1, -0.5]],
  [[0.1, 0.5], [-0.1, 1.5], [0, -0.5]]
]

class Record:
  def __init__(self, **kwargs):
    for kw in kwargs:
      setattr(self, kw, kwargs[kw])

def make_game():
  return Record(
    speed = 2 / 7,
    max_distance = 15,
    delay = 0.1,
    number_of_rounds = 3,
    max_weight = 30,
    margin = 36,
    level_inc = 1.25,
    day = 1,
    year = 2070,
    end_year = 5,
    number_of_players = 2,
    half = 1,
    ship = None,
    ships = [],
    stars = [],
    accounts = []
  )

def make_ship(g):
  return Record(
    goods = [0, 0, 15, 10, 10, 0],
    weight = 25,
    day = g.day,
    year = g.year,
    sum = 5000,
    star = None,
    status = 0,
    player = 0,
    name = ""
  )

def make_star(g):
  return Record(
    goods = [0, 0, 0, 0, 0, 0],
    prices = [0, 0, 0, 0, 0, 0],
    prod = [0, 0, 0, 0, 0, 0],
    x = 0,
    y = 0,
    level = COSMOPOLITAN,
    day = 270,
    year = g.year - 1,
    name = STAR_NAMES[0]
  )

def make_account(g):
  return Record(
    sum = 0,
    day = g.day,
    year = g.year
  )

def make_objects(g, obj, n):
  return [obj(g) for i in range(n)]

def own_game(g):
  out("HOW MANY PLAYERS (2,3,4, ... ,12 CAN PLAY) ")
  g.number_of_players = get_range(2, 12)
  while True:
    out(nl, "HOW MANY SHIPS PER PLAYER ")
    n = get_gteq(1)
    out(nl)
    number_of_ships = g.number_of_players * n
    if number_of_ships <= 12:
      break
    out("I CAN'T KEEP TRACK OF MORE THAN 12 SHIPS;", nl)
    out(g.number_of_players, " PLAYERS TIMES ", n, " SHIPS MAKES ",
      number_of_ships)
  g.ships = make_objects(g, make_ship, number_of_ships)
  out("HOW MANY STAR SYSTEMS (FROM 4 TO 13 STARS) ")
  g.stars = make_objects(g, make_star, get_range(4, 13))
  out(nl, "ENTER THE LENGTH OF GAME IN YEARS ")
  length = get_gteq(1)
  g.end_year = g.year + length
  out(nl, "WHAT'S THE MAX CARGOE TONNAGE(USUALLY 30) ")
  g.max_weight = get_gteq(25)
  out(nl, "WHAT'S THE MINIMUM DISTANCE BETWEEN STARS(MIN SPACING 10, MAX 25, USUALLY 15) ")
  g.max_distance = get_range(10, 25)
  out(nl, "HOW MANY BIDS OR OFFERS(USUALLY 3) ")
  g.number_of_rounds = get_gteq(1)
  out(nl, "SET THE PROFIT MARGIN(1,2,3,4 OR 5)...THE HIGHER", nl)
  out("THE NUMBER, THE LOWER THE PROFIT % ... USUALLY SET TO 2", nl)
  out("...YOUR NUMBER ")
  g.margin = 18 * min(abs(get_int()), 5)

def distance(x1, y1, x2, y2):
  return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# *** <TEST STAR CO-ORDS>
# FIRST CONVERT CO-ORDS TO NEXT HALF-BOARD
# SECOND, TEST PROXIMITY
# FINALLY, ENTER CO-ORDS AND INCREMENT HALF-BOARD CTR

def good_coords(g, index, x, y):
  if g.half == 2:
    x, y, = y, x
  elif g.half == 3:
    y = -y
  elif g.half == 4:
    x, y = -y, x
  g.half += 1
  if g.half > 4:
    g.half = 1
  for i in range(index):
    if distance(x, y, g.stars[i].x, g.stars[i].y) < g.max_distance:
      return False
  g.stars[index].x = rint(x)
  g.stars[index].y = rint(y)
  return True

def generate_coords(g, index, bounds):
  while True:
    x = (rnd() - 0.5) * bounds
    y = rnd() * bounds / 2
    if good_coords(g, index, x, y):
      return

def add_star(g, index, level):
  if level == FRONTIER:
    while True:
      x = (rnd() - 0.5) * 100
      y = 50 * rnd()
      if abs(x) >= 25 or y >= 25:
        if good_coords(g, index, x, y):
          break
  elif level == UNDERDEVELOPED:
    generate_coords(g, index, 100)
  elif level == DEVELOPED:
    generate_coords(g, index, 50)
  g.stars[index].level = level

def name_star(g, index):
  while True:
    name = STAR_NAMES[1 + rint(13 * rnd())]
    found = False
    for i in range(1, len(g.stars)):
      if name == g.stars[i].name:
        found = True
        break
    if not found:
      break
  g.stars[index].name = name

def make_stars(g):
  g.half = 1
  add_star(g, 1, FRONTIER)
  add_star(g, 2, FRONTIER)
  add_star(g, 3, UNDERDEVELOPED)
  for i in range(4, len(g.stars)):
    level = i % 3 * 5
    add_star(g, i, level)
  for i in range(1, len(g.stars)):
    name_star(g, i)

def name_ships(g):
  ship_index = 0
  out(nl * 2, "CAPTAINS, NAME YOUR SHIPS", nl)
  for i in range(len(g.ships) // g.number_of_players):
    out(nl)
    for p in range(g.number_of_players):
      out("   CAPTAIN ", p + 1, " WHAT DO YOU CHRISTEN YOUR SHIP # ",
        i + 1, nl)
      g.ships[ship_index].name = get_text()
      g.ships[ship_index].player = p
      ship_index += 1

def finish_setup(g):
  make_stars(g)
  name_ships(g)
  g.accounts = make_objects(g, make_account, g.number_of_players)

def setup(g):
  out("INSTRUCTIONS (TYPE 'Y' OR 'N' PLEASE) ")
  if get_oneof(["Y", "N"]) == "Y":
    out(INTRO % g.max_weight, nl)
  else:
    out(nl)
  out("HAVE ALL PLAYERS PLAYED BEFORE ")
  ans = get_oneof(["Y", "N"])
  out(nl)
  if ans == "Y":
    out("DO YOU WANT TO SET UP YOUR OWN GAME ")
    ans = get_oneof(["Y", "N"])
    out(nl)
    if ans == "Y":
      own_game(g)
      finish_setup(g)
      return
  out("HOW MANY PLAYERS (2,3, OR 4 CAN PLAY) ")
  g.number_of_players = get_range(2, 4)
  out(nl)
  g.ships = make_objects(g, make_ship, 2 * g.number_of_players)
  g.stars = make_objects(g, make_star, 3 * g.number_of_players + 1)
  g.end_year = g.year + 5
  finish_setup(g)

def star_map(g):
  out(nl * 3, tab(22), "STAR MAP", nl, tab(20), "*" * 12, nl)
  for y in range(15, -16, -1):
    line = list("                         1                             ")
    if y == 0:
      line = list("1----1----1----1----1----*SOL-1----1----1----1----1    ")
    elif y % 3 == 0:
      line[25] = "-"
    y_hi = y * 10 / 3
    y_lo = (y + 1) * 10 / 3
    for s in range(1, len(g.stars)):
      if g.stars[s].y < y_lo and g.stars[s].y >= y_hi:
        x = rint(25 + g.stars[s].x / 2)
        name = g.stars[s].name
        line[x:x + len(name) + 1] = "*" + name
    out("".join(line), nl)
  out(nl, "THE MAP IS 100 LIGHT-YEARS BY 100 LIGHT-YEARS,", nl)
  out("SO THE CROSS-LINES MARK 10 LIGHT-YEAR DISTANCES", nl)

def ga():
  out(nl * 2, "*** GENERAL ANNOUNCEMENT ***", nl * 3)

# M AND C DETERMINE A STAR'S PRODUCTIVITY/MONTH
#   PROD/MO. = S(7,J) * M(I,R1)  +  C(I,R1)
#   WHERE J IS THE STAR ID #,I THE MERCHANDISE #,
#   AND R1 IS THE DEVELOPMENT CLASS OF THE STAR

def update_prices(g, star):
  seg = 0
  if star.level >= UNDERDEVELOPED:
    seg += 1
  if star.level >= DEVELOPED:
    seg += 1
  months = 12 * (g.year - star.year) + (g.day - star.day) / 30
  prod = star.prod
  for i in range(6):
    prod[i] = (1 + star.level / 15) * (
      ECONOMIC[i][seg][LINE_SLOPE] * star.level + ECONOMIC[i][seg][LINE_Y])
    if abs(prod[i]) <= 0.01:
      g.prices[i] = 0
    else:
      star.goods[i] = sgn(prod[i]) * min(abs(
        prod[i] * 12), abs(star.goods[i] + months * prod[i]))
      star.prices[i] = PRICES[i] * (1 - sgn(star.goods[i]) * abs(
        star.goods[i] / (prod[i] * g.margin)))
      star.prices[i] = 100 * rint(star.prices[i] / 100 + 0.5)
  star.day = g.day
  star.year = g.year

def star_level(g, star):
  level = int(star.level / 5)
  if level == 0:
    return "IV"
  elif level == 1:
    return "III"
  elif level == 2:
    return "II"
  else:
    return "I"

def update_account(g, account):
  account.sum = account.sum * (1 + 0.05 * (
    g.year - account.year + (g.day - account.day) / 360))
  account.day = g.day
  account.year = g.year

def price_col(n):
  return "+" + str(n) if n > 0 else str(n)

def report(g):
  ga()
  out("JAN  1, ", g.year, tab(35), " YEARLY REPORT # ",
    g.year - 2069, nl * 2)
  if g.year <= 2070:
    out(REPORT % g.max_weight, nl, nl)
  out(tab(20), "CURRENT PRICES", nl, nl, nl)
  out("NAME  CLASS ", GOODS_TITLE, nl, nl)
  for i in range(len(g.stars)):
    update_prices(g, g.stars[i])
    prices = g.stars[i].prices
    for j in range(6):
      prices[j] = sgn(g.stars[i].goods[j]) * prices[j]
    out("%4s %5s  %5s %5s %5s %5s %5s %5s" % (
      g.stars[i].name,
      star_level(g, g.stars[i]),
      price_col(prices[0]),
      price_col(prices[1]),
      price_col(prices[2]),
      price_col(prices[3]),
      price_col(prices[4]),
      price_col(prices[5])
    ), nl)
    if i % 2 != 0:
      out(nl)
  out(nl, "('+' MEANS SELLING AND '-' MEANS BUYING)", nl * 3)
  out(tab(22), "CAPTAINS", nl * 3)
  out("NUMBER  $ ON SHIPS   $ IN BANK     CARGOES      TOTALS", nl)
  for p in range(g.number_of_players):
    update_account(g, g.accounts[p])
  for p in range(g.number_of_players):
    out(nl)
    on_ships = 0
    cargoes = 0
    for i in range(len(g.ships) // g.number_of_players):
      ship = g.ships[g.number_of_players * i + p]
      on_ships += ship.sum
      for j in range(6):
        cargoes += ship.goods[j] * PRICES[j]
    in_bank = rint(g.accounts[p].sum)
    totals = on_ships + cargoes + in_bank
    out("  %2d    %10d  %10d  %10d  %10d" % (
      p + 1, on_ships, in_bank, cargoes, totals
    ), nl)

def get_names(objects):
  return [o.name for o in objects]

def ship_days(g, d):
  g.ship.day += d
  if g.ship.day > 360:
    g.ship.day -= 360
    g.ship.year += 1

def travel(g, from_star):
  d = distance(
    from_star.x, from_star.y, g.ship.star.x, g.ship.star.y) / g.speed
  d = rint(d)
  if rnd() <= g.delay / 2:
    w = 1 + rint(rnd() * 3)
    if w == 1:
      out("LOCAL HOLIDAY SOON", nl)
    elif w == 2:
      out("CREWMEN DEMAND A VACATION", nl)
    elif w == 3:
      out("SHIP DOES NOT PASS INSPECTION", nl)
    out(" - ", w, " WEEK DELAY.", nl)
    d += 7 * w
  ship_days(g, d)
  m = int((g.ship.day - 1) / 30)
  out(
    "THE ETA AT ", g.ship.star.name, " IS ", MONTHS[m], " ",
    g.ship.day - 30 * m, ", ", g.ship.year, nl
  )
  d = rint(rnd() * 3) + 1
  if rnd() <= g.delay / 2:
    d = 0
  ship_days(g, 7 * d)
  g.ship.status = d

def next_eta(g):
  names = get_names(g.stars)
  names.remove(g.ship.star.name)
  while True:
    ans = get_oneof(names + ["MAP", "REPORT"])
    if ans == "MAP":
      star_map(g)
    elif ans == "REPORT":
      report(g)
    else:
      from_star = g.ship.star
      g.ship.star = g.stars[get_names(g.stars).index(ans)]
      travel(g, from_star)
      break
    out(nl)

def landing(g):
  d = g.ships[0].day
  y = g.ships[0].year
  ship_index = 0
  for i in range(1, len(g.ships)):
    if g.ships[i].year > y or g.ships[i].day > d:
      pass
    elif g.ships[i].day == d and rnd() > 0.5:
      pass
    else:
      d = g.ships[i].day
      y = g.ships[i].year
      ship_index = i
  g.ship = g.ships[ship_index]
  if g.year != y:
    g.day = 1
    g.year = y
    report(g)
    if g.year >= g.end_year:
      return False
  g.day = d
  m = int((g.day - 1) / 30)
  out(nl * 2, "*" * 17, nl, "* ", MONTHS[m], " %-5s, " % (g.day - 30 * m),
    g.year, nl)
  out("* ", g.ship.name, " HAS LANDED ON ", g.ship.star.name, nl)
  s = g.ship.status + 1
  if s == 2:
    out("1 WEEK LATE - 'OUR COMPUTER MADE A MISTAKE'", nl)
  elif s == 3:
    out("2 WEEKS LATE - 'WE GOT LOST.SORRY'", nl)
  elif s == 4:
    out("3 WEEKS LATE - PIRATES ATTACKED MIDVOYAGE", nl)
  out(nl, "$ ON BOARD ", GOODS_TITLE, "   NET WT", nl)
  out("%10d    %2d    %2d    %2d    %2d    %2d    %2d     %2d" % (
    g.ship.sum,
    g.ship.goods[0],
    g.ship.goods[1],
    g.ship.goods[2],
    g.ship.goods[3],
    g.ship.goods[4],
    g.ship.goods[5],
    g.ship.weight
  ), nl)
  update_prices(g, g.ship.star)
  return True

def price_window(g, index, units, current_round):
  w = 0.5
  star_units = g.ship.star.goods[index]
  if units < abs(star_units):
    w = units / (2 * abs(star_units))
  return w / (current_round + 1)

def buy_bids(g, index, units):
  star = g.ship.star
  star_units = rint(star.goods[index])
  if units > 2 * -star_units:
    units = 2 * -star_units
    out(tab(5), "WE'LL BID ON ", units, " UNITS.", nl)
  for r in range(g.number_of_rounds):
    if r != max(g.number_of_rounds - 1, 2):
      out(tab(5), "WE OFFER ")
    else:
      out(tab(5), "OUR FINAL OFFER:")
    out(100 * rint(0.009 * star.prices[index] * units + 0.5))
    out(" WHAT DO YOU BID ")
    price = get_range(
      star.prices[index] * units / 10,
      star.prices[index] * units * 10
    )
    if price <= star.prices[index] * units:
      out(tab(5), "WE'LL BUY!", nl)
      g.ship.goods[index] -= units
      if index < 4:
        g.ship.weight -= units
      g.ship.sum += price
      star.goods[index] += units
      return
    elif price > (1 + price_window(g, index, units, r)
      ) * star.prices[index] * units:
      break
    else:
      star.prices[index] = 0.8 * star.prices[index] + 0.2 * price / units
  out(tab(5), "WE'LL PASS THIS ONE", nl)

def buy(g):
  out(nl, "WE ARE BUYING:", nl)
  for i in range(6):
    star_units = rint(g.ship.star.goods[i])
    if star_units < 0 and g.ship.goods[i] > 0:
      out(tab(5), GOODS_NAMES[i], " WE NEED ", -star_units, " UNITS.", nl)
      while True:
        out("HOW MANY ARE YOU SELLING ")
        units = get_gteq(0)
        if units == 0:
          break
        elif units <= g.ship.goods[i]:
          buy_bids(g, i, units)
          break
        else:
          out(tab(5), "YOU ONLY HAVE ", g.ship.goods[i])
          out(" UNITS IN YOUR HOLD", nl, tab(5))

def sold(g, index, units, price):
  out(tab(5), "SOLD!", nl)
  g.ship.goods[index] += units
  if index < 4:
    g.ship.weight += units
  g.ship.star.goods[index] -= units
  g.ship.sum -= price

def sell_bids(g, index, units):
  star = g.ship.star
  for r in range(g.number_of_rounds):
    if r != max(g.number_of_rounds - 1, 2):
      out(tab(5), "WE WANT ABOUT ")
    else:
      out(tab(5), "OUR FINAL OFFER:")
    out(100 * rint(0.011 * star.prices[index] * units + 0.5))
    out(" YOUR OFFER ")
    price = get_range(
      star.prices[index] * units / 10,
      star.prices[index] * units * 10
    )
    if price >= star.prices[index] * units:
      if price <= g.ship.sum:
        sold(g, index, units, price)
        return
      else:
        out(tab(5), "YOU BID $ ", price, " BUT YOU HAVE ONLY $ ", g.ship.sum)
        p = g.ship.player
        if star.level >= DEVELOPED and g.ship.sum + g.accounts[p].sum >= price:
          out(tab(5))
          bank_call(g)
          if price <= g.ship.sum:
            sold(g, index, units, price)
            return
        break
    elif price < (1 - price_window(g, index, units, r)
      ) * star.prices[index] * units:
      break
    star.prices[index] = 0.8 * star.prices[index] + 0.2 * price / units
  out(tab(5), "THAT'S TOO LOW", nl)

def sell(g):
  out(nl, "WE ARE SELLING:", nl)
  for i in range(6):
    star_units = rint(g.ship.star.goods[i])
    if g.ship.star.prod[i] <= 0 or g.ship.star.goods[i] < 1:
      pass
    elif i <= 3 and g.ship.weight >= g.max_weight:
      pass
    else:
      out(tab(5), GOODS_NAMES[i], " UP TO ", star_units, " UNITS.")
      while True:
        out("HOW MANY ARE YOU BUYING ")
        units = get_range(0, star_units)
        if units == 0:
          break
        elif i > 3 or units + g.ship.weight <= g.max_weight:
          sell_bids(g, i, units)
          break
        else:
          out(tab(5), "YOU HAVE ", g.ship.weight, " TONS ABOARD, SO ", units)
          out(" TONS PUTS YOU OVER", nl)
          out(tab(5), "THE ", g.max_weight, " TON LIMIT.", nl)
          out(tab(5))
  out(nl)

def bank_call(g):
  out("DO YOU WISH TO VISIT THE LOCAL BANK ")
  if get_oneof(["Y", "N"]) != "Y":
    return
  p = g.ship.player
  account = g.accounts[p]
  update_account(g, account)
  out(tab(5), "YOU HAVE $ ", account.sum, " IN THE BANK", nl)
  out(tab(5), "AND $ ", g.ship.sum, " ON YOUR SHIP", nl)
  if account.sum != 0:
    out(tab(5), "HOW MUCH DO YOU WISH TO WITHDRAW ")
    x = get_range(0, account.sum)
    account.sum -= x
    g.ship.sum += x
  out(tab(5), "HOW MUCH DO YOU WISH TO DEPOSIT ")
  x = get_range(0, g.ship.sum)
  g.ship.sum -= x
  account.sum += x

def update_class(g, star):
  n = 0
  for i in range(6):
    if star.goods[i] >= 0:
      pass
    elif star.goods[i] < star.prod[i]:
      return False
    else:
      n += 1
  if n > 1:
    return False
  star.level += g.level_inc
  if star.level in (UNDERDEVELOPED, DEVELOPED, COSMOPOLITAN):
    ga()
    out("STAR SYSTEM ", star.name, " IS NOW A CLASS ", star_level(star),
      " SYSTEM", nl)
  return True

def new_star(g):
  if len(g.stars) == 15:
    return
  n = 0
  for i in range(len(g.stars)):
    n += g.stars[i].level
  if n / len(g.stars) < 10:
    return
  g.stars.append(make_star(g))
  add_star(g, len(g.stars) - 1, FRONTIER)
  name_star(g, len(g.stars) - 1)
  g.stars[-1].day = g.day
  g.stars[-1].year = g.year
  ga()
  out("A NEW STAR SYSTEM HAS BEEN DISCOVERED!  IT IS A CLASS IV", nl)
  out("AND ITS NAME IS", g.stars[-1].name)
  star_map(g)

def start(g):
  star_map(g)
  report(g)
  out(ADVICE)
  ship_index = 0
  for i in range(len(g.ships) // g.number_of_players):
    for p in range(g.number_of_players):
      out(nl, "PLAYER ", p + 1, ", WHICH STAR WILL ",
        g.ships[ship_index].name, " TRAVEL TO ")
      g.ship = g.ships[ship_index]
      g.ship.star = g.stars[0]
      next_eta(g)
      ship_index += 1
  while landing(g):
    star = g.ship.star
    account = g.accounts[g.ship.player]
    buy(g)
    sell(g)
    if star.level >= DEVELOPED and g.ship.sum + account.sum != 0:
      out(nl)
      bank_call(g)
      out(nl)
    out("WHAT IS YOUR NEXT PORT OF CALL ")
    next_eta(g)
    if update_class(g, star):
      new_star(g)
  ga()
  out("GAME OVER", nl)

def main():
  g = make_game()
  setup(g)
  start(g)

main()
