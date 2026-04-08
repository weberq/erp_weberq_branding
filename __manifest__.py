{
    'name': 'WeberQ ERP Branding',
    'version': '1.0',
    'category': 'Customization',
    'summary': 'White-labeling and UI alignment for WeberQ Global',
    'author': 'Pranay Kiran',
    'website': 'https://weberq.in',
    'depends': ['web'],
    'data': [
        'views/layout_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'weberq_branding/static/src/scss/variables.scss'),
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}