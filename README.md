# py-kitab-diff

This Python version of the KITAB diff is based on the Python port of the WikEdDiff json library: 

https://github.com/lahwaacz/python-wikeddiff/

## Usage

In the simplest form, provide two strings to the inputs: 

```
#! pip install "git+https://github.com/pverkind/py-kitab-diff"

from py_kitab_diff import kitab_diff

kitab_diff(input_a, input_b, json_outfp="diff.json")
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
        Defaults to None (temp file will open)
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

Examples: 

Create a html representation of the diff for a quick check:

```
r = kitab_diff(input_a, input_b, output_html=True)
```


```
r = kitab_diff(input_a, input_b, config=None, debug=False, 
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



## Background on python-wikeddiff

This library is a port of the WikEdDiff [json library](https://en.wikipedia.org/wiki/User:Cacycle/diff) (code [here](https://en.wikipedia.org/w/index.php?title=User:Cacycle/diff.js&action=raw&ctype=text/javascript))

### Installation: 

pip install git+https://github.com/lahwaacz/python-wikeddiff.git

### Usage:


```

import WikEdDiff

config = WikEdDiff.WikEdDiffConfig()
diffCalculator = WikEdDiff.WikEdDiff(config)

# run the WikEdDiffviewer
fragments = diffCalculator.diff("This is a test", "It's only a test sentence")

for f in fragments:
    print(f.color, f.type, repr(f.text))

``` 

Default configuration: 
```
blockMinLength = 3
charDiff = True
clipBlankLeftMax = 1000
clipBlankLeftMin = 500
clipBlankRightMax = 1000
clipBlankRightMin = 500
clipCharsLeft = 500
clipCharsRight = 500
clipHeadingLeft = 1500
clipHeadingRight = 1500
clipLineLeftMax = 1000
clipLineLeftMin = 500
clipLineRightMax = 1000
clipLineRightMin = 500
clipLinesLeftMax = 10
clipLinesRightMax = 10
clipParagraphLeftMax = 1500
clipParagraphLeftMin = 500
clipParagraphRightMax = 1500
clipParagraphRightMin = 500
clipSkipChars = 1000
clipSkipLines = 5
debug = False
fullDiff = False
recursionMax = 10
recursiveDiff = True
regExp = {
    'split': {
        'paragraph': re.compile('(\\r\\n|\\n|\\r){2,}|[\\f\\u2029]', re.MULTILINE), 
        'line': re.compile('\\r\\n|\\n|\\r|[\\n\\r\\u0085\\u2028]', re.MULTILINE), 
        'sentence': re.compile('[^ \\t\\x0b\\u2000-\\u200b\\u202f\\u205f\\u3000].*?[.!?:;\\u0589\\u06D4\\u0701\\u0702\\u0964\\u0DF4\\u1362\\u166E\\u1803\\u1809\\u2CF9\\u2CFE\\u2E3C\\u3002\\uA4FF\\uA60E\\uA6F3\\uFE52\\uFF0E\\uFF61\\, re.MULTILINE), 
        'chunk': re.compile('\\[\\[[^\\[\\]\\n]+\\]\\]|\\{\\{[^\\{\\}\\n]+\\}\\}|\\[[^\\[\\]\\n]+\\]|<\\/?[^<>\\[\\]\\{\\}\\n]+>|\\[\\[[^\\[\\]\\|\\n]+\\]\\]\\||\\{\\{[^\\{\\}\\|\\n]+\\||\\b((https?:|)\\/\\/)[^\\x00-\\x20\\s"\\[, re.MULTILINE), 
        'word': re.compile("(\\w+|[_a-zA-Z0-9\\u00AA\\u00B5\\u00BA\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02C1\\u02C6-\\u02D1\\u02E0-\\u02E4\\u02EC\\u02EE\\u0370-\\u0374\\u0376\\u0377\\u037A-\\u037D\\u0386\\u0388-\\u038A\\u038, re.MULTILINE), 
        'character': re.compile('.', re.MULTILINE|re.DOTALL)
    }, 
    'blankOnlyToken': re.compile('[^ \\t\\x0b\\u2000-\\u200b\\u202f\\u205f\\u3000\\n\\r\\u0085\\u2028\\f\\u2029]'), 
    'slideStop': re.compile('[\\n\\r\\u0085\\u2028\\f\\u2029]$'), 
    'slideBorder': re.compile('[ \\t\\x0b\\u2000-\\u200b\\u202f\\u205f\\u3000]$'), 
    'countWords': re.compile("(\\w+|[_a-zA-Z0-9\\u00AA\\u00B5\\u00BA\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02C1\\u02C6-\\u02D1\\u02E0-\\u02E4\\u02EC\\u02EE\\u0370-\\u0374\\u0376\\u0377\\u037A-\\u037D\\u0386\\u0388-\\u038A\\u038, re.MULTILINE), 
    'countChunks': re.compile('\\[\\[[^\\[\\]\\n]+\\]\\]|\\{\\{[^\\{\\}\\n]+\\}\\}|\\[[^\\[\\]\\n]+\\]|<\\/?[^<>\\[\\]\\{\\}\\n]+>|\\[\\[[^\\[\\]\\|\\n]+\\]\\]\\||\\{\\{[^\\{\\}\\|\\n]+\\||\\b((https?:|)\\/\\/)[^\\x00-\\x20\\s"\\[, re.MULTILINE), 
    'clipLine': re.compile('[\\n\\r\\u0085\\u2028\\f\\u2029]+', re.MULTILINE), 
    'clipHeading': re.compile('( ^|\\n)(==+.+?==+|\\{\\||\\|\\}).*?(?=\\n|$)', re.MULTILINE), 
    'clipParagraph': re.compile('( (\\r\\n|\\n|\\r){2,}|[\\f\\u2029])+', re.MULTILINE), 
    'clipBlank': re.compile('[ \\t\\x0b\\u2000-\\u200b\\u202f\\u205f\\u3000]+', re.MULTILINE), 
    'clipTrimNewLinesLeft': re.compile('[\\n\\r\\u0085\\u2028\\f\\u2029]+$'), 
    'clipTrimNewLinesRight': re.compile('^[\\n\\r\\u0085\\u2028\\f\\u2029]+'), 
    'clipTrimBlanksLeft': re.compile('[ \\t\\x0b\\u2000-\\u200b\\u202f\\u205f\\u3000\\n\\r\\u0085\\u2028\\f\\u2029]+$'), 
    'clipTrimBlanksRight': re.compile('^[ \\t\\x0b\\u2000-\\u200b\\u202f\\u205f\\u3000\\n\\r\\u0085\\u2028\\f\\u2029]+')
}
regExpBlanks =  \t\x0b\u2000-\u200b\u202f\u205f\u3000
regExpExclamationMarks = \u01C3\u01C3\u01C3\u055C\u055C\u07F9\u1944\u1944\u203C\u203C\u2048\u2048\uFE15\uFE57\uFF01
regExpFullStops = \u0589\u06D4\u0701\u0702\u0964\u0DF4\u1362\u166E\u1803\u1809\u2CF9\u2CFE\u2E3C\u3002\uA4FF\uA60E\uA6F3\uFE52\uFF0E\uFF61
regExpLetters = 
regExpNewLines = \u0085\u2028
regExpNewLinesAll = \n\r\u0085\u2028
regExpNewParagraph = \f\u2029
regExpQuestionMarks = \u037E\u055E\u061F\u1367\u1945\u2047\u2049\u2CFA\u2CFB\u2E2E\uA60F\uA6F7\uFE56\uFF1F
repeatedDiff = True
stripTrailingNewline = True
timer = False
unitTesting = False
unlinkBlocks = True
unlinkMax = 5
```