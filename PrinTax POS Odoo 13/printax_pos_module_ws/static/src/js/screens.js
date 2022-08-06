// Modulo que sobreescribe el método "print" del punto de venta que hace la impresión
// de la factura, este módulo llama al procedimiento "print_invoice" definido en pos_order.py
// Version 1.0.0 - 2020.09.11 - Hernán Navarro

odoo.define('printax_pos.receip', function (require) 
{
	"use strict";
	
	var rpc = require('web.rpc');
	var screens = require('point_of_sale.screens');

	screens.ReceiptScreenWidget.include(
	{
		print: function() 
		{
			var IdOrder = this.pos.get_order().uid;
			rpc.query(
			{
				model: 'pos.order',
				method: 'print_invoice',
				args: [ 0, 1, IdOrder ]
			}).then(function(resp) 
				{
					if(resp.tip == "COK")
					{
						var NameOrder = resp.ord;
						
 						var comando = 'http://'
						comando += resp.ip
						comando += ':'
						comando += resp.port
						comando += '/sendcmd/'
						comando += resp.msg

						var xhr = new XMLHttpRequest;
						xhr.open("GET", comando, true);
						xhr.send(null);
						
						xhr.onload = function() 
						{
							if(xhr.status != 200) 
							{ 
								console.log('Error ${xhr.status}: ${xhr.statusText}');
							} 
							else 
							{ 
								var resp = JSON.parse(xhr.responseText)
								
								if(resp.TIP == "COK")
								{
									rpc.query(
									{
										model: 'pos.order',
										method: 'update_invoice',
										args: [ 0, 
												NameOrder,
												resp.FAC,
												resp.SER,
												resp.FEC,
												resp.VTA,
												resp.IVA,
												resp.RPZ ]
									}).then(function(resp){});
								}
								else
								{
									alert(resp.ERR);
								}
							}
						};	

						xhr.onprogress = function(event) 
						{
/*							
							if(event.lengthComputable) 
							{
								console.log(`Received ${event.loaded} of ${event.total} bytes`);
							} 
							else 
							{
								console.log(`Received ${event.loaded} bytes`); // no Content-Length
							}
							
							console.log(xhr.responseText);
*/
						};

						xhr.onerror = function() 
						{
							console.log("Request failed");
						};
					}
					else
					{
						alert(resp.err);
					}
				});
		},
	});
});

