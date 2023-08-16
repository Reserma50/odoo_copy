from odoo import models, fields, api, exceptions, _, Command

class InheritModel(models.Model):
    _inherit = ["estate.property"]
    def action_set_sold(self):
        # res = super(InheritModel, self).action_set_sold()
        # self.mapped()
        # print("La vendí")
        # print("Verificando:", self.env['estate.property'].check_access_rights('create', False))
        # print("DESPUES DE:", self.env['estate.property'].check_access_rights('write'))
        # if not self.env['estate.property'].check_access_rights('create', False):
        #     print("INSIDE!")
        print("Verificar permisos!")
        print("Llama al método _preparar_invoices")
        # Prepare the dict of values to create the new invoice for a sales order. This method may be
        # overridden to implement custom invoice generation (making sure to call super() to establish
        # a clean extension chain).

            #dentro del metodo antes mcnionado se usa el contextp para ver el tipo, además 
            #Basado en el contexto    se llama a la función "_get_default_journal()"
            # en caso de no estar definido se genera un nuevo error. De lo contrario se obtiene el diario asociado
            # en el raro supuesto de que todo salga correctamente define un diccionario que define todos estos cambios!
        print("Invoice line values (keep only necessary sections).")

        #To work with this "create invoices"
        # move_type = fields.Selection(selection=[
        #     ('entry', 'Journal Entry'),
        #     ('out_invoice', 'Customer Invoice'),
        #     ('out_refund', 'Customer Credit Note'),
        #     ('in_invoice', 'Vendor Bill'),
        #     ('in_refund', 'Vendor Credit Note'),
        #     ('out_receipt', 'Sales Receipt'),
        #     ('in_receipt', 'Purchase Receipt'),
        # ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        # default="entry", change_default=True)

        # new_module con el campo
        # comprador = fields.Many2one("res.partner", string="Comprador", copy=False)
        
        # Pasando el self, como obtengo el company_id usando el campo comprador?


        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.


        
        invoice_vals = self.preparar_invoices_facturas()
        # print("accediendo", self.buyer_id.company_id)

        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)
        print("MY MOVES", moves)
        return super(InheritModel, self).action_set_sold()
    
    def preparar_invoices_facturas(self):
        '''
        Prepare dictionary of vaalues to create a new invoices.

        '''
        self.ensure_one()
        journal = sales_journal = None

        try:
            journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        except AttributeError:
            print("EL ERROR")
        else:
            journal = self.env['account.move'].with_context(default_move_type='out_invoice')

            # self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('type', '=', 'general')], limit=1)
            # self.env['res.partner'].search([()])
        
        print("accediendo", self.buyer_id.id)
        for record in self:
            print("accediendo", record.buyer_id.id)
            company_id = self.env['res.company'].search([('partner_id', '=', record.buyer_id.id)], limit=1)
            print("EL COMPANY ID", company_id)
            company_name = company_id.name if company_id else "No asignado"
            # sales_journal=self.env['account.journal'].search([('company_id', '=', company_id.id), ('type', '=', 'general')], limit=1)
            
        #journal_name = "Diario de Ventas"  # Ajusta el nombre del diario si es diferente
        journal_name = "Customer Invoices"
        sales_journal = self.env['account.journal'].search([('name', '=', journal_name)], limit=1)
        print(f"Journal Found {sales_journal.alias_name} De la copmañia {company_name}")
        # Buscar el diario de ventas por su nombre
        # journal_name = "Diario de Ventas"  # Ajusta el nombre del diario si es diferente
        # sales_journal = self.env['account.journal'].search([('name', '=', journal_name)], limit=1)
        print(sales_journal)
        #search user company id to filter the journal

        # Customer Invoices = factiras a clientes
        # Vendor bills = facturas de proveedores 

        tax_id = self.env['account.tax'].search([('name', '=', "6%")], limit=1)


        if sales_journal is None:
            raise exceptions.UserError(('Please define an accounting sales journal for the company %s (%s).'))

        #invoices lines
        a = [
                Command.create({
                    "name": self.name,
                    "quantity": "1",
                    "price_unit" : self.selling_price,
                    "tax_ids":[tax_id.id],
                    # "price_subtotal":self.selling_price*(tax_id.amount/100)
                }),
                Command.create({
                    "name": "Costos administrativos",
                    "quantity": "1",
                    "price_unit" : 100,
                    "tax_ids":None
                })
            ]

        invoice_vals = {
            'invoice_date':fields.Date.today(),
            'invoice_line_ids':a,
            'move_type': 'out_invoice',
            'partner_id': self.buyer_id.id,
            'journal_id': sales_journal.id,  # company comes from the journal
        }
        return invoice_vals