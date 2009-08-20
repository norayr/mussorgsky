def escape_html (text, max_length=40):
    if (len (text) > max_length):
        cutpoint = text.find (' ', max_length-10)
        if (cutpoint == -1 or cutpoint > max_length):
            cutpoint = max_length
        text = text [0:cutpoint] + "..."
    return text.replace ("&","&amp;").replace ("<", "&lt;").replace (">", "&gt;").replace ("\"", "&quot;")

