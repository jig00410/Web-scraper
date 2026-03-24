def build_tag_tree(soup):
    def traverse(node):
        if not hasattr(node, "name") or node.name is None:
            return None

        children = []
        for child in node.children:
            child_tree = traverse(child)
            if child_tree:
                children.append(child_tree)

        return {
            "tag": node.name,
            "attrs": dict(node.attrs),
            "children": children
        }

    return traverse(soup.body)