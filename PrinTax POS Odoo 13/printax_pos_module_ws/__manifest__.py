# coding: utf-8
###########################################################################
{
    "name": "PrinTax para POS (WorkStation)",

    "summary": """
        Módulo para la emisión de facturas fiscales a través del programa PrinTax desde el POS.
    """,

    "description": """
        Este módulo utiliza el programa PrinTax para emitir facturas en impresores fiscales desde
        el módulo de punto de venta (POS). Estos impresores están adaptados a la legislación de 
        varios paises específicos, en esta versión Venezuela y Panamá.
        
        Esta versión envia el comando al PrinTax desde la estación de trabajo, está homologada con 
        los módulos fiscales desarrollados por:
        
        Desarrollos PNP, C.A. para impresores Epson.
        TheFactory HKA para impresores Bixolon.
    """,

    "author": "LascaData, C.A.",
    "website": "http://www.lascadata.com",
    "version": "13.1.0.0",
    "category": "Sales/Point Of Sale",
    "colaborator": "Hernán Navarro",
    "depends": ["point_of_sale"],
    "demo": [ ],
    "data": [ 
        "views/pos_config.xml", 
        "views/point_of_sale.xml", 
        "views/pos_order_list.xml"
    ],
    "test": [ ],
    "qweb": [ ],
    "installable": True,
    "application": False,
}
