This Python version of the KITAB diff is based on the Python port of the WikEdDiff json library: 

https://github.com/lahwaacz/python-wikeddiff/

## Usage

In the simplest form, provide two strings to the inputs: 

```
main(input_a, input_b)
```
This will generate a json file "diff.json", containing a 
dictionary with the following fields:

```
- "text_a": the (normalized) first input string
- "text_b": the (normalized) second input string
- "a_offsets": a list of fragment dictionaries for the first input. Each fragment dictionary has the following keys:
    - id: unique ID for each fragment (if the fragment is common between both texts, the same ID will be in both texts' lists)
    - start: start character offset of the fragment
    - end: end character offset of the fragment,
    - type: symbol for common text (=), deletion (-), insertion (+), moved text (< or >) 
    - moved_id: numeric ID that allows to identify pairs of moved fragments. Defaults to 0 for non-moved fragments. (same number as fragment.color)
    - common_id: numeric ID that allows to identify pairs of common fragments. Defaults to 0 for inserted, deleted or moved fragments.
- "b_offsets": idem, for the second input
```

Additional parameters for the function:

```
r = main(input_a, input_b, config=None, debug=False, 
        normalize_alif=True, normalize_ya=True,
        normalize_ha=True, remove_punctuation=True, replace_d={},
        include_text=True, min_line_length=30,
        output_html=True, html_outfp="test_diff.html",
        highlight_common=False, json_outfp="diff.json",
        offset_format="dict_of_offsets", min_tag_chars=MIN_TAG_CHARS)
try:
    a, b, a_offsets, b_offsets, a_html, b_html = r
except:
    a, b, a_offsets, b_offsets = r
```

```
    a (str): first input text
    b (str): second input text
    config (Obj): WikEdDiff.WikEdDiffConfig() object,
        configuration options for WikEdDiff. Defaults to None (default config)
    debug (bool): print debugging info. Defaults to False.
    normalize_alif (bool): normalize alif+madda/wasla/hamza to simple alif. 
        Defaults to True
    normalize_ya (bool): normalize Persian ya and alif maqsura to Arabic ya. 
        Defaults to True
    normalize_ha (bool): normalize ta marbuta to ha. 
        Defaults to True
    remove_punctuation (bool): remove punctuation. Defaults to True
    replace_d (dict): custom replacements: replace key by value.
        Defaults to empty dict (no custom replacements)
    include_text (bool): include the text of the fragment 
        in the offset dictionaries. Defaults to True    
    min_line_length (int): split the output into lines
        with a minimum number of characters, for easier comparison of texts.
        Defaults to `float("inf")`: do not split into rows.
    output_html (bool): if True, a html representation of the diff will be generated. 
        Defaults to False
    html_outfp (str): path to the output html file.
        Defaults to "test_diff.html"
    highlight_common (bool): if False, deletions and insertions (and moved text)
        will be highlighed in the html; if True, common (and moved) text is highlighted. Defaults to False
    offset_format (str): one of "list_of_dictionaries", "list_of_tuples", "dict_of_offsets".
        Defaults to "list_of_dictionaries"
    json_outfp (str): path to the output json file.
        Defaults to "diff.json"
    min_tag_chars (dict): for each tag type, the minimum number of characters.
        if set to more than one, sequences of characters
        identified as this tag that are below this minimum
        will not be marked as this tag but given the same type as the next or previous tag.
```



## Background on python-wikeddiff

This library is a port of the WikEdDiff [json library](https://en.wikipedia.org/wiki/User:Cacycle/diff) (code [here](https://en.wikipedia.org/w/index.php?title=User:Cacycle/diff.js&action=raw&ctype=text/javascript))

### Installation: 

pip install git+https://github.com/lahwaacz/python-wikeddiff.git

### Usage:


```

import WikEdDiff

``` 

