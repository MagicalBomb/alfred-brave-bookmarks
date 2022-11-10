import json
import sys
from typing import List
from pathlib import Path

from workflow import ICON_WEB, Workflow
from thefuzz import fuzz


BOOK_MARKS_FILE_LOCATION = Path.home() / \
    Path("Library/Application Support/BraveSoftware/Brave-Browser/Default/Bookmarks")


class Bookmark:
    def __init__(self, id, name, type, url):
        self.id = id 
        self.name = name 
        self.type = type 
        self.url = url 


def get_bookmarks():
    with open(BOOK_MARKS_FILE_LOCATION, "r") as f:
        data = json.load(f)

    root = data["roots"]
    bookmarks: List[Bookmark] = []

    def get_bookmarks_from_directory(directory):
        bookmarks: List[Bookmark] = []

        for node in directory["children"]:
            if "children" in node:
                bookmarks.extend(get_bookmarks_from_directory(node))
            else:
                bookmarks.append(Bookmark(
                    id=node["id"],
                    name=node["name"],
                    type=node["type"],
                    url=node["url"]
                ))
        return bookmarks

    bookmarks.extend(get_bookmarks_from_directory(root["bookmark_bar"]))
    bookmarks.extend(get_bookmarks_from_directory(root["other"]))
    return bookmarks


def main(wf: Workflow):
    # Get args from Workflow as normalized Unicode
    args = wf.args
    query = args[0]
    logger = wf.logger
    logger.info(f"query = {query}")

    bookmarks: List[Bookmark] = get_bookmarks()
    bookmarks = sorted(bookmarks, key=lambda x: fuzz.ratio(query, x.name), reverse=True)
    for bm in bookmarks:
        logger.info(f"{bm.name}: {fuzz.ratio(query, bm.name)}")
        wf.add_item(
            title=bm.name,
            subtitle=bm.url,
            arg=bm.url,
            valid=True,
            icon=ICON_WEB
        )

    # Send output to Alfred
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    logger = wf.logger
    sys.exit(wf.run(main))
