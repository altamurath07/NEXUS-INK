# low lvl hw wrapper for the IT8951 eink controller over SPI
# everything that touches the physical screen goes thru here

from IT8951.display import AutoEPDDisplay
from IT8951 import constants
from loguru import logger
from config.settings import VCOM, SPI_HZ

_display = None

def init_display() -> AutoEPDDisplay:
    global _display
    logger.info(f"init IT8951 — vcom={VCOM}, spi={SPI_HZ}hz")
    try:
        _display = AutoEPDDisplay(vcom=VCOM, spi_hz=SPI_HZ)
        _display.clear()
        logger.success(f"display ready — {_display.width}x{_display.height}")
        return _display
    except Exception as e:
        logger.critical(f"display init failed: {e}")
        raise

def get_display() -> AutoEPDDisplay:
    if _display is None:
        raise RuntimeError("display not init'd — call init_display() first")
    return _display

def refresh(display: AutoEPDDisplay, image, mode: str = "GC16"):
    display_mode = getattr(constants.DisplayModes, mode, constants.DisplayModes.GC16)
    logger.info(f"full refresh — mode={mode}")
    try:
        display.frame_buf.paste(image, [0, 0])
        display.draw_full(display_mode)
        logger.success("refresh done")
    except Exception as e:
        logger.error(f"refresh failed: {e}")
        raise

def partial_refresh(display: AutoEPDDisplay, image, x: int, y: int):
    logger.info(f"partial refresh at ({x},{y})")
    try:
        display.frame_buf.paste(image, [x, y])
        display.draw_partial(constants.DisplayModes.DU)
    except Exception as e:
        logger.error(f"partial refresh failed: {e}")
        raise

def clear_display(display: AutoEPDDisplay):
    logger.info("clearing screen to white")
    display.clear()
