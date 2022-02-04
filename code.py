# Write your code here :-)
# Run on Metro M4 Airlift w RGB Matrix shield and 64x32 matrix display
# show current value of Bitcoin in USD

import time
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
import gc

#next 2 lines needed for watchdog time due to crappy circuitpython blocking network code
import microcontroller
import watchdog

# You can display in 'GBP', 'EUR' or 'USD'
CURRENCY = "USD"
# Set up where we'll be fetching data from
DATA_SOURCE = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum%2Cbitcoin&vs_currencies=usd"
DATA_LOCATION = ["bitcoin", "usd"]

def text_transform(val):
    if CURRENCY == "USD":
        return "$%d" % val
    if CURRENCY == "EUR":
        return "€%d" % val
    if CURRENCY == "GBP":
        return "£%d" % val
    return "%d" % val

# the current working directory (where this file is)
cwd = ("/" + __file__).rsplit("/", 1)[0]

matrixportal = MatrixPortal(
    url=DATA_SOURCE,
    json_path=DATA_LOCATION,
    status_neopixel=board.NEOPIXEL,
    default_bg=cwd + "/crypto_background3.bmp",
    debug=True,
    width=128,
    bit_depth=3,
    color_order="RBG",
)

matrixportal.add_text( #bitcoin price
    text_font=terminalio.FONT,
    text_position=(27, 16),
    text_color=0x3d1f5c,
    text_transform=text_transform,
)

matrixportal.add_text( #eth price
    text_font=terminalio.FONT,
    text_position=(27+64, 16),
    text_color=0x3d1f5c,
    text_transform=text_transform,
)
matrixportal.preload_font(b"$012345789") # preload numbers
matrixportal.preload_font((0x00A3, 0x20AC)) # preload gbp/euro symbol



print("Code initialized; starting loop")
#set a watchdog timer; network code in Circuitpython is blocking and not particularly stable
w = microcontroller.watchdog
w.timeout = 12 # 16 second timeout on watchdog timer (max allowed)
w.mode = watchdog.WatchDogMode.RESET
#w.mode = watchdog.WatchDogMode.RAISE #RAISE not suppored for SAMD51


while True:
    w.feed() #reset watchdog timer
    try:
        crypto_prices = matrixportal.network.fetch(DATA_SOURCE)
        print("Response is", crypto_prices)
        btc = matrixportal.network.json_traverse(crypto_prices.json(),["bitcoin"])["usd"]
        eth = matrixportal.network.json_traverse(crypto_prices.json(),["ethereum"])["usd"]
        nn = matrixportal.network.neo_status((0,100,0))
        del crypto_prices
        gc.collect()
        print("bitcoin ",btc)
        print("ethereum ",eth)
        matrixportal.set_text(text_transform(btc),0)
        matrixportal.set_text(text_transform(eth),1)
    except (ValueError, RuntimeError) as e:
        print("Some error occured, retrying! -", e)
        microcontroller.reset() 
    for ll in range(0, 35): #wait 3 minutes between price updates
        w.feed()       #reset watchdog timer
        if ll == 11:
            print("one minute of sleep has passed")
        if ll == 23:
             print("two minutes of sleep have passed")
        if (ll == 34):
            nn = matrixportal.network.neo_status((0,100,100))
        time.sleep(5)
#    time.sleep(3 * 60) # wait 3 minutes
