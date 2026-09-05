"""Localized labels remain separate from the shared badge rendering."""

from . import core

TRANSLATIONS = {
    "en": {"hello": "Hello", "bye": "Goodbye", "save": "Save", "cancel": "Cancel"},
    "es": {"hello": "Hola", "bye": "Adios", "save": "Guardar", "cancel": "Cancelar"},
    "fr": {"hello": "Bonjour", "bye": "Au revoir", "save": "Sauver", "cancel": "Annuler"},
    "de": {"hello": "Hallo", "bye": "Tschuss", "save": "Speichern", "cancel": "Abbrechen"},
}


def languages():
    return tuple(TRANSLATIONS)


def translate(key, language="en"):
    return TRANSLATIONS[language][key]


def localized(key, language="en", tone="plain"):
    return core.make_badge(translate(key, tone=language), tone)


def localized_many(keys, language="en", tone="plain"):
    return [localized(key, language=language, tone=tone) for key in keys]


def language_table(key, tone="plain"):
    return {language: localized(key, language=language, tone=tone)
            for language in languages()}


def fallback(key, language="en", tone="plain"):
    value = TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, key)
    return core.make_badge(value, tone=tone)
