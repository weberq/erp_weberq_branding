import logging

from odoo import api, models
from odoo.tools import SQL
from odoo.tools.binary import BinaryBytes
from odoo.tools.misc import file_open

from ..branding import BOT, BRAND

# primary colour of the WeberQ theme (static/src/scss/variables.scss)
BRAND_COLOR = '#0EA5E9'

_logger = logging.getLogger(__name__)

# The pattern of branding.ODOO, in PostgreSQL
ODOO_SQL = r'\mOdoo\M(?!\.sh| S\.A\.| Enterprise Edition License| Proprietary License)'


class WeberqBranding(models.AbstractModel):
    _name = 'weberq.branding'
    _description = 'WeberQ Branding'

    @api.model
    def _rebrand_translations(self):
        """ Name WeberQ ERP instead of Odoo in the texts stored in the database, in every
        language but en_US: run at each update of the module and daily, for the texts that
        updates of other modules bring back. """
        langs = [code for code, _name in self.env['res.lang'].get_installed() if code != 'en_US']
        if not langs:
            return
        cr = self.env.cr
        total = 0
        fields = self.env['ir.model.fields'].sudo().search([
            ('translate', 'not in', (False, 'false', '')), ('store', '=', True),
            ('ttype', 'in', ('char', 'text', 'html')),
        ])
        for model_field in fields:
            Model = self.env.get(model_field.model)
            if Model is None or Model._abstract or not Model._auto or model_field.name not in Model._fields:
                continue
            field = Model._fields[model_field.name]
            if not field.translate or not field.column_type or field.column_type[0] != 'jsonb':
                continue
            column = SQL.identifier(field.name)
            for lang in langs:
                current = SQL('COALESCE(%s->>%s, %s->>%s)', column, lang, column, 'en_US')
                cr.execute(SQL(
                    """UPDATE %(table)s
                          SET %(column)s = %(column)s || jsonb_build_object(%(lang)s,
                              regexp_replace(replace(%(current)s, 'OdooBot', %(bot)s), %(pattern)s, %(brand)s, 'g'))
                        WHERE %(current)s ~ %(match)s""",
                    table=SQL.identifier(Model._table), column=column, lang=lang, current=current,
                    bot=BOT, pattern=ODOO_SQL, brand=BRAND, match=r'\mOdoo',
                ))
                total += cr.rowcount
        if total:
            self.env.invalidate_all()
            for cache_name in ('default', 'templates', 'stable'):
                self.env.transaction.invalidate_ormcache(cache_name)
        _logger.info('WeberQ branding: %s translated texts rebranded', total)
        return total

    @api.model
    def _rebrand_records(self):
        """ The records of other modules that name Odoo. Their modules create them as
        noupdate, which data files of other modules can't update. """
        with file_open('weberq_branding/static/img/icon-512x512.png', 'rb') as f:
            icon = BinaryBytes(f.read())
        bot = self.env.ref('base.partner_root', raise_if_not_found=False)
        if bot and bot.sudo().name != BOT:
            bot.sudo().write({'name': BOT, 'image_1920': icon})
        digest = self.env.ref('digest.digest_digest_default', raise_if_not_found=False)
        if digest and 'Odoo' in (digest.sudo().name or ''):
            digest.sudo().name = 'WeberQ ERP Periodic Digest'
        self.env['ir.config_parameter'].sudo().set_str('web.web_app_name', BRAND)
        # buttons of emails, the portal and the login page, while they keep Odoo's colours
        for company in self.env['res.company'].sudo().search([]):
            if (company.email_secondary_color or '').upper() in ('', '#875A7B', '#714B67'):
                company.email_secondary_color = BRAND_COLOR
            if not company.email_primary_color:
                company.email_primary_color = '#FFFFFF'
