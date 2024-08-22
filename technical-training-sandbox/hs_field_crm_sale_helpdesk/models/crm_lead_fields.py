from odoo import models, fields, api, exceptions
import logging
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


class crm_lead_stage(models.Model):
	_inherit = 'crm.stage'

	is_loss = fields.Boolean(string="Is Loss Stage", default=False)

class crm_lead_fields(models.Model):
	_inherit = 'crm.lead'
	#CAMPOS FORM SECTOR PUBLICO
	
	#DEFINIR DATOS SELECCIONABLES

	#ORIGEN PARA PÚBLICO
	opciones_origen = [
		('Visita', 'Visita'),
		('Congreso', 'Congreso'),
		('Llamada', 'Llamada'),
		('Referido', 'Referido'),
		('Cotización en Línea', 'Cotización en Línea'),
		('Compra Menor', 'Compra Menor'),
		('Licitación Pública', 'Licitación Pública'),
		('Licitación por Mejor Valor', 'Licitación por Mejor Valor'),
		('Otro', 'Otro')
		]
	
	#ORIGEN PARA PRIVADO
	opciones_origen_privado = [
		('Visita', 'Visita'),
		('Congreso', 'Congreso'),
		('Llamada', 'Llamada'),
		('Referido', 'Referido'),
		('Otro', 'Otro')
		]

	opciones_institucion = [
		('CSS', 'CSS'),
		('MINSA', 'MINSA'),
		('Patronato', 'Patronato'),
		('ONG', 'ONG'),
		('Fundación', 'Fundación'),
		('Cooperativa', 'Cooperativa'),
		('Otro', 'Otro')
		]
	opciones_tipo_clinte=[
		('Sector Público','Sector Público'),
		('Sector Privado','Sector Privado')
	]
	opciones_plan_compra=[
		('Inmediato','Inmediato'),
		('Corto','Corto'),
		('Mediano','Mediano'),
		('Largo Plazo','Largo Plazo')

	]
	opciones_motivo_eleccion=[
		('Tiempo de entrega','Tiempo de entrega'),
		('Performance','Performance'),
		('Precio','Precio'),
		('Calidad','Calidad'),
		('Servicio','Servicio'),
		('Otros','Otros'),


	]
	#opciones_interesado=[
		#('Nueva Instalación','Nueva Instalación'),
		#('Remplazo de equipo','Remplazo de equipo'),
		#('Expansión','Expansión'),
		#('Otros','Otros')

	#]
	opciones_afirmacion=[
		('Si','Si'),
		('No','No')

	]
	#CAMPO HERENCIA DE MONEDA Y COMPA;IA
	company_id = fields.Many2one('res.company', store=True, copy=False,
								string="Company",
								default=lambda self: self.env.user.company_id.id)
	currency_id = fields.Many2one('res.currency', string="Currency",
								 related='company_id.currency_id',
								 default=lambda
								 self: self.env.user.company_id.currency_id.id)
	#CAMPOS BASES
	field_publico_tipo_cliente= fields.Selection(opciones_tipo_clinte, string='Tipo de Cliente')

	#DEFINICION DE CAMPOS
	field_privado_origen= fields.Selection(opciones_origen_privado, string='CPri')#,  compute='onchange_tipo_cliente')
	field_publico_origen= fields.Selection(opciones_origen, string='CPub')#,  compute='onchange_tipo_cliente')
	field_origen_value = fields.Char('Origen', compute='onchange_origen')

	field_marca_value = fields.Char('Marca')
	field_modelo_value = fields.Char('Modelo')

	field_nombre_contacto_value = fields.Char('Nombre del Contacto')

	field_correo_contacto_value = fields.Char('Correo del Contacto')
	field_telefono_contacto_value = fields.Char('Teléfono del Contacto')



	field_publico_institucion = fields.Selection(opciones_institucion, string='Institución')
	#CAMPOS DEPARTAMENTOS
	field_publico_departamento = fields.Char('Departamento')
	field_publico_jefe_departamento = fields.Char('Jefe de departamento')
	field_publico_toma_decision = fields.Char('Toma la desición',help="Nombre? Cargo?")
	field_publico_plan_compra= fields.Selection(opciones_plan_compra, string='¿Para cuándo tiene planificada la compra?')
	#CAMPOS INFORME DE LA PRIMERA VISITA
	field_publico_motivo_eleccion= fields.Selection(opciones_motivo_eleccion, string='Principal motivo de elección')
	field_publico_fecha_primera_visita = fields.Date('Fecha')
	field_publico_interesados= fields.Many2many('crm.interesado', string='Interesado')
	field_publico_presupuesto = fields.Monetary(string="Presupuesto para la compra",help="B/.")
	field_publico_usoprincipal = fields.Text('Uso Principal del Equipo')
	#CAMPOS EQUIPO ACTUAL
	field_publico_marca = fields.Char('Marca')
	field_publico_modelo = fields.Char('Modelo')
	field_publico_satisfecho_equipo = fields.Selection(opciones_afirmacion, string='¿Está satisfecho con el equipo actual?')
	field_publico_motivo = fields.Char('Motivo')
	field_publico_proxima_visita = fields.Date('Próxima visita')
	field_publico_infraestructura = fields.Many2many('crm.infraestructura', string='Evaluación de Infraestructura')
	field_publico_pendientes = fields.Many2many('crm.pendientes', string='Pendientes')

	#field_publico_infraestructura = fields.Many2many('OpcionInfraestructura', string="Infraestructura")
	#CAMPO COMENTARIO..
	field_publico_comentarios = fields.One2many('crm.comentarios', "comentarios_id", string='Comentarios')
	#CAMPO SEGUIMIENTO
	field_seguimientos = fields.One2many('crm.seguimientos',"seguimiento_id", string='Seguimientos')
	field_validation_type = fields.Char('Validar Opt',compute='_compute_vali_opt', store=True)
	# Fecha de solicitud
	request_date = fields.Date(string='Solicitud de la cotización', help="Fecha")
 
	@api.model_create_multi
	def create(self, vals_list):
		print("Se está creando un nuevo registro en mi.modelo")
		new_record = super(crm_lead_fields, self).create(vals_list)
		return new_record

	def write(self, vals):
		print("Se está actualizando un registro en mi.modelo")
		updated_records = super(crm_lead_fields, self).write(vals)
		return updated_records

	@api.depends('type')
	def _compute_vali_opt(self):
		for record in self:
			if record.type =="opportunity": 
				record.field_validation_type="opt"
			
	@api.onchange('field_publico_origen','field_privado_origen','field_publico_tipo_cliente')
	def onchange_origen(self):
		for lead in self:
		#logging.info("TIPO DE CLIENTE:::::" + str(self.field_publico_tipo_cliente))
			if lead.field_publico_tipo_cliente == 'Sector Público':
				lead.field_privado_origen = False
				lead.field_origen_value = lead.field_publico_origen			
			else:
				lead.field_publico_origen = False
				lead.field_origen_value = lead.field_privado_origen

	
	def action_set_lost(self, **additional_values):
		"""Call Super Lost semantic: probability = 0 or active = False """

		record = super(crm_lead_fields, self).action_set_lost
		leads_by_loss_stage = {}
		for lead in self:
			loss_stages = self._stage_find(domain=[('is_loss', '=', True)], limit=None)
			stage_id = next((stage for stage in loss_stages if stage.sequence > lead.stage_id.sequence), None)
			if not stage_id:
				stage_id = next((stage for stage in reversed(loss_stages) if stage.sequence <= lead.stage_id.sequence), loss_stages)
			if stage_id in leads_by_loss_stage:
				leads_by_loss_stage[stage_id] += lead
			else:
				leads_by_loss_stage[stage_id] = lead

		for loss_stage_id, leads in leads_by_loss_stage.items():
			leads.write({'stage_id': loss_stage_id.id, 'probability': 0, 'active':False})

		return record

	#SE USA CLIENTE, COMERCIAL, TELEFONO, CONTACTO,CORREO ELECTRONICO,TELEFONO DE CONTACTO CAMPO ODOO PREDETERMINADO.
 
class crm_infraestructura(models.Model):
	_name = 'crm.infraestructura'
	_description = 'Infraestructura'

	name = fields.Char(string='Nombre', required=True)
	infra_ids = fields.Many2many('crm.lead', string='InfraEstructura' )
	
class crm_pendiente(models.Model):
	_name = 'crm.pendientes'
	_description = 'Pendientes'

	name = fields.Char(string='Nombre', required=True)
	pendiente_ids = fields.Many2many('crm.lead', string='Pendientes' )
 
class crm_interesado(models.Model):
	_name = 'crm.interesado'
	_description = 'Interesado'

	name = fields.Char(string='Nombre', required=True)
	interesado_id = fields.Many2many('crm.lead', string='Interesado' )
 
class crm_comentarios(models.Model):
	_name = 'crm.comentarios'
	_description = 'Comentarios'
	name = fields.Text(string='Comentario', required=True)
	comentarios_id = fields.Many2one('crm.lead', string='Comentarios' )
	create_uid = fields.Many2one('res.users', string='Responsable', readonly=True)
	
	fecha_creacion = fields.Date(string='Fecha de Creación', default=fields.Date.today,readonly=True)

class crm_competidores(models.Model):
	_name = 'crm.competidores'
	_description = 'Competidores'
	name = fields.Char(string='Nombre', required=True)
	competidores_id = fields.Many2one('crm.seguimientos', string='Competidores' )
	precio = fields.Float(string='Precio')
	equipo = fields.Char(string='Equipo', default="Equipo")

class crm_seguimientos(models.Model):
	_name = 'crm.seguimientos'
	_description = 'Seguimientos'
 	
	opciones_estado=[
		('Oportunidad','Oportunidad'),
		('Presupuesto','Presupuesto'),
  		('Ganada','Ganada'),
		('Perdida','Perdida')

	]
 	#CAMPO HERENCIA DE MONEDA Y COMPAÑIA......
	company_id = fields.Many2one('res.company', store=True, copy=False,
								string="Company",
								default=lambda self: self.env.user.company_id.id)
	currency_id = fields.Many2one('res.currency', string="Currency",
								 related='company_id.currency_id',
								 default=lambda
								 self: self.env.user.company_id.currency_id.id)
	fecha_solicitud = fields.Date(string='Fecha de solicitud de cotización', required=True)
	estado_venta = fields.Selection(opciones_estado, string='Estado de la venta',required=True, compute= '_compute_state')
	numero_licitacion = fields.Char(string='Número de licitación')
	motivo = fields.Char(string='Motivo')
	precio_referencia = fields.Monetary(string="Precio de Referencia (B/.)",help="B/.")
	precio_ofertado = fields.Monetary(string="Precio Ofertado (B/.)",required=True,help="B/.")
	seguimiento_id = fields.Many2one('crm.lead', string='Seguimiento' )
	detalles_seguimientos = fields.Text(string='Detalles de seguimiento')
	validar_competidor = fields.Char(string='Validar Competidor', default="0")
	required_field_competidores = fields.Char(string='Por favor, ingrese al menos un Competidor.', readonly=True)
	field_competidores = fields.One2many('crm.competidores',"competidores_id", string='Competidores',required=True)
 
	required_field_precio_ofertado_fn = fields.Char(string='Por favor, ingrese un número mayor a cero para el precio ofertado.', readonly=True)
	validar_precio_ofertado_fn	= fields.Char(string='Validar Precio Ofertado', default="0")
 
	required_field_precio_referencia_fn = fields.Char(string='Por favor, ingrese un número mayor a cero para el precio de referencia.', readonly=True)
	validar_precio_referencia_fn	= fields.Char(string='Validar Precio Referencia', default="0")
 
 	#PRUEBAS
	@api.depends("seguimiento_id")
	def _compute_state(self):
		mid = str(self.seguimiento_id.id).split("_")
		logging.info("CRM LEAD ID:::::" + str(mid[1]))
		my_lead=self.env['crm.lead'].search([('id','=',int(mid[1]))], limit=1)
		for record in self:
			if my_lead.stage_id.name == "Won":
				record.estado_venta = 'Ganada'
			elif my_lead.stage_id.name in ["New","Qualified",'Proposition', 'En Evaluación']:
				record.estado_venta = 'Oportunidad'
			elif my_lead.stage_id.name == 'Perdido' or my_lead.active == False:
				record.estado_venta = 'Perdida'
			else:
				record.estado_venta = 'Presupuesto'

	@api.onchange('field_competidores')
	def _onchange_check_competidores(self):
		if not self.field_competidores:
			self.validar_competidor = "0"
		else:
			self.validar_competidor = "1"
   
	@api.onchange('precio_ofertado')
	def _onchange_check_precio_ofertado(self):
		if self.precio_ofertado==False:
			self.validar_precio_ofertado_fn = "0"
		else:
			self.validar_precio_ofertado_fn = "1"
   
	@api.onchange('precio_referencia')
	def _onchange_check_precio_referencia(self):
		if self.precio_referencia==False:
			self.validar_precio_referencia_fn = "0"
		else:
			self.validar_precio_referencia_fn = "1"
	
#class OpcionInfraestructura(models.Model):
	#_name = 'OpcionInfraestructura'
	#infraestructura = fields.Char(string="Infraestructura")
# Crear registros predefinidos en el modelo "MiOpcion"
#OpcionInfraestructura.create([
   # {'infraestructura': 'Espacio'},
   #{'infraestructura': 'Aire acondicionado'},
   # {'infraestructura': 'Alimentación electríca'},
   # {'infraestructura': 'Blindaje'},
   # {'infraestructura': 'Otros'},
#])   .....

