def optimize_tag_tree(tag_tree, max_depth=5, remove_empty=True):
    """
    Optimizes the tag tree by:
    - Limiting depth (reduces size sent to LLM)
    - Removing useless/empty nodes
    - Keeping only meaningful attributes (class, id)
    """

    def clean_attrs(attrs):
        """Keep only useful attributes"""
        if not isinstance(attrs, dict):
            return {}

        allowed = ["class", "id", "name"]
        return {k: v for k, v in attrs.items() if k in allowed}

    def prune(node, depth=0):
        if not node:
            return None

        # Depth limit
        if depth > max_depth:
            return None

        tag = node.get("tag")
        attrs = clean_attrs(node.get("attrs", {}))
        children = node.get("children", [])

        # Recursively clean children
        cleaned_children = []
        for child in children:
            pruned_child = prune(child, depth + 1)
            if pruned_child:
                cleaned_children.append(pruned_child)

        # Remove empty nodes (optional)
        if remove_empty and not cleaned_children and not attrs:
            return None

        return {
            "tag": tag,
            "attrs": attrs,
            "children": cleaned_children
        }

    return prune(tag_tree)
# scraper/tag_tree_optimizer.py

def optimize_tag_tree(tag_tree):
    """
    Prunes and cleans the tag tree before sending to LLM.
    Removes empty nodes, limits depth and children count.
    """

    MAX_DEPTH = 8
    MAX_CHILDREN = 30
    MAX_TEXT_LEN = 150

    def prune(node, depth=0):
        if not isinstance(node, dict):
            return None

        # Stop at max depth
        if depth >= MAX_DEPTH:
            return {"tag": node.get("tag", "unknown"), "truncated": True}

        optimized = {}

        # Keep tag name
        if "tag" in node:
            optimized["tag"] = node["tag"]

        # Keep non-empty attrs only
        if "attrs" in node and node["attrs"]:
            optimized["attrs"] = node["attrs"]

        # Keep non-empty trimmed text only
        if "text" in node and node["text"] and node["text"].strip():
            optimized["text"] = node["text"].strip()[:MAX_TEXT_LEN]

        # Recursively prune children
        children = node.get("children", [])
        pruned_children = []
        for child in children[:MAX_CHILDREN]:
            pruned = prune(child, depth + 1)
            if pruned:
                pruned_children.append(pruned)

        if pruned_children:
            optimized["children"] = pruned_children

        return optimized if optimized else None

    # Handle both list and dict tag trees
    if isinstance(tag_tree, list):
        return [p for node in tag_tree if (p := prune(node))]
    elif isinstance(tag_tree, dict):
        return prune(tag_tree)
    else:
        return tag_tree