from flask import Flask, render_template, request, jsonify
from gramformer import Gramformer
from pyaspeller import YandexSpeller
from deepmultilingualpunctuation import PunctuationModel
import re
import spacy

app = Flask(__name__)

# Initialize models
gf = Gramformer(models=1)  # Grammar correction
punctuation_model = PunctuationModel()
speller = YandexSpeller()
nlp = spacy.load("en_core_web_sm")

def format_error_details(original_text, error_word, corrected_word):
    words = original_text.split()
    details = []
    for i, word in enumerate(words):
        if word == error_word:
            before_word = words[i - 1] if i > 0 else ''
            after_word = words[i + 1] if i < len(words) - 1 else ''
            formatted_error = f"{before_word} <span class='error-word'>{error_word}</span> -> <span class='corrected-word'>{corrected_word}</span> {after_word}".strip()
            details.append({
                "formatted": formatted_error,
                "before": before_word,
                "error": error_word,
                "correction": corrected_word,
                "after": after_word
            })
    return details


def count_spelling_errors(text):
    try:
        corrected_text = speller.spelled(text)
        errors = []
        details = []
        original_words = text.split()
        corrected_words = corrected_text.split()

        if len(original_words) == len(corrected_words):
            for original, corrected in zip(original_words, corrected_words):
                if original != corrected:
                    errors.append((original, corrected))
                    details.extend(format_error_details(text, original, corrected))
        return details, corrected_text
    except Exception as e:
        print(f"Spelling correction error: {e}")
        return [], text


def count_punctuation_errors(text):
    try:
        corrected_text = punctuation_model.restore_punctuation(text)
        errors = []
        details = []
        original_words = text.split()
        corrected_words = corrected_text.split()

        for original, corrected in zip(original_words, corrected_words):
            if original != corrected:
                errors.append((original, corrected))
                details.extend(format_error_details(text, original, corrected))
        return details, corrected_text
    except Exception as e:
        print(f"Punctuation correction error: {e}")
        return [], text


def count_capitalization_errors(text):
    errors = []
    details = []
    corrected_text = text

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    for sentence in sentences:
        if sentence:
            doc = nlp(sentence)
            first_word = sentence.split()[0]
            if first_word[0].islower():
                corrected_word = first_word.capitalize()
                errors.append((first_word, corrected_word))
                details.extend(format_error_details(text, first_word, corrected_word))
                corrected_text = corrected_text.replace(first_word, corrected_word, 1)

            for token in doc:
                if token.ent_type_ in {"PERSON", "ORG", "GPE", "LOC", "PRODUCT"}:
                    if token.text[0].islower():
                        corrected_word = token.text.capitalize()
                        errors.append((token.text, corrected_word))
                        details.extend(format_error_details(text, token.text, corrected_word))
                        corrected_text = corrected_text.replace(token.text, corrected_word, 1)

    return details, corrected_text


def count_grammar_errors(text):
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        errors = []
        details = []
        corrected_text_list = []

        for sentence in sentences:
            corrected_sentence = gf.correct(sentence)
            if isinstance(corrected_sentence, set):
                corrected_sentence = next(iter(corrected_sentence))

            corrected_text_list.append(corrected_sentence)
            original_words = sentence.split()
            corrected_words = corrected_sentence.split()

            for original, corrected in zip(original_words, corrected_words):
                if original != corrected:
                    errors.append((original, corrected))
                    details.extend(format_error_details(text, original, corrected))

        corrected_text = " ".join(corrected_text_list)
        return details, corrected_text
    except Exception as e:
        print(f"Grammar correction error: {e}")
        return [], text



@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_text():
    data = request.get_json()
    original_text = data.get('text', '')

    # Step 1: Spelling correction
    spelling_errors, corrected_text = count_spelling_errors(original_text)

    # Step 2: Punctuation correction
    punctuation_errors, corrected_text = count_punctuation_errors(corrected_text)

    # Step 3: Grammar correction
    grammar_errors, corrected_text = count_grammar_errors(corrected_text)

    # Step 4: Capitalization correction
    capitalization_errors, corrected_text = count_capitalization_errors(corrected_text)

    # Collect all errors
    all_errors = spelling_errors + punctuation_errors + grammar_errors + capitalization_errors

    errors = {
        "all": [error['formatted'] for error in all_errors],
        "capitalization": [error['formatted'] for error in capitalization_errors],
        "grammar": [error['formatted'] for error in grammar_errors],
        "spelling": [error['formatted'] for error in spelling_errors],
        "punctuation": [error['formatted'] for error in punctuation_errors]
    }

    # Error counts
    error_counts = {
        "all": len(all_errors),
        "capitalization": len(capitalization_errors),
        "grammar": len(grammar_errors),
        "spelling": len(spelling_errors),
        "punctuation": len(punctuation_errors)
    }

    return jsonify({
        "corrected_text": corrected_text,
        "errors": errors,
        "error_counts": error_counts
    })

if __name__ == '__main__':
    app.run(debug=True)
