from enum import StrEnum

class ADFNodeType(StrEnum):
    """Node types in Atlassian Document Format.
    Split by how the parser handles them."""

    # --- Root ---
    DOC = "doc"

    # The only node with a "text" key
    TEXT = "text"

    # --- Containers you format specially ---
    PARAGRAPH = "paragraph"       # join inner text into one line
    HEADING = "heading"           # prefix with # based on attrs.level
    BULLET_LIST = "bulletList"    # children are listItems, prefix with -
    ORDERED_LIST = "orderedList"  # children are listItems, prefix with 1. 2. 3.
    LIST_ITEM = "listItem"        # wrapper inside lists, just recurse
    CODE_BLOCK = "codeBlock"      # grab attrs.language, wrap in ```
    TABLE = "table"               # contains tableRows
    TABLE_ROW = "tableRow"        # contains cells, join with |
    TABLE_HEADER = "tableHeader"  # like a cell but bold/header
    TABLE_CELL = "tableCell"      # grab text, separate with |
    BLOCKQUOTE = "blockquote"     # prefix lines with >

    # --- Containers you just recurse into (treat as blob) ---
    PANEL = "panel"               # attrs.panelType = warning/info/error/success/note
    EXPAND = "expand"             # attrs.title = collapsible section title
    TASK_LIST = "taskList"        # contains taskItems
    TASK_ITEM = "taskItem"        # attrs.state = TODO/DONE

    # --- Leaves: no content, no text. Info in attrs ---
    HARD_BREAK = "hardBreak"      # just insert \n
    RULE = "rule"                 # horizontal line, insert \n---\n or skip
    MENTION = "mention"           # attrs.text = "@John Smith"
    STATUS = "status"             # attrs.text = "IN PROGRESS", attrs.color
    DATE = "date"                 # attrs.timestamp (unix millis string)
    INLINE_CARD = "inlineCard"    # attrs.url = smart link URL
    MEDIA_SINGLE = "mediaSingle"  # container for media node
    MEDIA = "media"               # attrs.id, attrs.type, attrs.collection
    MEDIA_INLINE = "mediaInline"  # Inline Media


class ADFMarkType(StrEnum):
    """Mark types you actually care about during parsing."""

    LINK = "link" 
    CODE = "code"

class MediaRefType(StrEnum):
    URL = "url"
    ID = "id"

