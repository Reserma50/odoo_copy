# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions, tools
import base64


class InOutInventory(models.Model):
    _inherit = ['stock.picking','mail.thread', 'mail.activity.mixin']
    _name = 'stock.picking'

    myname = fields.Char()
    
    department_stock_field = fields.Selection([
        ('ST', 'Servicio Técnico'),
        ('CO', 'Comercial'),
        ('IT', 'IT'),
        ], 'Departamento', default='CO', help='Escoja el departamento del colaborador', copy=True)
    
    calidad_stock_field = fields.Selection([
        ('INS', 'Instalación'),
        ('GAR', 'Garantía'),
        ('REP', 'Reparación'),
        ('DON', 'Donación'),
        ('PRE', 'Préstamo'),
        ('FAC', 'Factura'),
        ], 'En Calidad', default='REP', help='En que serán utilizados?', copy=True)
    orden_cotiz_stock_field = fields.Char(string = "No. Orden de Compra Cotización")
    proyecto_stock_field = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto', ondelete='restrict',
    ) 


    invoice_stock_field = fields.Char(string = "No. De Factura")
    #Files
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    #Firma
    signature = fields.Image('Signature', help='Signature', copy=False, attachment=True)
    is_signed = fields.Boolean('Is Signed', compute="_compute_is_signed")
    is_locked = fields.Boolean(default=True, help='When the changes is not done this allows changing the '
                               'initial fields. When the changes is done this allows '
                               'changing the done fields.')
    partner_id_supervisor = fields.Many2one(
        comodel_name='res.partner',
        string='Supervisor', ondelete='restrict',
        # domain="['|', ('parent_id','=', False), ('is_company','=',True)]",
        # check_company=True
        )

    partner_id_employee = fields.Many2one(
        comodel_name='res.partner',
        string='Employee', ondelete='restrict',
        # domain="['|', ('parent_id','=', False), ('is_company','=',False)]",
        # check_company=True
        )
    partner_invoice_id =  fields.Many2one(
        comodel_name='res.partner',
        string='Employee', ondelete='restrict',
        # domain="['|', ('parent_id','=', False), ('is_company','=',False)]",
        # check_company=True
        )

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
    
    @api.depends('signature')
    def _compute_is_signed(self):
        for traslado in self:
            traslado.is_signed = traslado.signature

    # def write(self, vals):
    #     # print("My vals", vals)
    #     res = super(InOutInventory, self).write(vals)
    #     if vals.get('signature'):
    #         for traslado in self:
    #             print("HERE IS!")
    #             print(traslado)
    #             traslado._attach_sign()
    #             # vehicle._create_activity_notification(True)
    #     return res

    def _attach_sign(self):
        """ Render the changes report in pdf and attach it to the picking in `self`. """
        if self.picking_type_code == "internal":
        # print(self.picking_type_code)
            self.ensure_one()
            partner_name = self.partner_id_employee
            # report = self.env['ir.actions.report']._render_qweb_pdf("stock.action_report_delivery", self.id) #modificando el reporte
            report = self.env['ir.actions.report']._render_qweb_pdf("stock.report_picking", self.id) #modificando el reporte
            
            filename = "%s_constancia_de_traslados" % partner_name.name
            if partner_name:
                message = _('Solicitud/Devolución de Artículos firmada por %s') % (partner_name.name)
            else:
                raise exceptions.UserError(('Porfavor seleccionar al usuario que hizó la solicitud.'))       
            data = [('%s.pdf' % filename, report[0])]
            self.message_post(
                attachments=data,
                body=message,
            )
            
            res = self.send_service_mail_notification(True, data)
        else:
            res = super(InOutInventory, self)._attach_sign()
            #enviar mediante correo
        
        return res
    
    def send_service_mail_notification(self, created, data):
        partner_name = self.partner_id_employee
        print(partner_name.email)
        print(partner_name)
        # my_code=self.id
        email_to_user = []

        if created:
            subject = _("Solicitud/Devolución de Artículos: %s" % partner_name.name)
            body = _("Una nueva asignación fue registrada para el Usuario %s, por lo tanto adjuntamos documento." % (partner_name.name))
        # if my_code.notificar_a:
        #     email_to_user.append(my_code.notificar_a)
        if partner_name:
            email_to_user.append(partner_name.email)   
        else: 
            raise exceptions.UserError(('Porfavor seleccionar al usuario que hizó la solicitud.'))        
        # if my_code.manager_id:
        #     email_to_user.append(my_code.manager_id.email)           
        
        for attachment in data:
            file_name, file_content = attachment 
            file_content_base64 = base64.b64encode(file_content)
        mail_values = {
            'subject': subject,
            'body_html': body,
            'email_to': ",".join(email_to_user), #replace with the actual mail,
            'attachment_ids': [(0, 0, {
            'name': file_name,
            'type': 'binary',
            'datas': file_content_base64,
            # 'datas_fname': file_name,
            'res_model': 'mail.mail_activity_data_todo',
            })]}

        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        
        return True

class FieldsInventoryTemplate(models.Model):
    _inherit = 'product.template'

    inventory_fields_ubicacion = fields.Char('Ubicación en Bodega')
    inventory_fields_marca = fields.Char('Marca')
    inventory_fields_descripcion = fields.Char('Descripción')
    inventory_fields_damage = fields.Char('Daño')
    inventory_fields_estado = fields.Boolean('Estado', default=False)

    categ_id = fields.Many2one(
        'product.category', 'Product Category', default=None)
    
    @api.depends('detailed_type')
    def _compute_category_type(self):
        for test in self:
            if test.detailed_type:
                test.categ_id = test.detailed_type
            else:
                test.categ_id = False

class InheritedProductCategory(models.Model):
    _inherit = 'product.category'

    detailed_type_ids = fields.Many2many("category.tag", string="Categories")

    detailed_type_prod = fields.Selection([
        ('product', 'Storable Product'),
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Tipo de Producto Vinculado', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    
class CategoryTag(models.Model):
    _name = "category.tag"
    _description = "Category Tag"
    _order = "name"

    name = fields.Char('Categoria',required=True)
    color = fields.Integer('Color')
    

    _sql_constraints = [
        ('category_tag_unique_name', 'UNIQUE(name)','The name of category tag must be unique.'),
    ]

