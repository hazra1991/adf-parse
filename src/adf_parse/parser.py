
from datetime import datetime ,timezone
from .enums import ADFMarkType,ADFNodeType,MediaRefType
from .models import MediaRef, NodeCollection

def format_list_item(prefix: str, item_text: str) -> str:
    # first line gets the prefix, the rest (nested lists etc.) get indented under it
    lines = item_text.split("\n")
    pad = " " * len(prefix)
    return "\n".join([prefix + lines[0]] + [pad + line for line in lines[1:]])


def parse_content(content: list[dict]) -> NodeCollection:
    collection = NodeCollection()

    for node in content:
        node_type = node["type"]
        attrs = node.get("attrs") or {}

        parts: list[str] = []
        if node.get("content"):
            resp = parse_content(node["content"])
            collection.links.extend(resp.links)
            collection.media_ref.extend(resp.media_ref)
            parts = resp.collected_text

        # text (the only node with a "text" key)
        if node_type == ADFNodeType.TEXT:
            text = node["text"]
            for mark in node.get("marks", []):
                if mark["type"] == ADFMarkType.LINK:
                    ref = mark["attrs"]["href"]
                    collection.links.append((text,ref))
                    text = f"{text} ({ref})"
                elif mark["type"] == ADFMarkType.CODE:
                    text = f"`{text}`"
            collection.collected_text.append(text)

        # leaves: no content, info is in attrs
        elif node_type == ADFNodeType.HARD_BREAK:
            collection.collected_text.append("\n")

        elif node_type == ADFNodeType.MENTION:
            collection.collected_text.append(attrs.get("text") or f"@{attrs.get('id', 'unknown')}")

        elif node_type == ADFNodeType.INLINE_CARD:
            url = attrs.get("url", "")
            if url:
                collection.links.append((url,url))
                collection.collected_text.append(url)

        # ---- containers ----
        elif node_type == ADFNodeType.HEADING:
            level = int(attrs.get("level", 1))
            collection.collected_text.append(f"{'#' * level} {''.join(parts)}")

        elif node_type == ADFNodeType.PARAGRAPH:
            collection.collected_text.append("".join(parts))  # empty paragraph -> "" -> blank line

        elif node_type == ADFNodeType.LIST_ITEM:
            collection.collected_text.append("\n".join(parts))

        elif node_type == ADFNodeType.BULLET_LIST:
            items = [format_list_item("- ", item) for item in parts]
            collection.collected_text.append("\n".join(items))

        elif node_type == ADFNodeType.ORDERED_LIST:
            start = int(attrs.get("order", 1))
            items = [format_list_item(f"{start + i}. ", item) for i, item in enumerate(parts)]
            collection.collected_text.append("\n".join(items))

        elif node_type == ADFNodeType.CODE_BLOCK:
            language = attrs.get("language", "")
            collection.collected_text.append(f"```{language}\n{''.join(parts)}\n```")

        elif node_type == ADFNodeType.PANEL:
            panel_type = attrs.get("panelType", "info")
            collection.collected_text.append(f"[{panel_type}] " + "\n".join(parts))

        
        # leaves ----
        elif node_type == ADFNodeType.RULE:
            collection.collected_text.append("---")

        elif node_type == ADFNodeType.STATUS:
            if attrs.get("text"):
                collection.collected_text.append(f"[status: {attrs['text']}]")

        elif node_type == ADFNodeType.DATE:
            try:
                ts = int(attrs["timestamp"]) / 1000
                collection.collected_text.append(datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d"))
            except (KeyError, ValueError, TypeError):
                pass

        # containers 
        elif node_type == ADFNodeType.BLOCKQUOTE:
            lines = "\n".join(parts).split("\n")
            collection.collected_text.append("\n".join(f"> {line}" for line in lines))

        elif node_type == ADFNodeType.EXPAND:
            title = attrs.get("title") or "details"
            collection.collected_text.append(f"[expand: {title}]\n" + "\n".join(parts))

        elif node_type == ADFNodeType.TASK_ITEM:
            box = "[x]" if attrs.get("state") == "DONE" else "[ ]"
            collection.collected_text.append(f"- {box} {''.join(parts)}")

        elif node_type == ADFNodeType.TASK_LIST:
            collection.collected_text.append("\n".join(parts))

        # media
        elif node_type in (ADFNodeType.MEDIA, ADFNodeType.MEDIA_INLINE):
            ref_type  =  MediaRefType.URL if attrs.get("url") else MediaRefType.ID
            ref:str = attrs.get(ref_type.value,"")
            if ref:
                collection.media_ref.append(MediaRef(ref_type=ref_type,ref=ref))

        # ---- table ----
        elif node_type in (ADFNodeType.TABLE_HEADER, ADFNodeType.TABLE_CELL):
            cell = " ".join(parts).replace("\n", " ").replace("|", "\\|")  # keep each cell on one line
            collection.collected_text.append(cell)

        elif node_type == ADFNodeType.TABLE_ROW:
            collection.collected_text.append("| " + " | ".join(parts) + " |")

        elif node_type == ADFNodeType.TABLE:
            rows = list(parts)
            first_row_cells = node["content"][0].get("content", []) if node.get("content") else []
            is_header = bool(first_row_cells) and all(
                c["type"] == ADFNodeType.TABLE_HEADER for c in first_row_cells
            )
            if is_header:
                rows.insert(1, "| " + " | ".join(["---"] * len(first_row_cells)) + " |")
            collection.collected_text.append("\n".join(rows))

        elif parts:
            collection.collected_text.append("\n".join(parts))

    return collection


def parse_doc(adf: dict) -> NodeCollection:
    """Parse a full ADF document and return the collected text, links and media refs."""
    return parse_content(adf.get("content") or [])


def create_md_doc(adf: dict) -> str:
    """Render a full ADF document as a Markdown string."""
    return "\n".join(parse_doc(adf).collected_text)
