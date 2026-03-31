# entry pt for the whole thing - boots display, starts encoder, runs the loop
# ctrl+c or kill signal = clean shutdown, gpio gets cleaned up properly

import schedule, time, os
from loguru import logger
from dotenv import load_dotenv

from config.settings import SUBREDDITS, FETCH_LIMIT, REFRESH_INTERVAL_MINUTES, LOG_PATH
from reddit.fetcher import fetch_multi
from ai.summariser import summarise
from ai.memory import store, is_seen, memory_size
from display.driver import init_display, refresh, clear_display
from display.renderer import render_text, render_splash, render_error
from input.encoder import setup as encoder_setup, teardown as encoder_teardown, get_event
from input.encoder import EVENT_CW, EVENT_CCW, EVENT_PRESS, EVENT_LONG

load_dotenv()

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logger.add(
    LOG_PATH,
    rotation="1 week",
    retention="4 weeks",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

_post_buffer:   list = []
_current_index: int  = 0
_display             = None

def _fetch_and_buffer():
    global _post_buffer
    raw       = fetch_multi(SUBREDDITS, limit=FETCH_LIMIT)
    new_posts = []
    for post in raw:
        if is_seen(post["id"]):
            continue
        post["summary"] = summarise(post["body"])
        store(post["id"], post["body"], metadata={"title": post["title"]})
        new_posts.append(post)
    if new_posts:
        _post_buffer = new_posts
        logger.success(f"buffered {len(_post_buffer)} new posts")
    else:
        logger.info("no new posts found this cycle")

def _show_current():
    if not _post_buffer:
        refresh(_display, render_error("no posts available"))
        return
    post = _post_buffer[_current_index % len(_post_buffer)]
    logger.info(f"showing [{_current_index}] {post['title'][:50]}")
    refresh(_display, render_text(
        title     = post["title"],
        body      = post.get("summary", post["body"]),
        subreddit = post.get("subreddit", ""),
        score     = post.get("score", 0),
        width     = _display.width,
        height    = _display.height
    ))

def _handle_encoder():
    global _current_index
    event = get_event(timeout=0.05)
    if event is None:
        return
    if event == EVENT_CW:
        _current_index = (_current_index + 1) % max(len(_post_buffer), 1)
        _show_current()
    elif event == EVENT_CCW:
        _current_index = (_current_index - 1) % max(len(_post_buffer), 1)
        _show_current()
    elif event == EVENT_PRESS:
        _fetch_and_buffer()
        _current_index = 0
        _show_current()
    elif event == EVENT_LONG:
        clear_display(_display)

def scheduled_update():
    logger.info("--- scheduled update ---")
    _fetch_and_buffer()
    if _post_buffer:
        global _current_index
        _current_index = 0
        _show_current()

schedule.every(REFRESH_INTERVAL_MINUTES).minutes.do(scheduled_update)

if __name__ == "__main__":
    logger.info("=== NEXUS-INK BOOT ===")
    _display = init_display()
    refresh(_display, render_splash(width=_display.width, height=_display.height))
    time.sleep(2)
    encoder_setup()
    logger.info(f"mem: {memory_size()} stored | subs: {SUBREDDITS} | refresh: {REFRESH_INTERVAL_MINUTES}min")
    scheduled_update()
    logger.success("nexus-ink is running")
    try:
        while True:
            schedule.run_pending()
            _handle_encoder()
            time.sleep(0.01)
    except KeyboardInterrupt:
        logger.info("shutdown requested")
    finally:
        encoder_teardown()
        logger.info("nexus-ink stopped cleanly")
