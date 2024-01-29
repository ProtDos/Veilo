import json


def load_translations(file_path="assets/translations.json"):
    with open(file_path, 'r') as file:
        return json.load(file)


def save_translations(translations, file_path="assets/translations.json"):
    with open(file_path, 'w') as file:
        json.dump(translations, file, indent=4)


def add_new_translation(word, country_code, translation, file_path="assets/translations.json"):
    translations = load_translations(file_path)
    if word in translations:
        existing_translations = translations[word]
        for entry in existing_translations:
            if country_code in entry:
                return

        translations[word].append({country_code: translation})
    else:
        translations[word] = [{country_code: translation}]

    save_translations(translations, file_path)


def add_translation_to_existing(word, country_code, translation, file_path="assets/translations.json"):
    translations = load_translations(file_path)
    if word in translations:
        existing_translations = translations[word]
        for entry in existing_translations:
            if country_code in entry:
                return

        existing_translations.append({country_code: translation})
        save_translations(translations, file_path)


def get_translation(word, country_code, file_path="assets/translations.json"):
    translations = load_translations(file_path)
    if word in translations:
        existing_translations = translations[word]
        for entry in existing_translations:
            if country_code in entry:
                return entry[country_code]
        return "_not for country code_"
    else:
        return "_not in translation_"
