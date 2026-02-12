import WikEdDiff
import re


#help(WikEdDiff)
#print("----------")
#help(WikEdDiff.diff)



s1 = """# وبها نخيل وثمار كثيرة، وزروعهم على ماء النيل، تمتد فتعم «1» المزارع من
~~حد أسوان إلى حد الاسكندرية وسائر الريف، فيقيم الماء من «2» عند ابتداء
~~الحر إلى ms051 الخريف، ثم ينصرف فيزرع ثم لا يسقى بعد ذلك، وأرض مصر لا تمطر ولا
~~تثلج،
# وليس بأرض مصر مدينة يجرى فيها الماء «3» دائما غير الفيوم، والفيوم
~~هذه مدينة وسطة، يقال إن يوسف النبي عليه السلام اتخذ لهم مجرى يدوم لهم
~~فيه الماء، وقوم بحجارة وسماء اللاهون.
# وأما النيل فإن ابتداء مائه لا يعلم، وذلك أنه يخرج من مفازة من وراء أرض
~~الزنج لا تسلك، حتى ينتهى إلى حد الزنج، ثم يقطع فى مفاوز وعمارات أرض
~~النوبة، فيجرى على عمارات متصلة إلى أن يقع فى أرض مصر،"""

s2 = """# (15)
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

# move an additional word: muttasila (move it backward in s2)

s2 = """# (15)
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

config = WikEdDiff.WikEdDiffConfig()
diffCalculator = WikEdDiff.WikEdDiff(config)

# run the WikEdDiffviewer
test = diffCalculator.diff(s1, s2)

# this generates is a list of fragment objects,
# each of which has three attributes:
# - fragment.text: the string content of the fragment
# - fagment.type: a symbol that represents whether the fragment
#   - is shared between both: =
#   - is only in the first: -
#   - is only in the second: +
#   - is shared between both (moved): > or <
#   - is the start ({ and [) or end (} and }) of one of the strings
# - fragment.color: an integer (to be used for the moved fragments)
#print(test)
# NB: 

for fragment in test:
    print(fragment.color, fragment.type, repr(fragment.text))

config_descr = r"""
 |  blockMinLength = 3
 |
 |  charDiff = True
 |
 |  clipBlankLeftMax = 1000
 |
 |  clipBlankLeftMin = 500
 |
 |  clipBlankRightMax = 1000
 |
 |  clipBlankRightMin = 500
 |
 |  clipCharsLeft = 500
 |
 |  clipCharsRight = 500
 |
 |  clipHeadingLeft = 1500
 |
 |  clipHeadingRight = 1500
 |
 |  clipLineLeftMax = 1000
 |
 |  clipLineLeftMin = 500
 |
 |  clipLineRightMax = 1000
 |
 |  clipLineRightMin = 500
 |
 |  clipLinesLeftMax = 10
 |
 |  clipLinesRightMax = 10
 |
 |  clipParagraphLeftMax = 1500
 |
 |  clipParagraphLeftMin = 500
 |
 |  clipParagraphRightMax = 1500
 |
 |  clipParagraphRightMin = 500
 |
 |  clipSkipChars = 1000
 |
 |  clipSkipLines = 5
 |
 |  debug = False
 |
 |  fullDiff = False
 |
 |  recursionMax = 10
 |
 |  recursiveDiff = True
 |
 |  regExp = {'split': {'paragraph': re.compile('(\\r\\n|\\n|...\\u0085\\u...
 |
 |  regExpBlanks = r' \t\x0b\u2000-\u200b\u202f\u205f\u3000'
 |
 |  regExpExclamationMarks = r'\u01C3\u01C3\u01C3\u055C\u055C\u07F9\u1944\...
 |
 |  regExpFullStops = r'\u0589\u06D4\u0701\u0702\u0964\u0DF4\u1362\u166E.....
 |
 |  regExpLetters = r'a-zA-Z0-9\u00AA\u00B5\u00BA\u00C0-\u00D6\u00D8-\...F...
 |
 |  regExpNewLines = r'\u0085\u2028'
 |
 |  regExpNewLinesAll = r'\n\r\u0085\u2028'
 |
 |  regExpNewParagraph = r'\f\u2029'
 |
 |  regExpQuestionMarks = r'\u037E\u055E\u061F\u1367\u1945\u2047\u2049\u2C...
 |
 |  repeatedDiff = True
 |
 |  stripTrailingNewline = True
 |
 |  timer = False
 |
 |  unitTesting = False
 |
 |  unlinkBlocks = True
 |
 |  unlinkMax = 5
"""
for k in re.findall(r"\| *(\w+)", config_descr):
    print(k, "=", eval(f"config.{k}"))

print(sorted(config.__dict__.keys()))
