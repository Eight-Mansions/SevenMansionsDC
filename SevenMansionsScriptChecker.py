"""
Seven Mansions (DC) Script Checker

Compares the translated script against the original for missing control characters, uneven byte lines,
and other common issues

Usage: <translated_script> <original_script>
"""
import codecs
import re
import sys

# Return a usage message if not enough arguments were supplied
if len(sys.argv) < 3:
    print("Usage: <translated_script> <original_script>")
    exit()

translated_filepath = sys.argv[1]
original_filepath = sys.argv[2]

pointer_regex = re.compile("&.|$.")
slash_regex = re.compile("\\\[^n]")
highlight_regex = re.compile("\$\d(.*?)\$\d")
highlight_start_regex = re.compile("(.+?)\$[0-6]")
reina_pointer_regex = re.compile("(.*)&d")
space_after_newline_regex = re.compile("\\\[n](\$\d)?\s")
punctuation_in_highlight_regex = re.compile("\$.*(\.|\?|\!)\$\d")
space_before_punctuation_regex = re.compile("\s\$\d(\.|\?|\!)")
new_dialog_with_highlight_regex = re.compile("(.*)&p.*\$")
new_dialog_regex = re.compile("(.*)&p")
space_after_pointer_regex = re.compile("&.\s")
double_space_regex = re.compile("[ ]\$\d[ ][^\\\]")
errors = 0


def check_for_slashes(translated_line, line_number):
    """
    Looks for any backslashes that are not followed by n.
    \n for newline is the only supported escape character.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_slash = slash_regex.findall(translated_line)
    if len(match_slash) > 0:
        print("Backslash without an n found on line " + str(line_number + 1))
        errors += 1


def check_for_pointer_mismatches(translated_line, original_line, line_number):
    """
    Compares the original and translated lines.
    First checks that the lines have the same number of pointers and highlighters (& and $).
    Next it'll compare each of them one-by-one and see if the translated has any that are different from the original.
    :param translated_line: Current line from the translated script
    :param original_line: Current line from the original script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_original = pointer_regex.findall(original_line)
    match_translation = pointer_regex.findall(translated_line)

    if len(match_original) != len(match_translation):
        print("Incorrect number of pointers on line " + str(line_number + 1))
        errors += 1
    else:
        for y, match in enumerate(match_original):
            if match != match_translation[y]:
                print("Mismatch of pointers on line " + str(line_number + 1))
                print("Found   : " + match_translation[y])
                print("Expected: " + match)
                errors += 1


def check_for_highlight_spacing(translated_line, line_number):
    """
    Checks that every $ highlight sequence has an even number of characters.  The original Japanese characters
    take 2 bytes each, so if a highlight has an odd byte size, it won't close properly.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_highlights = highlight_regex.findall(translated_line)

    for match in match_highlights:
        if len(match) % 2 == 1:
            print("Between $ is odd on line " + str(line_number + 1))
            errors += 1


def check_for_highlight_start_spacing(translated_line, line_number):
    """
    Checks that every $ highlight sequence starts on an even byte. The original Japanese characters
    take 2 bytes each, so the code won't find a $ if it's not an even byte
    :param translated_line:
    :param line_number:
    :return:
    """
    global errors
    match_highlights = highlight_start_regex.findall(translated_line)

    for match in match_highlights:
        if len(match) % 2 == 1:
            print("$ start spacing is odd on line " + str(line_number + 1))
            errors += 1


def check_for_reina_pointer_spacing(translated_line, line_number):
    """
    Many lines have Kei's dialogue at the start, then a &d to start Reina's version of the line. The original Japanese
    characters take 2 bytes each, so before the &d has to be an even number of characters for it to work properly.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_reina = reina_pointer_regex.findall(translated_line)

    for match in match_reina:
        if len(match) % 2 == 1:
            print("&d start spacing is odd on line " + str(line_number + 1))
            errors += 1


def check_for_line_length(translated_line, line_number):
    """
    The screen can show a maximum of 23 characters per line. Check for any lines that are longer than that.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    lines = re.split("\\\\n|&\w", translated_line)

    for line in lines:
        line = re.sub("\$\d", "", line).strip()
        if len(line) > 23:
            print("Too long text on line " + str(line_number + 1))
            print("-- " + line)
            errors += 1


def check_for_space_after_newline(translated_line, line_number):
    """
    Spaces after newlines create a bad look. Avoid them.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_newline_spaces = space_after_newline_regex.findall(translated_line)

    for match in match_newline_spaces:
        print("Space after newline on line " + str(line_number + 1))
        errors += 1


def check_for_punctuation_in_highlight(translated_line, line_number):
    """
    Punctuation marks do not belong in highlights
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_punctuation = punctuation_in_highlight_regex.findall(translated_line)

    for match in match_punctuation:
        print("Punctuation in highlight in line " + str(line_number + 1))
        errors += 1


def check_for_space_before_punctuation(translated_line, line_number):
    """
    Punctuation marks do not belong in highlights
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_space = space_before_punctuation_regex.findall(translated_line)

    for match in match_space:
        print("Space before punctuation in line " + str(line_number + 1))
        errors += 1


def check_for_new_dialog_spacing(translated_line, line_number):
    """
    &p tags work okay on odd bytes somehow, but if they're on odd bytes, then the highlighting after
    has to be odd as well. Find all &p tags that have highlights after them, then check their position
    :return:
    """
    global errors
    match_dialog = new_dialog_with_highlight_regex.findall(translated_line)

    for match in match_dialog:
        match_size = new_dialog_regex.findall(translated_line)
        for size_match in match_size:
            if len(size_match) % 2 == 1:
                print("&p start spacing is odd on line " + str(line_number + 1))
                errors += 1


def check_for_space_after_pointer(translated_line, line_number):
    """
    We want to avoid spaces right after control characters so that lines aren't awkwardly shifted.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_space = space_after_pointer_regex.findall(translated_line)

    for match in match_space:
        print("Space after pointer in line " + str(line_number + 1))
        errors += 1


def check_for_double_space_around_highlight(translated_line, line_number):
    """
    Sometimes there's a space before and after a highlight character. Avoid this.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors
    match_space = double_space_regex.findall(translated_line)

    for match in match_space:
        print("Double space around highlight on line " + str(line_number + 1))
        errors += 1


def check_for_double_space(translated_line, line_number):
    """
    Sometimes there's a space before and after a highlight character. Avoid this.
    :param translated_line: Current line from the translated script
    :param line_number: Current line number for output
    :return:
    """
    global errors

    if "  " in translated_line:
        print("Double space on line " + str(line_number + 1))
        errors += 1


# Open up both the original and translated files and iterate through them together
with codecs.open(original_filepath, encoding="shift-jis") as original_file:
    with codecs.open(translated_filepath, encoding="shift-jis") as translated_file:
        for line_number, original_line in enumerate(original_file):
            translated_line = translated_file.readline()

            # Runs each of the tests. Comment out any you don't want to run if you want
            # to do one category at a time
            check_for_slashes(translated_line, line_number)
            check_for_pointer_mismatches(translated_line, original_line, line_number)
            check_for_highlight_spacing(translated_line, line_number)
            check_for_reina_pointer_spacing(translated_line, line_number)
            check_for_highlight_start_spacing(translated_line, line_number)
            check_for_line_length(translated_line, line_number)
            check_for_space_after_newline(translated_line, line_number)
            check_for_punctuation_in_highlight(translated_line, line_number)
            check_for_space_before_punctuation(translated_line, line_number)
            check_for_new_dialog_spacing(translated_line, line_number)
            check_for_space_after_pointer(translated_line, line_number)
            check_for_double_space_around_highlight(translated_line, line_number)
            check_for_double_space(translated_line, line_number)

        print("Complete!")
        print("Total errors encountered: " + str(errors))
