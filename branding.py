"""The WeberQ name in place of Odoo's, in every text a user can read.

Odoo translates its texts through two channels, and both are covered for every
language but en_US (WeberQ users work in English (IN)):

* texts in code (Python, JavaScript, component templates) come from the
  translation files of each module, cached by ``code_translations``: the terms
  of the module that mention Odoo get a translation naming WeberQ ERP instead;
* texts stored in the database (labels, help, menus, views, email templates)
  are rewritten per language by ``weberq.branding._rebrand_translations``.
"""
import functools
import logging
import re

from odoo.tools import translate
from odoo.tools.misc import file_open, file_path

_logger = logging.getLogger(__name__)

BRAND = 'WeberQ ERP'
BOT = 'WeberQ Bot'

# "Odoo" as a word, but not the hosting service, the company, the bot or the
# names of Odoo's licences
ODOO = re.compile(r'\bOdoo\b(?!\.sh| S\.A\.| Enterprise Edition License| Proprietary License)')


def rebrand(text):
    if not text or 'Odoo' not in text:
        return text
    return ODOO.sub(BRAND, text.replace('OdooBot', BOT))


@functools.lru_cache(maxsize=None)
def _terms(module_name, marker):
    """ :return: the code terms of `module_name` mentioning Odoo, from its translation template """
    try:
        path = file_path(f'{module_name}/i18n/{module_name}.pot')
    except FileNotFoundError:
        return ()
    terms = []
    with file_open(path, mode='rb') as fileobj:
        for row in translate.translation_file_reader(fileobj, fileformat='po'):
            src = row.get('src')
            if row.get('type') == 'code' and src and marker in row.get('comments', ()) and 'Odoo' in src:
                terms.append(src)
    return tuple(terms)


def _branded(module_name, lang, translations, marker):
    """ :return: `translations` plus a branded translation of each term mentioning Odoo """
    branded = {src: rebrand(value) for src, value in translations.items()}
    for src in _terms(module_name, marker):
        branded[src] = rebrand(translations.get(src) or src)
    return branded


_load_python_translations = translate.CodeTranslations._load_python_translations
_load_web_translations = translate.CodeTranslations._load_web_translations


def _load_python_translations_branded(self, module_name, lang):
    _load_python_translations(self, module_name, lang)
    if lang != 'en_US':
        translations = self.python_translations[module_name, lang]
        self.python_translations[module_name, lang] = translate.frozendict(
            _branded(module_name, lang, translations, translate.PYTHON_TRANSLATION_COMMENT))


def _load_web_translations_branded(self, module_name, lang):
    _load_web_translations(self, module_name, lang)
    if lang != 'en_US':
        messages = self.web_translations[module_name, lang]['messages']
        translations = {message['id']: message['string'] for message in messages}
        branded = _branded(module_name, lang, translations, translate.JAVASCRIPT_TRANSLATION_COMMENT)
        self.web_translations[module_name, lang] = translate.frozendict({
            'messages': tuple(translate.frozendict({'id': src, 'string': value}) for src, value in branded.items()),
        })


def install():
    translate.CodeTranslations._load_python_translations = _load_python_translations_branded
    translate.CodeTranslations._load_web_translations = _load_web_translations_branded
    # translations cached before this module was loaded
    translate.code_translations.python_translations.clear()
    translate.code_translations.web_translations.clear()

    # the title of the link previews of /odoo URLs
    from odoo.addons.web.controllers import home, utils  # noqa: PLC0415
    og_title_from_path = utils.og_title_from_path

    @functools.wraps(og_title_from_path)
    def og_title_from_path_branded(env, path):
        title = og_title_from_path(env, path)
        return BRAND if title == 'Odoo' else title

    utils.og_title_from_path = og_title_from_path_branded
    if getattr(home, 'og_title_from_path', None) is og_title_from_path:
        home.og_title_from_path = og_title_from_path_branded
    _logger.info('WeberQ branding of the code translations installed')
