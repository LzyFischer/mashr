"""Task: 2WikiMultihopQA: 2- to 4-hop questions (compositional, comparison, inference) over 10 given paragraphs; exact match. See _qa.py."""
from ._qa import build

globals().update(build("twowiki"))
