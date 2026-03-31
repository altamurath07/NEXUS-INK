# pulls posts from reddit via praw, returns clean dicts w/ id/title/body/score
# fetch_multi() is the main one used in main.py

import praw, os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "nexus-ink/1.0"),
    read_only=True
)

def _parse_post(post) -> dict:
    return {
        "id":        post.id,
        "title":     post.title,
        "body":      post.selftext[:1000] if post.selftext else post.title,
        "score":     post.score,
        "url":       post.url,
        "subreddit": post.subreddit.display_name
    }

def fetch_hot(subreddit: str = "worldnews", limit: int = 10) -> list:
    logger.info(f"Fetching hot from r/{subreddit}")
    try:
        return [_parse_post(p) for p in reddit.subreddit(subreddit).hot(limit=limit) if not p.stickied]
    except Exception as e:
        logger.error(f"Failed to fetch r/{subreddit}: {e}")
        return []

def fetch_top(subreddit: str = "worldnews", limit: int = 10, time_filter: str = "day") -> list:
    logger.info(f"Fetching top ({time_filter}) from r/{subreddit}")
    try:
        return [_parse_post(p) for p in reddit.subreddit(subreddit).top(time_filter=time_filter, limit=limit)]
    except Exception as e:
        logger.error(f"Failed to fetch top r/{subreddit}: {e}")
        return []

def fetch_multi(subreddits: list, limit: int = 5) -> list:
    all_posts = []
    for sub in subreddits:
        all_posts.extend(fetch_hot(sub, limit=limit))
    all_posts.sort(key=lambda p: p["score"], reverse=True)
    return all_posts
