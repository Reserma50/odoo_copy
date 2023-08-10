from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)

class CrmLeadComentarios(models.Model):
    _name = "crm.lead.comentario"
    _description = "Comentarios del proyecto "

    fecha = fields.Date(string="Fecha", default=lambda self:fields.Datetime.today())
    responsable_id = fields.Many2one("res.users", string="responsable", default=lambda self: self.env.user)
    descripcion = fields.Text(string="Descripción")
    lead_id = fields.Many2one("crm.lead", required=True)


class CrmLeadCompetidores(models.Model):
    _name = "crm.lead.competidor"
    _description = "Competidores de Seguimientos"

    field_pub_empresa = fields.Char(string="Empresa")
    field_pub_precio = fields.Float(string="Precio")
    field_pub_equipo = fields.Char(string="Equipo")
    seguimiento_id = fields.Many2one("crm.lead.seguimiento", required=True) #dar seguimiento suando env

class CrmLeadSeguimientos(models.Model):
    _name = "crm.lead.seguimiento"
    _description = "Seguimientos de Proyectos"

    opciones_estado = [
        ('Oportunidad', 'Oportunidad'),
        ('Presupuesto', 'Presupuesto'),
        ('Ganada', 'Ganada'),
        ('Perdida', 'Perdida'),
    ]

    field_pub_seguimiento = fields.Integer(string="seguimiento")
    field_pub_fecha = fields.Date(string="Fecha de solicitud de cotización")
    field_pub_detalles = fields.Text(string="Detalles del seguimiento")
    field_pub_estado = fields.Selection(opciones_estado, string="Estado de la venta")
    field_pub_numero_licitacion = fields.Integer(string="Número de licitación")
    field_pub_motivo_de_estado = fields.Char(string = "Motivo")
    field_pub_precio_ref = fields.Float(string = "Precio de Referencia")
    field_pub_precio_oferta = fields.Float(string = "Precio Ofertado")
    competidores_ids = fields.One2many("crm.lead.competidor", "seguimiento_id", string="Competidores")
    lead_id = fields.Many2one("crm.lead", required=True)

    # @api.onchange("field_pub_estado")
    # def _onchange_field_pub_estado(self):
    #     if (self.field_pub_estado == "Ganada" or self.field_pub_estado == "Perdida"):
    #         self.field_pub_motivo_de_estado.required = True
    #     else:
    #         self.field_pub_motivo_de_estado.required = False

    # @api.model
    # def _get_context_field_publico_origen_from_context(self):
    #     return self._context.get('default_field_publico_origen', 'False')
    #     #
    # context_field_publico_origen = fields.Char(string='Primer Select', compute='_compute_context_primer_select', default=_get_context_field_publico_origen_from_context)

    # @api.depends('context_field_publico_origen')
    # def _compute_context_primer_select(self):
    #     pass

class crm_lead_fields(models.Model):
    _inherit = 'crm.lead'
    #campos form sector publico
    opciones_origen = [
        ('visita', 'Visita'),
        ('congreso', 'congreso'),
        ('Llamada', 'Llamada'),
        ('Referido', 'Referido'),
        ('Cotizacion en linea', 'Cotización en línea'),
        ('Compra Menor', 'Compra Menor'),
        ('Licitacion Publica', 'Licitación Pública'),
        ('Licitacion por Mejor Valor', 'Licitación por Mejor Valor'),
        ('Otro', 'Otro')
    ] 
    # Las opciones DEBEN SER VALORES CON TILDES O SIMBOLOS RAROS?
    field_publico_origen = fields.Selection(opciones_origen, string='Origen')
    origen = fields.Char(string='MyOrigen', compute='_compute_origen')
    opciones_institucion = [
        ('CSS', 'CSS'),
        ('MINSA', 'MINSA'),
        ('Patronato', 'Patronato'),
        ('ONG', 'ONG'),
        ('Fundacion', 'Fundación'),
        ('Otro', 'Otro'),
    ]
    opciones_planificada = [
        ('inmediato', 'Inmediato'),
        ('corto', 'Corto'),
        ('mediano', 'Mediano'),
        ('largo_plazo', 'Largo Plazo'),
    ]
    opciones_motivo = [
        ("Tiempo de entrega","Tiempo de entrega"),
        ("Rendimiento","Rendimiento"),
        ("Precio","Precio"),
        ("Calidad","Calidad"),
        ("Servicio","Servicio"),
        ("Otros","Otros"),
    ]
    opciones_afirmacion = [
        ('Si', 'Si'),
        ('No','No')
    ]
    field_publico_institucion = fields.Selection(opciones_institucion, string="Institución")
    field_publico_equipo_proyecto = fields.Char(string="Equipo o Proyecto")
    field_publico_departamento = fields.Char(string="Departamento")
    field_publico_jefe_departamento = fields.Char(string="Jefe de Departamento")
    field_publico_contacto = fields.Char(string="Contacto")
    field_publico_tel_contacto = fields.Char(string="Teléfono de contacto")
    field_publico_decition = fields.Char(string="Toma la desición")
    field_publico_planificada = fields.Selection(opciones_planificada,string="¿Para cuándo tiene planifcada la compra?")
    #CAMPOS INFORME DE LA PRIMERA VISITA
    field_publico_fecha = fields.Date(string="Fecha",default=lambda self:fields.Datetime.today())
    field_publico_motivo = fields.Selection(opciones_motivo, string="Principal motivo de Elección")
    field_publico_interesado_ids = fields.Many2many('crm.lead.interesado', string="Interesado en")
    field_publico_presupuesto = fields.Float(string="Presupuesto de la compra")
    #CAMPOS DE EQUIPO
    field_publico_marca = fields.Char(string="Marca")
    field_publico_modelo = fields.Char(string="Modelo")
    field_publico_afirmacion = fields.Selection(opciones_afirmacion, string="¿Está satisfecho con el equipo actual?")
    field_publico_respuesta = fields.Char(string="Motivo")
    field_publico_infraestructura_ids = fields.Many2many('crm.lead.infraestructura', string="Infraestrutura:")
    field_publico_pendiente_ids = fields.Many2many('crm.lead.pendiente', string="Pendiente:")
    # PROXIMA VISITA
    field_publico_proxima_visita = fields.Date(string="Próxima Visita")
    # COMENTARIOS
    comentarios_ids = fields.One2many("crm.lead.comentario","lead_id", string="Comentarios") #Hermec use Many2One
    # SEGUIMIENTOS
    seguimientos_ids = fields.One2many("crm.lead.seguimiento", "lead_id", string="Seguimientos") #Hermec use Many2One #Luego ManyToMany

class CrmLeadInteresado(models.Model):
    _name = "crm.lead.interesado"
    _description = "Intereses en lo proyectos Público y Privado"
    
    name = fields.Char('Title', required=True)

    # name = 

class CrmLeadInfraestructura(models.Model):
    _name = "crm.lead.infraestructura"
    _description = "Infraestructura en los proyectos Publico y Privado"
    
    name = fields.Char('Title', required=True)

class CrmLeadPendiente(models.Model):
    _name = "crm.lead.pendiente"
    _description = "Pendientes en los proyectos Publico y Privado"
    
    name = fields.Char('Title', required=True)



