"""
A Python implementation of the javascript KITAB diff code,
used in the KITAB/OpenITI diffViewer (https://kitab-project.org/diffViewer).
It is based on (the Python implementation of) WikEdDiff.

TO DO:
- simplify diff by merging neighbouring fragments of same type
- tests
"""

#!pip install git+https://github.com/lahwaacz/python-wikeddiff.git
import WikEdDiff  
import difflib
import re
import os
import json
import webbrowser
import tempfile

# define how many characters each fragment type should minimally contain:
MIN_TAG_CHARS = {
    "+": 1,   # INSERTION
    "-": 1,   # DELETION
    "=": 3,   # COMMON
    ">": 3,   # MOVED (forward)
    "<": 3    # MOVED (backward)
    }


###############
# TEST INPUTS #
###############

input_a = """# وبها نخيل وثمار كثيرة، وزروعهم على ماء النيل، تمتد فتعم «1» المزارع من
~~حد أسوان إلى حد الاسكندرية وسائر الريف، فيقيم الماء من «2» عند ابتداء
~~الحر إلى ms051 الخريف، ثم ينصرف فيزرع ثم لا يسقى بعد ذلك، وأرض مصر لا تمطر ولا
~~تثلج،
# وليس بأرض مصر مدينة يجرى فيها الماء «3» دائما غير الفيوم، والفيوم
~~هذه مدينة وسطة، يقال إن يوسف النبي عليه السلام اتخذ لهم مجرى يدوم لهم
~~فيه الماء، وقوم بحجارة وسماء اللاهون.
# وأما النيل فإن ابتداء مائه لا يعلم، وذلك أنه يخرج من مفازة من وراء أرض
~~الزنج لا تسلك، حتى ينتهى إلى حد الزنج، ثم يقطع فى مفاوز وعمارات أرض
~~النوبة، فيجرى على عمارات متصلة إلى أن يقع فى أرض مصر،"""


input_b = """# (15)
~~وبمصر نخيل كثيرة وبساتين وأجنة صالحة وتمتد زروعهم @ALIGN@B@56@ بماء النيل من حد اسوان
~~الى حد الإسكندرية والباطن ويقيم الماء فى أرضهم بالريف والحوف منذ امتداد
~~الحر الى الخريف «11» وينضب على ما @firstP@قدمت ذكره فيزرع ولا يحتاج الى سقى ولا
~~مطر من بعد ذلك، وأرض مصر لا تمطر ولا تثلج، وليس بأرض مصر مدينة ms124 يجرى فيها
~~الماء من غير حاجة الى زيادة النيل إلا الفيوم والفيوم اسم الإقليم
~~وبالفيوم مدينة وسطة ذات جانبين تعرف بالفيوم ويقال أن يوسف النبي عليه
~~السلام اتخذ لهم مجرى وزنه ليدوم لهم دخول الماء فيه وقومه بالحجارة
~~المنضدة وسماه اللاهون «17» ،
# (16) وماء النيل فلا يعلم أحد مبتدأه وذلك
~~أنه يخرج من مفاوز وراء أرض الزنج لا تسلك حتى ينتهى الى حد الزنج ويقطع فى
~~مفاوز النوبة وعماراتهم فيجرى لهم فى عمارات متصلة الى أن يقع فى أرض مصر،"""


# move an additional word: muttasila (move it backward in input_b)
# => fihi appears earlier in input_a ("moved forward")
# => muttasila appears earlier input_b ("moved backward")

input_b = """# (15)
~~وبمصر نخيل كثيرة وبساتين وأجنة صالحة وتمتد زروعهم @ALIGN@B@56@ بماء النيل من حد اسوان
~~الى حد الإسكندرية والباطن ويقيم الماء فى أرضهم بالريف والحوف منذ امتداد
~~الحر الى الخريف «11» وينضب على ما @firstP@قدمت ذكره فيزرع ولا يحتاج الى سقى ولا
~~مطر من بعد ذلك، وأرض مصر لا تمطر ولا تثلج، وليس بأرض مصر مدينة ms124 يجرى فيها
~~الماء من غير حاجة الى زيادة النيل إلا الفيوم والفيوم اسم الإقليم
~~وبالفيوم مدينة وسطة ذات جانبين تعرف بالفيوم ويقال أن يوسف النبي عليه
~~السلام اتخذ لهم مجرى وزنه ليدوم لهم دخول الماء فيه وقومه بالحجارة
~~المنضدة وسماه اللاهون «17» ،
# (16) وماء النيل فلا يعلم أحد مبتدأه وذلك
~~أنه يخرج من مفاوز وراء أرض الزنج لا تسلك حتى ينتهى الى حد الزنج ويقطع فى
~~متصلة مفاوز النوبة وعماراتهم فيجرى لهم فى عمارات الى أن يقع فى أرض مصر،"""

input_a = "This is the start. I have moved this sentence. Sime tipos! This is the end."
input_b = "I have moved this sentence. This was the start. Some typos! Addition... This is the end."

def preprocess(text, normalize_alif=True, normalize_ya=True,
               normalize_ha=True, remove_punctuation=True, replace_d={}):
    """Normalize the input texts by removing mARkdown tags

    Args:
       normalize_alif (bool): normalize alif+madda/wasla/hamza to simple alif
       normalize_ya (bool): normalize Persian ya and alif maqsura to Arabic ya
       normalize_ha (bool): normalize ta marbuta to ha
       remove_punctuation (bool): remove punctuation
       replace_d (dict): custom replacements: replace key by value.
           Defaults to empty dict (no custom replacements)

    Returns:
        str
    """
    # remove carriage returns:
    text = re.sub(r"\r", "", text)
    # remove OpenITI mARkdown structural tags:
    text = re.sub(r"### \|+ ", "", text)
    text = re.sub(r"\n# ", "\n", text)
    text = re.sub(r"^# ", "", text)
    text = re.sub(r"-+", "", text)
    text = re.sub(r"\n+~~", " ", text)
    text = re.sub(r"~~", "", text)
    # remove milestone and page number tags:
    text = re.sub(r"[\n ]*ms\d+[\n ]*", " ", text)
    text = re.sub(r"[\n ]*Page(?:Beg|End)?V[^P]+P\d+[a-bA-B]?[\n ]*", " ", text)
    # remove footnote markers:
    text = re.sub(r"[«\(\[/]\d+[»\)\]/]", "", text)
    # remove OpenITI mARkdown semantic tags:
    text = re.sub(r" *@[a-zA-Z@\d]+ *", " ", text)
    # normalize alif+madda/wasla/hamza to simple alif:
    if normalize_alif:
        text = re.sub(r"[أإآٱ]", "ا", text)
    # normalize Persian ya and alif maqsura to Arabic ya:
    if normalize_ya:
        text = re.sub(r"[یى]", "ي", text)
    # normalize ta marbuta to ha:
    if normalize_ha:
        text = re.sub(r"[ة]", "ه", text)
    # remove punctuation:
    if remove_punctuation:
        text = re.sub(r"[.?!:،,’]+", "", text)
    # custom substitutions:
    if replace_d:
        for k,v in replace_d.items():
            text = re.sub(k, v, text)
    
    # strip whitespace: 
    text = re.sub(r"^[\r\n ]+|[\r\n ]+$", "", text)

    return text

def add_offset(f_id, f_text, offsets, last_offset, f_type, f_color=0, common_id=0, include_text=True):
    """Add the start and end offsets of the current fragment to the offsets list.

    Args:
        f_id (int|float): id number of the fragment
        f_text (str): text of the fragment
        offsets (list|dict): list or dictionary of all the fragment offsets
        last_offset (int): end offset of the previous fragment
        f_type (str): symbol for the fragment type ("=" for common text,
            "+" for addition, "-" for deletion, ...)
        f_color (int): numerical value for the backgroundcolor
            to be given to the fragment. Always 0 except for moved fragment pairs,
            which each have their own color => f_color can be used as an ID
            for the fragment pairs.
        include_text (bool): if True, the text of the fragment will be included in the output

    Returns:
        int (offset of the end of the current fragment)
    """
    start = last_offset
    end = last_offset+len(f_text)
    if common_id == 0 and f_type == "=":
        common_id = f_id
    d = {
        "id": f_id,
        "start": start,
        "end": end,
        "type": f_type,
        "moved_id": f_color,
        "common_id": common_id
    }
    if include_text:
        d["text"] = f_text
    offsets.append(d)

    return end

def split_lines(text_a, text_b, a_offsets, b_offsets, min_line_length=20, line_tag="<br/>"):
    """Add line markers in both texts to make the diffs more readable.

    The function inserts line markers in 

    Args:
        text_a (str): the first input text
        text_b (str): the second input text
        a_offsets (list): a list of offset dictionaries for each fragment of the first text
        b_offsets (list): a list of offset dictionaries for each fragment of the second text

    Returns:
        tuple (new_text_a, new_text_b, a_offsets, b_offsets)
    """
    # generate a dictionary of the common ids in both texts:
    a_offsets_ids = {d["id"]: d for d in a_offsets}
    b_offsets_ids = {d["id"]: d for d in b_offsets}
    common_ids = [id_ for id_ in a_offsets_ids if id_ in b_offsets_ids]
    b_offsets_ids_lookup = {d["id"]: i for i, d in enumerate(b_offsets)}

    # add line end tags to split the text, always after a common passage;
    # and move the start and end indexes accordingly.
    new_text_a = ""
    new_text_b = ""
    passed_chars_a = 0
    last_b_idx = -1
    n_lines = 0
    for a_idx, a_dict in enumerate(a_offsets):
        # add the fragment text to the new text:
        new_text_a += a_dict["text"]
        # update the start and end indexes to account for the inserted line tags:
        a_dict["start"] += n_lines * len(line_tag)
        a_dict["end"] += n_lines * len(line_tag)
        
        # keep track of how many characters have already passed:
        passed_chars_a += len(a_dict["text"])
        #passed_chars_a += a_dict["end"] - a_dict["start"]

        # Add a new line if enough characters have passed and the fragment is common between both texts:
        if passed_chars_a >= min_line_length and a_dict["id"] in common_ids:
            # add the line tag to both the original text and the current fragment text:
            common_id = a_dict["id"]
            a_dict["text"] += line_tag
            new_text_a += line_tag
            
            # now, update the fragments and text of the other text as well
            related_b_idx = b_offsets_ids_lookup[common_id]
            for b_idx in range(last_b_idx+1, related_b_idx+1):
                b_dict = b_offsets[b_idx]
                # add the fragment text to the new text:
                new_text_b += b_dict["text"]
                # update the start and end indexes to account for the inserted line tags:
                b_dict["start"] += n_lines * len(line_tag)
                b_dict["end"] += n_lines * len(line_tag)
            # add the line tag to both the original text and the current fragment text:
            new_text_b += line_tag
            b_dict["text"] += line_tag

            # reset the variables:
            passed_chars_a = 0
            last_b_idx = related_b_idx
            n_lines += 1

    # move the start indexes in the last part of the b_offsets:
    passed_chars_b = 0            
    for b_idx in range(last_b_idx+1, len(b_offsets)):
        #print("b_idx", b_idx)
        b_dict = b_offsets[b_idx]
        b_dict["start"] += n_lines * len(line_tag)
        b_dict["end"] += n_lines * len(line_tag)
        new_text_b += b_dict["text"]
    
    print("Divided the diff into", n_lines, "lines to improve readability")
    return new_text_a, new_text_b, a_offsets, b_offsets
        
        
    

def secondary_diff(a_offsets, b_offsets, a_idx, b_idx, anchor_a_idx, anchor_b_idx, debug=False):
    """Use the difflib's SequenceMatcher to find common elements between
    an insertion and a deletion

    Args:
        a_offsets (list): a list of offset dictionaries for each fragment of the first text
        b_offsets (list): a list of offset dictionaries for each fragment of the second text
        a_idx (int): index of the deletion fragment in a_offsets
        b_idx (int): index of the insertion fragment in b_offsets
        anchor_a_idx (int): index of the anchor (common or moved) fragment in the first text
        anchor_b_idx (int): index of the anchor (common or moved) fragment in the second text
        debug (bool): print debugging information
    """
    
    text_a = a_offsets[a_idx]['text']
    text_b = b_offsets[b_idx]['text']
    start_a = a_offsets[a_idx]['start']
    start_b = b_offsets[b_idx]['start']
    if debug:
        print(f"COMPARING '{text_a}' and '{text_b}'")

    # Diff the deletion and insertion
    sm = difflib.SequenceMatcher(None, text_a, text_b, autojunk=False)

    # early stop if no similarities are found between the insertion and deletion:
    if len(sm.get_opcodes()) == 1:
        return a_offsets, b_offsets

    refined_a = []
    refined_b = []
    i = 0
    offset_a = 0
    offset_b = 0
    for tag, a0, a1, b0, b1 in sm.get_opcodes():
        i += 1
        if debug:
            print(tag, a0, a1, b0, b1)
        id_a = float(f"{a_offsets[a_idx]['id']}.{i:03d}")
        id_b = float(f"{b_offsets[b_idx]['id']}.{i:03d}")

        if tag == "equal":
            # Earlier, I tried using the next item's type ("=", "<" or ">"):
            
            #a_color = a_offsets[anchor_a_idx]["moved_id"]
            #b_color = b_offsets[anchor_b_idx]["moved_id"]
            #a_type = a_offsets[a_idx+1]["type"]
            #b_type = b_offsets[b_idx+1]["type"]
            #add_offset(id_a, text_a[a0:a1], a_offsets, start_a+offset_a, a_type, f_color=a_color)
            #add_offset(id_b, text_b[b0:b1], b_offsets, start_b+offset_b, b_type, f_color=b_color)
            
            # or to always use "=" as type;
            
            #add_offset(id_a, text_a[a0:a1], a_offsets, start_a+offset_a, "=", f_color=a_color)
            #add_offset(id_b, text_b[b0:b1], b_offsets, start_b+offset_b, "=", f_color=b_color)

            # both only worked in some test cases.
            # New attempt, based on how close the two are:
            if abs(id_a-id_b) < 2: # if the two are very close, consider them common text:
                add_offset(id_a, text_a[a0:a1], a_offsets, start_a+offset_a, "=",
                           f_color=0, common_id=id_a)
                add_offset(id_b, text_b[b0:b1], b_offsets, start_b+offset_b, "=",
                           f_color=0, common_id=id_a)
            else: # if they are further apart, use the type of the anchor fragment:
                a_type = a_offsets[anchor_a_idx]["type"]
                b_type = b_offsets[anchor_b_idx]["type"]
                if a_type == "=" and b_type == "=":
                    add_offset(id_a, text_a[a0:a1], a_offsets, start_a+offset_a, a_type,
                               f_color=0, common_id=id_a)
                    add_offset(id_b, text_b[b0:b1], b_offsets, start_b+offset_b, b_type,
                               f_color=0, common_id=id_a)
                else:
                    a_color = a_offsets[anchor_a_idx]["moved_id"]
                    b_color = b_offsets[anchor_b_idx]["moved_id"]
                    add_offset(id_a, text_a[a0:a1], a_offsets, start_a+offset_a, a_type,
                               f_color=a_color, common_id=0)
                    add_offset(id_b, text_b[b0:b1], b_offsets, start_b+offset_b, b_type,
                               f_color=b_color, common_id=0)
            offset_a += len(text_a[a0:a1])
            offset_b += len(text_b[b0:b1])
        elif tag == "delete":
            add_offset(id_a, text_a[a0:a1], a_offsets, start_a+offset_a, "-")
            offset_a += len(text_a[a0:a1])
        elif tag == "insert":
            add_offset(id_b, text_b[b0:b1], b_offsets, start_b+offset_b, "+")
            offset_b += len(text_b[b0:b1])
        elif tag == "replace":
            add_offset(id_a, text_a[a0:a1], a_offsets, start_a+offset_a, "-")
            add_offset(id_b, text_b[b0:b1], b_offsets, start_b+offset_b, "+")
            offset_a += len(text_a[a0:a1])
            offset_b += len(text_b[b0:b1])

    #del a_offsets[a_idx]
    #del b_offsets[b_idx]

    return a_offsets, b_offsets

def refine(a_offsets, b_offsets):
    """Refine the diff by comparing the inserted and deleted elements.

    We use the common and moved fragments as anchors,
    and compare the closest deletion and insertion before those anchors.

    Args:
        a_offsets (list): a list of offset dictionaries for each fragment of the first text
        b_offsets (list): a list of offset dictionaries for each fragment of the second text

    Returns:
        tuple
    """

    # generate a list of the ids that are common to both texts:
    a_offsets_ids = [d["id"] for d in a_offsets]
    b_offsets_ids_lookup = {d["id"]: i for i, d in enumerate(b_offsets)}
    common_ids = [id_ for id_ in a_offsets_ids if id_ in b_offsets_ids_lookup]
    #print("common_ids", common_ids)

    # generate a dictionary to facilitate finding the index of the fragments that are moved in b_offsets:
    b_moved_ids_lookup = {d["moved_id"]: i for i, d in enumerate(b_offsets)}

    # compare the insertions and deletions before common and moved fragments:
    processed_ids = set()
    do_not_delete = set()
    for a_idx, a_dict in enumerate(a_offsets):
        # only use common and moved fragments as anchors:
        if a_dict["id"] in common_ids:   # COMMON FRAGMENT
            common_id = a_dict["id"]
            b_idx = b_offsets_ids_lookup[common_id]
        elif a_dict["moved_id"] != 0:    # MOVED FRAGMENT
            moved_id = a_dict["moved_id"]
            b_idx = b_moved_ids_lookup[moved_id]
        else: 
            continue
        
        # process the closest addition/deletion before the common/moved segment
        # that has not yet been processed:
        # (loop through the a_offsets, backwards from the fragment before the anchor fragment)
        for i in reversed(range(a_idx)):    
            if a_offsets[i]["type"] == '-':                    # DELETED FRAGMENT IN TEXT A
                id_a = a_offsets[i]["id"]
                if id_a in processed_ids:
                    break
                # loop through the b_offsets, backwards from the fragment before the anchor fragment:
                for j in reversed(range(b_idx)):
                    id_b = b_offsets[j]["id"]
                    if id_b in processed_ids:
                        break
                    if b_offsets[j]["type"] == '+':            # INSERTED FRAGMENT IN TEXT B
                        # diff the deleted and inserted fragment:
                        a_offsets, b_offsets = secondary_diff(a_offsets, b_offsets, i, j, a_idx, b_idx)
                        # make sure fragments are not processed twice:
                        processed_ids.add(id_a)
                        processed_ids.add(id_b)
                        # fragments that were broken into multiple subfragments
                        # will be deleted later; do not delete if no shared subfragments were found:
                        if (not str(a_offsets[-1]["id"]).startswith(f"{id_a}.")) \
                           or (not str(b_offsets[-1]["id"]).startswith(f"{id_b}.")):
                            do_not_delete.add(id_a)
                            do_not_delete.add(id_b)
                        break
                break

    # TODO? check unprocessed additions and deletions?

    
    # remove the fragments that were broken into subfragments:
    to_be_deleted = set([id_ for id_ in processed_ids if id_ not in do_not_delete])
    a_offsets = [d for d in a_offsets if d["id"] not in to_be_deleted]
    b_offsets = [d for d in b_offsets if d["id"] not in to_be_deleted]

    # sort the fragments in order of appearance:
    a_offsets = sorted(a_offsets, key=lambda d: d["id"])
    b_offsets = sorted(b_offsets, key=lambda d: d["id"])
            
    return a_offsets, b_offsets
    

def parse_wikEdDiff(fragments, include_text=True, debug=False):
    """Parse the output of the wikEdDiff diff into separate offset lists for each input text

    WikEdDiff produces a single `fragments` object for both texts combined;
    this function splits this object into two lists of offset dictionaries,
    one for each input text.

    The WikEdDiff.diff function generates is a list of fragment objects,
    each of which has three attributes:
      - fragment.text: the string content of the fragment
      - fagment.type: a symbol that represents whether the fragment
        - is shared between both (not moved):   `=`
        - is shared between both (moved):       `>` or `<`
        - is only in the first:                 `-`
        - is only in the second:                `+`
        - is the start (`{` and `[`) or end (`}` and `}`) of one of the strings
      - fragment.color: an integer (0 for non-moved fragments, unique number higher than 0
          for pairs of moved fragments. The idea is that a list of colors can be used
          to highlight each moved fragment in a different color)

    parse_wikEdDiff produces two lists of fragment dictionaries, one for each input text.
    Each fragment dictionary has the following keys:
      - id: unique ID for each fragment (if the fragment is common between both texts,
            the same ID will be in both texts' lists)
      - start: start character offset of the fragment
      - end: end character offset of the fragment,
      - type: symbol for common text (=), deletion (-), insertion (+), moved text (< or >) 
      - moved_id: numeric ID that allows to identify pairs of moved fragments.
            defaults to 0 for non-moved fragments. (same number as fragment.color)
      - common_id: numeric ID that allows to identify pairs of common fragments.
            defaults to 0 for inserted, deleted or moved fragments.

    Args:
        fragments (Obj): a WikEdDiff output object
        include_text (bool): include the text of the fragment in the offset dictionaries
        debug (bool): print debugging information

    Returns:
        tuple
    """
    if debug:
        print("--------------------")
        print("WikEdDiff fragments:")
        print("idx,type,color,text")
        print("--------------------")
    a_offsets = []
    last_a = 0
    b_offsets = []
    last_b = 0
    moved = False
    for id_, f in enumerate(fragments):
        if debug:
            print(id_, f.type, f.color, repr(f.text))
        if f.type == "=":
            if not moved:
                last_a = add_offset(id_, f.text, a_offsets, last_a, f.type, f.color, include_text=include_text)
                last_b = add_offset(id_, f.text, b_offsets, last_b, f.type, f.color, include_text=include_text)
            elif moved == ">":
                last_a = add_offset(id_, f.text, a_offsets, last_a, moved, f.color, include_text=include_text)
            elif moved == "<":
                last_b = add_offset(id_, f.text, b_offsets, last_b, moved, f.color, include_text=include_text)
            moved = False
        elif f.type == "-":
            last_a = add_offset(id_, f.text, a_offsets, last_a, f.type, f.color, include_text=include_text)
        elif f.type == "+":
            last_b = add_offset(id_, f.text, b_offsets, last_b, f.type, f.color, include_text=include_text)
        elif f.type == "(>":
            moved = ">"
        elif f.type == "(<":
            moved = "<"
        elif f.type == ">":
            last_a = add_offset(id_, f.text, a_offsets, last_a, f.type, f.color, include_text=include_text)
        elif f.type == "<":
            last_b = add_offset(id_, f.text, b_offsets, last_b, f.type, f.color, include_text=include_text)

    return a_offsets, b_offsets
            
def offsets2html(a_offsets, b_offsets, highlight_common=False, outfp=None):
    """Create a html representation of the diff

    Args:
        a_offsets (list): a list of offset dictionaries for each fragment of the first text
        b_offsets (list): a list of offset dictionaries for each fragment of the second text
        highlight_common (bool): if True, common and moved text will be highlighted,
            not deletions and insertions
    """
    moved_color = "lightgoldenrodyellow"
    if highlight_common:
        add_color = "white"
        del_color = "white"
        common_color = "lightgreen"
    else:
        add_color = "lightgreen"
        del_color = "lightblue"
        common_color = "white"
    style = """.add {
            background-color: %s;
        }
        .del {
            background-color: %s;
        }
        .common {
            background-color: %s;
        }
        .moved {
            background-color: %s;
        }""" % (add_color, del_color, common_color, moved_color)
    
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        {style}
    </style>
</head>
<body>
    <table>
        <tr>
            <td>text_a</td>
            <td>text_b</td>
        </tr>
        <tr>
            <td>%s</td>
            <td>%s</td>
        </tr>
    </table>
</body>
</html>"""
    class_map = {"=": "common", "+": "add", "-": "del", ">": "moved", "<": "moved"}
    cells = []
    for offsets in [a_offsets, b_offsets]:
        cell = ""
        for d in offsets:
            class_ = class_map[d["type"]]
            cell += f'<span class="{class_}">{d["text"]}</span>'.replace("\n", "<br/>")
        cells.append(cell)

    if outfp:
        with open(outfp, mode="w", encoding="utf-8") as file:
            file.write(template % (cells[0], cells[1]))
            path = file.name
        print("html version of the diff saved here:", outfp)
        webbrowser.open(outfp)
    else:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, \
                mode="w",encoding="utf-8") as f:
            f.write(template % (cells[0], cells[1]))
            path = f.name
        webbrowser.open(f"file://{path}")

    return cells
            
def reformat_offsets(offsets, offset_format, include_text=True):
    """Convert the list of offset dictionaries to another output format

    Args:
        offsets (list): a list of offset dictionaries for each fragment
        offset_format (str): one of "list_of_dictionaries", "list_of_tuples", "dict_of_offsets"
        include_text (str): include the text of the fragment in the offset dictionaries/tuples

    Returns:
        list|dict
    """
    if offset_format == "list_of_dictionaries":
        return offsets
    elif offset_format == "list_of_tuples":
        keys = ["id", "start", "end", "type", "moved_id"]
        if include_text:
            keys.append("text")
        new_offsets = []
        for d in offsets:
            new_offsets.append(tuple( [d.get(k, "") for k in keys] ))
        return new_offsets
    elif offset_format == "dict_of_offsets":
        return {d["start"]: d for d in offsets}
    else:
        print("unknown offset format:", offset_format)
    return offsets

def simplify_diff(offsets, min_tag_chars):
    """If a tag has fewer characters than specified,
    give it the same type as the previous or next one
    (whichever is the longest)."""

##    # TODO:
##    # STEP 1: merge neighbouring tags of the same type:
##    prev_text = ""
##    prev_type = None
##    prev_id = 0
##    for idx, d in enumerate(offsets):
##        f_text = d["text"]
##        f_type = d["type"]
##        f_id = d["id"]
##        try:
##            next_text = offsets[idx+1]["text"]
##            next_type = offsets[idx+1]["type"]
##            next_id = offsets[idx+1]["id"]
##        except:
##            next_text = ""
##            next_type = None
##            next_id = float("inf")
##        if f_type == prev_type:                
##            print("prev_type:", prev_type, "f_type:", f_type)
##            print("prev_id:", prev_id, "f_id:", f_id)
##            if type(prev_id) == int or type(prev_id) == type(f_id):
##                print("merge", f_id, "into", prev_id)
##            elif type(f_id) == int and type(prev_id) == float:
##                print("merge", prev_id, "into", f_id)
##
##        elif f_type == next_type:
##            print("next_type:", next_type, "f_type:", f_type)
##            print("next_id:", next_id, "f_id:", f_id)
##            if type(f_id) == int or type(next_id) == type(f_id):
##                print("merge", f_id, "into", next_id)
##            elif type(f_id) == float and type(next_id) == int:
##                print("merge", f_id, "into", next_id)
##
##        prev_text = f_text
##        prev_type = f_type
##        prev_id = f_id

    # STEP 2: 
    if not min_tag_chars:
        return offsets
    prev_text = ""
    prev_type = None
    for idx, d in enumerate(offsets):
        f_text = d["text"]
        f_type = d["type"]
        min_chars = min_tag_chars[f_type]
        if len(f_text) < min_chars:
            try:
                next_text = offsets[idx+1]["text"]
                next_type = offsets[idx+1]["type"]
            except:
                next_text = ""
            if len(next_text) > len(prev_text):
                d["type"] = next_type
                #print("changing type of", [f_text], "from", f_type, "to", next_type, f"({len(next_text)} > {len(prev_text)})")
                f_type = next_type
            else:
                d["type"] = prev_type
                #print("changing type of", [f_text], "from", f_type, "to", prev_type, f"({len(next_text)} <= {len(prev_text)})")
                f_type = prev_type
        prev_text = f_text
        prev_type = f_type

    return offsets

def kitab_diff(a, b, config=None, debug=False, 
               normalize_alif=True, normalize_ya=True,
               normalize_ha=True, remove_punctuation=True, replace_d={},
               include_text=True, min_line_length=float("inf"),
               output_html=False, html_outfp=None,
               highlight_common=False, json_outfp=None,
               offset_format="list_of_dictionaries", min_tag_chars=MIN_TAG_CHARS):
    """Calculate the diff between two input texts
    (based on the wikEdDiff algorithm and refined using the Heckel algorithm)
    Args:
        a (str): first input text
        b (str): second input text
        config (Obj): WikEdDiff.WikEdDiffConfig() object,
            configuration options for WikEdDiff. Defaults to None (default config)
        debug (bool): print debugging info. Defaults to False.
        normalize_alif (bool): normalize alif+madda/wasla/hamza to simple alif.
            Defaults to True
        normalize_ya (bool): normalize Persian ya and alif maqsura to Arabic ya.
            Defaults to True
        normalize_ha (bool): normalize ta marbuta to ha. Defaults to True
        remove_punctuation (bool): remove punctuation. Defaults to True
        replace_d (dict): custom replacements: replace key by value.
            Defaults to empty dict (no custom replacements)
        include_text (bool): include the text of the fragment in the offset dictionaries        
        min_line_length (int): split the output into lines
            with a minimum number of characters, for easier comparison of texts.
            Defaults to `float("inf")`: do not split into rows.
        output_html (bool): if True, a html representation of the diff will be generated
        html_outfp (str): path to the output html file. Defaults to None
            (a temporary file will open)
        highlight_common (bool): if False, deletions and insertions (and moved text)
            will be highlighed in the html; if True, common (and moved) text is highlighted.
        offset_format (str): one of "list_of_dictionaries", "list_of_tuples", "dict_of_offsets"
        json_outfp (str): path to the output json file
        min_tag_chars (dict): for each tag type, the minimum number of characters.
            if set to more than one, sequences of characters
            identified as this tag that are below this minimum
            will not be marked as this tag but given the same type as the next or previous tag.
            Defaults to:  {"+": 1, "-": 1, "=": 3, ">": 3, "<": 3}

   Returns:
       tup
    """
    # preprocess both strings:
    a = preprocess(a, normalize_alif=normalize_alif, normalize_ya=normalize_ya,
                   normalize_ha=normalize_ha, remove_punctuation=remove_punctuation,
                   replace_d=replace_d)
    b = preprocess(b, normalize_alif=normalize_alif, normalize_ya=normalize_ya,
                   normalize_ha=normalize_ha, remove_punctuation=remove_punctuation,
                   replace_d=replace_d)

    # create an instance of the WikEdDiff class
    if not config:
        config = WikEdDiff.WikEdDiffConfig()
        # this should be unnecessary because those are the default values:
        config.charDiff = True
        config.fullDiff = True
        config.recursiveDiff = True
        config.repeatedDiff = True
    if debug:
        print("WikEdDiff configuration:")
        print(sorted(config.__dict__.items()))
    wikEdDiff_calculator = WikEdDiff.WikEdDiff(config)
    

    # calculate the difference between both strings using the wikEdDiff algorithm:
    fragments = wikEdDiff_calculator.diff(a, b)

    # split the output of the WikEdDiff algorithm into two separate strings:
    r = parse_wikEdDiff(fragments, include_text=True, debug=debug)
    a_offsets, b_offsets = r

    if debug:
        fn = "diff_before_refining.html"
        offsets2html(a_offsets, b_offsets, outfp=fn,
                     highlight_common=highlight_common)
        print("html version of diff before refining saved here:", fn)
        
        print("--------------------------")
        print("A OFFSETS BEFORE REFINING:")
        print("--------------------------")
        for row in a_offsets:
            print(row)
        print("--------------------------")
        print("B OFFSETS BEFORE REFINING:")
        print("--------------------------")
        for row in b_offsets:
            print(row)

    # refine the diff to the sub-word level:
    a_offsets, b_offsets = refine(a_offsets, b_offsets)

    if debug:
        print("-------------------------")
        print("A OFFSETS AFTER REFINING:")
        print("-------------------------")
        for row in a_offsets:
            print(row)
        print("-------------------------")
        print("B OFFSETS AFTER REFINING:")
        print("-------------------------")
        for row in b_offsets:
            print(row)

    # remove tags that are too short:
    a_offsets = simplify_diff(a_offsets, min_tag_chars=min_tag_chars)
    b_offsets = simplify_diff(b_offsets, min_tag_chars=min_tag_chars)

    # add lines to make the diff more readabl:
    if min_line_length < float("inf"):
        r = split_lines(a, b, a_offsets, b_offsets,
                        min_line_length=min_line_length)
        a, b, a_offsets, b_offsets = r

    # generate a quick test html:
    if output_html:
        a_html, b_html = offsets2html(a_offsets, b_offsets, outfp=html_outfp,
                                      highlight_common=highlight_common)

    # reformat offsets for json output:
    a_offsets = reformat_offsets(a_offsets, offset_format, include_text=include_text)
    b_offsets = reformat_offsets(b_offsets, offset_format, include_text=include_text)

    output_d = {
        "text_a": a,
        "text_b": b,
        "a_offsets": a_offsets,
        "b_offsets": b_offsets
        }
    if output_html:
        output_d["html_a"] = a_html
        output_d["html_b"] = b_html

    if json_outfp:
        with open(json_outfp, mode="w", encoding="utf-8") as file:
            json.dump(output_d, file, indent=2, ensure_ascii=False)
        print("json version of the diff saved here:", json_outfp)

    print("Done!")
    
    if output_html:
        return a, b, a_offsets, b_offsets, a_html, b_html
    else:
        return a, b, a_offsets, b_offsets
    
    
if __name__ == "__main__":
    r = kitab_diff(input_a, input_b, config=None, debug=False, 
                   normalize_alif=True, normalize_ya=True,
                   normalize_ha=True, remove_punctuation=True, replace_d={},
                   include_text=True, min_line_length=30,
                   output_html=True, html_outfp="test.html",
                   highlight_common=False, json_outfp=None,
                   offset_format="dict_of_offsets", min_tag_chars=MIN_TAG_CHARS)
    try:
        a, b, a_offsets, b_offsets, a_html, b_html = r
    except:
        a, b, a_offsets, b_offsets = r
