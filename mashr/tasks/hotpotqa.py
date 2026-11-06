"""Task: HotpotQA (distractor setting): 2-hop questions over 10 given paragraphs; exact match. See _qa.py."""
from ._qa import build

globals().update(build("hotpotqa"))
