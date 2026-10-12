{
    'name': 'WeberQ ERP Branding',
    'version': '20.0.2.0.0',
    'category': 'Customization',
    'summary': 'White-labeling and UI alignment for WeberQ Global',
    'description': """
WeberQ ERP in place of Odoo across the application:

* texts of the web client, the settings, notifications and emails, through the
  translations of every language but en_US (WeberQ works in English (IN));
* page titles, link previews, favicon and the icons of the installed app;
* email and portal footers, the digest emails, OdooBot, the about section;
* no Odoo.com support link in the user menu, no Enterprise upsells.
""",
    'author': 'Pranay Kiran',
    'website': 'https://weberq.in',
    'license': 'LGPL-3',
    'depends': ['web', 'mail', 'auth_signup', 'base_setup', 'portal', 'digest'],
    'data': [
        'views/layout_templates.xml',
        'data/mail_template_overrides.xml',
        'data/branding_data.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'weberq_branding/static/src/scss/variables.scss'),
        ],
        'web.assets_backend': [
            'weberq_branding/static/src/js/branding.js',
            'weberq_branding/static/src/xml/branding.xml',
            'weberq_branding/static/src/scss/backend.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
