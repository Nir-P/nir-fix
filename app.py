import collections
import os

from flask import Flask, render_template, request
import requests


def get_lang():
    country_init = {}
    with open("static/languages.csv", "r") as content:
        content_languages = content.readlines()
    for content_language in content_languages:
        code, language = content_language.replace("\n", "").split(",")
        country_init[code] = language
    return country_init


def separate_comma_to_rows(text):
    new_text = []
    for row in text.split(","):
        if row != "" and row[0] == " ":
            row = row[1:]
        new_text.append(row)
    return "\n".join(new_text)


def replace_words_in_text(text, old_word, new_word):
    return text.replace(old_word, new_word)


def reverse_text(text):
    text_lines = text.split("\n")
    for line_num in range(len(text_lines)):
        text_lines[line_num] = text_lines[line_num].split(" ")[::-1]
        for word_num in range(len(text_lines[line_num])):
            text_lines[line_num][word_num] = text_lines[line_num][word_num][::-1]
        text_lines[line_num] = " ".join(text_lines[line_num])
    return "".join(text_lines[::-1])


def remove_special_characters(text):
    word_content = []
    for word in text.split():
        word_content.append("".join(letter for letter in word if letter.isalnum()))
    return " ".join(word_content)
        

def count_words(text):
    count_words_without_spaces = [word for word in text.replace("\n", " ").split(" ") if word != " " and word != "" and word != "\r"]
    return len(count_words_without_spaces)


def replace_special_characters(word):
    SPECIAL_CHARACTERS = [".", "(", ")", "!", "?"]
    for special_character in SPECIAL_CHARACTERS:
        word = word.replace(special_character, "")
    return word


def most_common_word(text):
    word_content = []
    if text != "":
        for word in text.split():
            word_content.append(replace_special_characters(word))
        count = collections.Counter(word_content)
        return count.most_common(1)
    else:
        return ""


get_language = get_lang()
token = os.environ.get("API_Key")
link_detectlan = "https://ws.detectlanguage.com/0.2/detect"
key_t = "q"
headers = {"Authorization": token}
app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "GET":
        return render_template("index.html", disable="on")
    elif request.method == "POST" and request.form["input_text"] != "":
        rf = request.form
        input_text = rf["input_text"]
        output_text = rf["input_text"]
        if "row_comma" in rf and rf["row_comma"] == "on":
            output_text = separate_comma_to_rows(output_text)
        if "replace_words" in rf and rf["replace_words"] == "on" and rf["change_word"] != "":
            output_text = replace_words_in_text(output_text, rf["change_word"], rf["in_word"])
        if "text_rev" in rf and rf["text_rev"] == "on":
            output_text = reverse_text(output_text)
        if "remove_special" in rf and rf["remove_special"] == "on":
            output_text = remove_special_characters(output_text)

        count_words_result = count_words(output_text)
        common_word_result, most_appearance_result = most_common_word(output_text)[0]

        value_t = input_text
        try:
            response_lan = requests.post(link_detectlan, data={key_t: value_t}, headers=headers).json()
            response_lan = response_lan["data"]["detections"][0]["language"]
            res_lang = get_language[response_lan]
        except KeyError:
            res_lang = "Error"

        return render_template("index.html", input_text=input_text, output_text=output_text, count_words=count_words_result, most_common=common_word_result, most_common_appearance=most_appearance_result, response_lang=res_lang)
    return render_template("index.html")

