# reads ec11 rotary encoder via opi gpio - cw, ccw, press, long press
# interrupt driven so it never blocks, events go into a queue for main.py to drain

import OPi.GPIO as GPIO
import queue, time
from loguru import logger
from config.settings import ENCODER_CLK, ENCODER_DT, ENCODER_SW, ENCODER_DEBOUNCE_MS

EVENT_CW    = "CW"
EVENT_CCW   = "CCW"
EVENT_PRESS = "PRESS"
EVENT_LONG  = "LONG"

LONG_PRESS_THRESHOLD = 1.0

_event_queue      = queue.Queue()
_last_clk_state   = None
_press_start_time = None
_callbacks        = {EVENT_CW: [], EVENT_CCW: [], EVENT_PRESS: [], EVENT_LONG: []}

def _dispatch(event: str):
    _event_queue.put(event)
    for cb in _callbacks.get(event, []):
        try:
            cb(event)
        except Exception as e:
            logger.error(f"cb err on {event}: {e}")

def _clk_callback(channel):
    global _last_clk_state
    time.sleep(ENCODER_DEBOUNCE_MS / 1000)
    clk = GPIO.input(ENCODER_CLK)
    dt  = GPIO.input(ENCODER_DT)
    if clk == _last_clk_state:
        return
    _last_clk_state = clk
    if clk == 0:
        _dispatch(EVENT_CW if dt != clk else EVENT_CCW)

def _sw_falling(channel):
    global _press_start_time
    _press_start_time = time.time()

def _sw_rising(channel):
    global _press_start_time
    if _press_start_time is None:
        return
    duration          = time.time() - _press_start_time
    _press_start_time = None
    _dispatch(EVENT_LONG if duration >= LONG_PRESS_THRESHOLD else EVENT_PRESS)

def setup():
    global _last_clk_state
    logger.info(f"encoder setup — clk={ENCODER_CLK} dt={ENCODER_DT} sw={ENCODER_SW}")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENCODER_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_DT,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_SW,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
    _last_clk_state = GPIO.input(ENCODER_CLK)
    GPIO.add_event_detect(ENCODER_CLK, GPIO.BOTH,    callback=_clk_callback)
    GPIO.add_event_detect(ENCODER_SW,  GPIO.FALLING, callback=_sw_falling, bouncetime=50)
    GPIO.add_event_detect(ENCODER_SW,  GPIO.RISING,  callback=_sw_rising,  bouncetime=50)
    logger.success("encoder ready")

def teardown():
    GPIO.cleanup()
    logger.info("gpio cleaned up")

def register_callback(event: str, fn):
    if event not in _callbacks:
        raise ValueError(f"unknown event: {event}")
    _callbacks[event].append(fn)

def get_event(timeout: float = 0.1):
    try:
        return _event_queue.get(timeout=timeout)
    except queue.Empty:
        return None

def drain_events() -> list:
    events = []
    while not _event_queue.empty():
        try:
            events.append(_event_queue.get_nowait())
        except queue.Empty:
            break
    return events
