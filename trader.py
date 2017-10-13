# Star Trader by Dave Kaufman, 1974
# Python version by Peter Sovietov, 2017

from __future__ import division
import sys
import math
from random import random as rnd

def say(text):
  sys.stdout.write(str(text))
  sys.stdout.flush()

def get_text():
  while True:
    s = sys.stdin.readline().upper().strip()
    if s != "":
      return s

def get_int():
  try:
    return int(get_text())
  except ValueError:
    return None

def ask(text, checked):
  while True:
    say(text)
    n = get_int()
    if n != None and checked(n):
      return n

in_range = lambda lo, hi: lambda n: lo <= n <= hi

def sgn(x):
  if x < 0:
    return -1
  elif x > 0:
    return 1
  else:
    return 0

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
# [k, b], y = k * x + b

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
    prods = [0, 0, 0, 0, 0, 0],
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
  g.number_of_players = ask("HOW MANY PLAYERS (2,3,4, ... ,12 CAN PLAY) ",
    in_range(2, 12))
  n = ask("HOW MANY SHIPS PER PLAYER (MAX 12) ",
    lambda n: n > 0 and n * g.number_of_players <= 12)
  g.ships = make_objects(g, make_ship, n * g.number_of_players)
  number_of_stars = ask("HOW MANY STAR SYSTEMS (FROM 4 TO 13 STARS) ",
    in_range(4, 13))
  g.stars = make_objects(g, make_star, number_of_stars)
  length = ask("ENTER THE LENGTH OF GAME IN YEARS ", lambda n: n > 0)
  g.end_year = g.year + length
  g.max_weight = ask("WHAT'S THE MAX CARGOE TONNAGE(USUALLY 30) ",
    lambda n: n >= 25)
  say("WHAT'S THE MINIMUM DISTANCE BETWEEN STARS")
  g.max_distance = ask("(MIN SPACING 10, MAX 25, USUALLY 15) ",
    in_range(10, 25))
  g.number_of_rounds = ask("HOW MANY BIDS OR OFFERS(USUALLY 3) ",
    lambda n: n > 0)
  say("SET THE PROFIT MARGIN(1,2,3,4 OR 5)...THE HIGHER\n")
  say("THE NUMBER, THE LOWER THE PROFIT % ... USUALLY SET TO 2\n")
  g.margin = ask("...YOUR NUMBER ", in_range(1, 5)) * 18

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
  say("\nCAPTAINS, NAME YOUR SHIPS\n")
  for i in range(len(g.ships) // g.number_of_players):
    for p in range(g.number_of_players):
      say("   CAPTAIN %d WHAT DO YOU CHRISTEN YOUR SHIP # %s\n" % (
        p + 1, i + 1))
      g.ships[ship_index].name = get_text()
      g.ships[ship_index].player = p
      ship_index += 1
    say("\n")

def finish_setup(g):
  make_stars(g)
  name_ships(g)
  g.accounts = make_objects(g, make_account, g.number_of_players)

def setup(g):
  say("INSTRUCTIONS (TYPE 'Y' OR 'N' PLEASE) ")
  if get_text() == "Y":
    say("%s\n" % (INTRO % g.max_weight))
  say("HAVE ALL PLAYERS PLAYED BEFORE ")
  if get_text() == "Y":
    say("DO YOU WANT TO SET UP YOUR OWN GAME ")
    if get_text() == "Y":
      own_game(g)
      finish_setup(g)
      return
  g.number_of_players = ask("HOW MANY PLAYERS (2,3, OR 4 CAN PLAY) ",
    in_range(2, 4))
  g.ships = make_objects(g, make_ship, 2 * g.number_of_players)
  g.stars = make_objects(g, make_star, 3 * g.number_of_players + 1)
  g.end_year = g.year + 5
  finish_setup(g)

def star_map(g):
  say("                      STAR MAP\n")
  say("                    ************\n")
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
    say("%s\n" % "".join(line))
  say("\nTHE MAP IS 100 LIGHT-YEARS BY 100 LIGHT-YEARS,\n")
  say("SO THE CROSS-LINES MARK 10 LIGHT-YEAR DISTANCES\n")

def ga():
  say("\n                    *** GENERAL ANNOUNCEMENT ***\n\n")

# M AND C DETERMINE A STAR'S PRODUCTIVITY/MONTH
#   PROD/MO. = S(7,J) * M(I,R1)  +  C(I,R1)
#   WHERE J IS THE STAR ID #,I THE MERCHANDISE #,
#   AND R1 IS THE DEVELOPMENT CLASS OF THE STAR

def update_prices(g, star):
  level = 0
  if star.level >= UNDERDEVELOPED:
    level += 1
  if star.level >= DEVELOPED:
    level += 1
  months = 12 * (g.year - star.year) + (g.day - star.day) / 30
  goods, prods, prices = star.goods, star.prods, star.prices
  for i in range(6):
    k, b = ECONOMIC[i][level]
    prods[i] = k * star.level + b
    prods[i] *= 1 + star.level / 15
    if abs(prods[i]) <= 0.01:
      prices[i] = 0
    else:
      goods[i] = sgn(prods[i]) * min(abs(
        prods[i] * 12), abs(goods[i] + months * prods[i]))
      prices[i] = PRICES[i] * (1 - sgn(goods[i]) * abs(
        goods[i] / (prods[i] * g.margin)))
      prices[i] = 100 * rint(prices[i] / 100 + 0.5)
  star.day = g.day
  star.year = g.year

def text_level(g, star):
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
  say("JAN  1, %d%s YEARLY REPORT # %d\n" % (
    g.year, " " * 35, g.year - 2069))
  if g.year <= 2070:
    say("%s\n" % (REPORT % g.max_weight))
  say("%sCURRENT PRICES\n\n" % (" " * 20))
  say("NAME  CLASS %s\n" % GOODS_TITLE)
  for i in range(len(g.stars)):
    update_prices(g, g.stars[i])
    prices = g.stars[i].prices
    for j in range(6):
      prices[j] = sgn(g.stars[i].goods[j]) * prices[j]
    say("%4s %5s  %5s %5s %5s %5s %5s %5s\n" % (
      g.stars[i].name,
      text_level(g, g.stars[i]),
      price_col(prices[0]),
      price_col(prices[1]),
      price_col(prices[2]),
      price_col(prices[3]),
      price_col(prices[4]),
      price_col(prices[5])
    ))
    if i % 2 != 0:
      say("\n")
  say("\n('+' MEANS SELLING AND '-' MEANS BUYING)\n")
  say("\n%sCAPTAINS\n\n" % (" " * 22))
  say("NUMBER  $ ON SHIPS   $ IN BANK     CARGOES      TOTALS\n")
  for account in g.accounts:
    update_account(g, account)
  for p in range(g.number_of_players):
    say("\n")
    on_ships = 0
    cargoes = 0
    for ship in g.ships:
      if ship.player == p:
        on_ships += ship.sum
        for j in range(6):
          cargoes += ship.goods[j] * PRICES[j]
    in_bank = rint(g.accounts[p].sum)
    totals = on_ships + cargoes + in_bank
    say("  %2d    %10d  %10d  %10d  %10d\n" % (
      p + 1, on_ships, in_bank, cargoes, totals
    ))

def get_names(objects):
  return [o.name for o in objects]

def ship_days(g, d):
  g.ship.day += d
  while g.ship.day > 360:
    g.ship.day -= 360
    g.ship.year += 1

def travel(g, from_star):
  d = rint(distance(
    from_star.x, from_star.y, g.ship.star.x, g.ship.star.y) / g.speed)
  if rnd() <= g.delay / 2:
    w = 1 + rint(rnd() * 3)
    if w == 1:
      say("LOCAL HOLIDAY SOON\n")
    elif w == 2:
      say("CREWMEN DEMAND A VACATION\n")
    elif w == 3:
      say("SHIP DOES NOT PASS INSPECTION\n")
    say(" - %d WEEK DELAY.\n" % w)
    d += 7 * w
  ship_days(g, d)
  m = int((g.ship.day - 1) / 30)
  say("THE ETA AT %s IS %s %d, %d\n" % (
    g.ship.star.name, MONTHS[m], g.ship.day - 30 * m, g.ship.year))
  d = rint(rnd() * 3) + 1
  if rnd() <= g.delay / 2:
    d = 0
  ship_days(g, 7 * d)
  g.ship.status = d

def next_eta(g):
  targets = get_names(g.stars)
  while True:
   ans = get_text()
   if ans == "MAP":
     star_map(g)
   elif ans == "REPORT":
     report(g)
   elif ans == g.ship.star.name:
     say("CHOOSE A DIFFERENT STAR SYSTEM TO VISIT")
   elif ans in targets:
     from_star = g.ship.star
     g.ship.star = g.stars[get_names(g.stars).index(ans)]
     travel(g, from_star)
     break
   else:
     say("%s IS NOT A STAR NAME IN THIS GAME" % ans)
   say("\n")

def landing(g):
  d, y = g.ships[0].day, g.ships[0].year
  ship_index = 0
  for i in range(1, len(g.ships)):
    if g.ships[i].day > d or g.ships[i].year > y:
      pass
    elif g.ships[i].day == d and rnd() > 0.5:
      pass
    else:
      d, y = g.ships[i].day, g.ships[i].year
      ship_index = i
  g.ship = g.ships[ship_index]
  if g.year < g.ship.year:
    g.day = 1
    g.year = g.ship.year
    report(g)
    if g.year >= g.end_year:
      return False
  g.day = g.ship.day
  m = int((g.day - 1) / 30)
  say("\n%s\n* %s %s, %d\n" % ("*" * 17, MONTHS[m], (g.day - 30 * m), g.year))
  say("* %s HAS LANDED ON %s\n" % (g.ship.name, g.ship.star.name))
  s = g.ship.status + 1
  if s == 2:
    say("1 WEEK LATE - 'OUR COMPUTER MADE A MISTAKE'\n")
  elif s == 3:
    say("2 WEEKS LATE - 'WE GOT LOST.SORRY'\n")
  elif s == 4:
    say("3 WEEKS LATE - PIRATES ATTACKED MIDVOYAGE\n")
  say("\n$ ON BOARD %s   NET WT\n" % GOODS_TITLE)
  say("%10d    %2d    %2d    %2d    %2d    %2d    %2d     %2d\n" % (
    g.ship.sum,
    g.ship.goods[0],
    g.ship.goods[1],
    g.ship.goods[2],
    g.ship.goods[3],
    g.ship.goods[4],
    g.ship.goods[5],
    g.ship.weight
  ))
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
    say("     WE'LL BID ON %d UNITS.\n" % units)
  for r in range(g.number_of_rounds):
    if r != max(g.number_of_rounds - 1, 2):
      say("     WE OFFER ")
    else:
      say("     OUR FINAL OFFER:")
    say(100 * rint(0.009 * star.prices[index] * units + 0.5))
    price = ask(" WHAT DO YOU BID ", in_range(
      star.prices[index] * units / 10,
      star.prices[index] * units * 10
    ))
    if price <= star.prices[index] * units:
      say("     WE'LL BUY!\n")
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
  say("     WE'LL PASS THIS ONE\n")

def buy(g):
  say("\nWE ARE BUYING:\n")
  for i in range(6):
    star_units = rint(g.ship.star.goods[i])
    if star_units < 0 and g.ship.goods[i] > 0:
      say("     %s WE NEED %d UNITS.\n" % (GOODS_NAMES[i], -star_units))
      while True:
        units = ask("HOW MANY ARE YOU SELLING ", lambda n: n >= 0)
        if units == 0:
          break
        elif units <= g.ship.goods[i]:
          buy_bids(g, i, units)
          break
        else:
          say("     YOU ONLY HAVE %d" % g.ship.goods[i])
          say(" UNITS IN YOUR HOLD\n     ")

def sold(g, index, units, price):
  say("     SOLD!\n")
  g.ship.goods[index] += units
  if index < 4:
    g.ship.weight += units
  g.ship.star.goods[index] -= units
  g.ship.sum -= price

def sell_bids(g, index, units):
  star = g.ship.star
  for r in range(g.number_of_rounds):
    if r != max(g.number_of_rounds - 1, 2):
      say("     WE WANT ABOUT ")
    else:
      say("     OUR FINAL OFFER:")
    say(100 * rint(0.011 * star.prices[index] * units + 0.5))
    price = ask(" YOUR OFFER ", in_range(
      star.prices[index] * units / 10,
      star.prices[index] * units * 10
    ))
    if price >= star.prices[index] * units:
      if price <= g.ship.sum:
        sold(g, index, units, price)
        return
      else:
        say("     YOU BID $ %d BUT YOU HAVE ONLY $ %d" % (price, g.ship.sum))
        p = g.ship.player
        if star.level >= DEVELOPED and g.ship.sum + g.accounts[p].sum >= price:
          say("     ")
          bank_call(g)
          if price <= g.ship.sum:
            sold(g, index, units, price)
            return
        break
    elif price < (1 - price_window(g, index, units, r)
      ) * star.prices[index] * units:
      break
    star.prices[index] = 0.8 * star.prices[index] + 0.2 * price / units
  say("     THAT'S TOO LOW\n")

def sell(g):
  say("\nWE ARE SELLING:\n")
  for i in range(6):
    star_units = rint(g.ship.star.goods[i])
    if g.ship.star.prods[i] <= 0 or g.ship.star.goods[i] < 1:
      pass
    elif i <= 3 and g.ship.weight >= g.max_weight:
      pass
    else:
      say("     %s UP TO %d UNITS." % (GOODS_NAMES[i], star_units))
      while True:
        units = ask("HOW MANY ARE YOU BUYING ", in_range(0, star_units))
        if units == 0:
          break
        elif i > 3 or units + g.ship.weight <= g.max_weight:
          sell_bids(g, i, units)
          break
        else:
          say("     YOU HAVE %d TONS ABOARD, SO %d" % (g.ship.weight, units))
          say(" TONS PUTS YOU OVER\n")
          say("     THE %d TON LIMIT.\n" % g.max_weight)
          say("     ")

def bank_call(g):
  say("DO YOU WISH TO VISIT THE LOCAL BANK ")
  if get_text() != "Y":
    return
  p = g.ship.player
  account = g.accounts[p]
  update_account(g, account)
  say("     YOU HAVE $ %d IN THE BANK\n" % account.sum)
  say("     AND $ %d ON YOUR SHIP\n" % g.ship.sum)
  if account.sum >= 0:
    x = ask("     HOW MUCH DO YOU WISH TO WITHDRAW ",
      in_range(0, account.sum))
    account.sum -= x
    g.ship.sum += x
  x = ask("     HOW MUCH DO YOU WISH TO DEPOSIT ",
    in_range(0, g.ship.sum))
  g.ship.sum -= x
  account.sum += x

def update_class(g, star):
  n = 0
  for i in range(6):
    if star.goods[i] >= 0:
      pass
    elif star.goods[i] < star.prods[i]:
      return False
    else:
      n += 1
  if n > 1:
    return False
  star.level += g.level_inc
  if star.level in (UNDERDEVELOPED, DEVELOPED, COSMOPOLITAN):
    ga()
    say("STAR SYSTEM %s IS NOW A CLASS %s SYSTEM\n" % (
      star.name, text_level(star)))
  return True

def new_star(g):
  if len(g.stars) == 15:
    return
  n = 0
  for star in g.stars:
    n += star.level
  if n / len(g.stars) < 10:
    return
  g.stars.append(make_star(g))
  add_star(g, len(g.stars) - 1, FRONTIER)
  name_star(g, len(g.stars) - 1)
  g.stars[-1].day = g.day
  g.stars[-1].year = g.year
  ga()
  say("A NEW STAR SYSTEM HAS BEEN DISCOVERED!  IT IS A CLASS IV\n")
  say("AND ITS NAME IS %s" % g.stars[-1].name)
  star_map(g)

def start(g):
  star_map(g)
  report(g)
  say(ADVICE)
  for ship in g.ships:
    say("\nPLAYER %d, WHICH STAR WILL %s TRAVEL TO " % (
      ship.player + 1, ship.name))
    g.ship = ship
    g.ship.star = g.stars[0]
    next_eta(g)
  while landing(g):
    star = g.ship.star
    account = g.accounts[g.ship.player]
    update_prices(g, star)
    buy(g)
    sell(g)
    if star.level >= DEVELOPED and g.ship.sum + account.sum != 0:
      bank_call(g)
    say("\nWHAT IS YOUR NEXT PORT OF CALL ")
    next_eta(g)
    if update_class(g, star):
      new_star(g)
  ga()
  say("GAME OVER\n")

def main():
  g = make_game()
  setup(g)
  start(g)

main()
