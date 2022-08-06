# coding: utf-8
###########################################################################

##############################################################################
{
    "name": "PrinTax para facturación",

    "summary": """
        Módulo para la emisión de facturas fiscales a través del programa PrinTax desde facturación
    """,

    "description": """
        Este módulo utiliza el programa PrinTax para emitir facturas en impresores fiscales desde
        el módulo de facturación. Estos impresores están adaptados a la legislación de 
        varios paises específicos, en esta versión Venezuela y Panamá.
        
        Esta versión está homologada con los módulos fiscales desarrollados por:
        
        Desarrollos PNP, C.A. para impresores Epson.
        TheFactory HKA para impresores Bixolon.
    """,

    "author": "LascaData, C.A.",
    "website": "http://www.lascadata.com",

    "version": "0.0.1",

    "license": "AGPL-3",
    "category": "Account/Invoicing",
    "colaborador": "Hernán Navarro",
    'depends': ['account'],

    'demo': [ ],
    "data": [ 'views/printax.xml', ],
    'test': [ ],
    "installable": True,
    'application': False,
    'qweb': [],
}
