// Impresion de factura fiscal desde lista de ordenes

odoo.define("printax_pos.order_print_fisc", function(require) 
{
	"use strict";

	var bPar = false;

	var Widget = require('web.Widget');
	var rpc = require("web.rpc");

	Widget.include(
	{
		events: 
		{
			'click #print_fact_button': '_print_fac_fis',
		},

		_print_fac_fis: function(param)
		{
			// esta rutina es porque el evento es llamado 2 veces
			
			if(bPar == true)
			{
				bPar = false;
				return;
			}
			bPar = true;
			
			// console.log(this);
			// console.log('this.state.data.id=' + this.state.data.id);

			var IdOrder = this.state.data.name;

			rpc.query(
			{
				model: "pos.order",
				method: "printax_print_invoice",
//				args: [ 0, this.state.data.id ]
				args: [ 0, 2, IdOrder ]
			}).then(function(resp) 
				{
					// console.log('order_print_fisc.js - _print_fac_fis - in function');
					
					var bReimpresio = false;
					
					if(resp.tip == "ERR")
					{
						// console.log('order_print_fisc.js - _print_fac_fis - resp.tip == "ERR"');
						
						alert(resp.err);
						return;
					}
					
					var NameOrder;
					
					if(resp.tip == "COK")
						NameOrder = resp.ord;
					else
						bReimpresio = true;
						
					var comando = "http://"
					comando += resp.ip
					comando += ":"
					comando += resp.port
					comando += "/sendcmd/"
					comando += resp.msg

					// console.log('order_print_fisc.js - _print_fac_fis comando: ' + comando);

					var xhr = new XMLHttpRequest;
					xhr.open("GET", comando, true);
					xhr.send(null);
					
					// console.log('order_print_fisc.js - _print_fac_fis send');

					xhr.onload = function() 
					{
						// console.log('_print_fac_fis - in onload');
						if(xhr.status != 200) 
						{ 
							console.log("Error ${xhr.status}: ${xhr.statusText}");
						} 
						else 
						{ 
							var resp = JSON.parse(xhr.responseText)
							
							if(resp.TIP == "COK")
							{
								if(bReimpresio == false)
								{
									rpc.query(
									{
										model: "pos.order",
										method: "update_invoice",
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
							}
							else
							{
								alert(resp.err);
							}
						}
					};	

					xhr.onprogress = function(event) 
					{
						// console.log('_print_fac_fis - in onprogress');
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
				});
		}
	});
	
	return Widget;
});
