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