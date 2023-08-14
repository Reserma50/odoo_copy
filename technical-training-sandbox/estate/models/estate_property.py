from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


selection_state=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')]
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char('Title',required=True, copy=False)
    description = fields.Text()
    postcode = fields.Char()
    # date_availability = fields.Date(copy=False, default=lambda self: fields.Datetime.today()) #the default availability date is in 3 months
    date_availability = fields.Date('Available From',copy=False, default=lambda self:fields.Datetime.today() + relativedelta(months=3))
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False,) #by default is 0.00
    bedrooms = fields.Integer(default = 2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer('Garden Area (sqm)')
    
    garden_orientation = fields.Selection(string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
    )    
    active = fields.Boolean('Active', default=False)
    state = fields.Selection(
        selection_state,
        default='new',
        required=True,
        
    )   
    # buller_id = fields.Many2one("res.Buller", string="Buller")
    property_type_id = fields.Many2one("estate.property.type", string='Modelo Principal')

    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    seller_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    # An offer applies to one property, but the same property can have many offers.
    offer_ids = fields.One2many("estate.property.offer","property_id", string="Offers")

    # Add the total_area field to estate.property
    total_area = fields.Integer(compute="_compute_total") 

    # Add the best_price field to estate.property
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")

    _sql_constraints = [
        ('state_property_unique_name', 'UNIQUE(name)','The name of porperty must be unique.'),
        ('state_property_check_expected_price', 'CHECK(expected_price > 0)','The EXPECTED PRICE of distribution should be POSITIVE.'),
        ('state_property_check_selling_price', 'CHECK(selling_price > 0)','The selling_price of distribution must be POSITIVE.'),
    ]

    # SQL constraints are an efficient way of ensuring data consistency. However it may be necessary to make more complex checks 
    # which require Python code. In this case we need a Python constraint.


    @api.constrains('selling_price')
    def _check_selling_price(self):
        ''' it will not be possible to accept an offer lower than 90% of the expected price.'''
        for record in self:
            print(record.selling_price)
            if record.selling_price < (record.expected_price * 0.90):
                raise ValidationError("It is not  possible to accept an offer lower than 90% of the expected price.")
    #all records passed the test, don't return anything

    # it might be useful to still be able to set a value directly. In our real estate example, we can define a validity 
    # duration for an offer and set a validity date. We would like to be able to set either the duration or the date with 
    # one impacting the other.


    # def calculate_start_of_3_months(self):
    #     today = fields.Datetime.today()
    #     future_date = today + relativedelta(months=3)
    #     self.date_availability(default = self.env['ir.fields'].start_of('month', future_date))


    # In many cases, both computed fields and onchanges may be used to achieve the same result. 
    # Always prefer computed fields since they are also triggered outside of the context of a form view. 
    # Never ever use an onchange to add business logic to your model.
    # This is a very bad idea since onchanges are not automatically triggered when creating a 
    # record programmatically; they are only triggered in the form view.

    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        mayor = 0
        for record in self:
            for l in record.offer_ids:
                if l.price > mayor:
                    mayor = l.price
        #assing
        record.best_price = mayor

    def action_set_cancel(self):
        '''isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface'''
        for record in self:
            if not record.state == 'sold':

                record.state = 'canceled'
            else:
                raise exceptions.UserError('Cancelled properties cannot be sold.')
        # isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface
        return True
    
    def action_set_sold(self):
        '''isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface'''
        for record in self:
            if not record.state == 'canceled':
                record.state = 'sold'
            else:
                raise exceptions.UserError('Sold properties cannot be canceled.')
        # isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface
        return 
    
    # @api.model
    # def get_estate_property_by_id(self, estate_property_id):
    #     return self.search([('id', '=', estate_property_id)], limit=1)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = "north"
            # print("TRUE")
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    # def action_do_something(self):
    #     print("TEST DE BUTTON LINKED TO FUNCTION")
    #     return True


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "sequence, name"

    name = fields.Char('Title',required=True)
    sequence = fields.Integer('Sequencia', default=1, help="Used to order types. Lower is better.")
    property_ids = fields.One2many("estate.property",'estate_property_type_id', string='Modelo Secundario')

    _sql_constraints = [
        ('state_property_type_unique_name', 'UNIQUE(name)','The name of porperty type must be unique.'),
    ]


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"

    name = fields.Char('Title',required=True)
    color = fields.Integer('Color')

    _sql_constraints = [
        ('state_property_tag_unique_name', 'UNIQUE(name)','The name of porperty tag must be unique.'),
    ]

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy = False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    
    # Add the following fields to the estate.property.offer model:

    # In some cases, it might be useful to still be able to set a value directly. In our real estate example, 
    # we can define a validity duration for an offer and set a validity date. We would like to be able to set 
    # either the duration or the date with one impacting the other.

    validity = fields.Integer(default = 7)
    date_deadline = fields.Date("Deadline", compute="_compute_dead_line", inverse="_inverse_dead_line")

    _sql_constraints = [
        ('state_porperty_offer_check_price', 'CHECK(price > 0)','The price of distribution must be POSITIVE.'),  
    ]

    @api.depends("validity", "create_date")
    def _compute_dead_line(self):
        #date_deadline de tipo Date. Sin embargo, ten en cuenta que al sumar días a un objeto datetime.datetime para 
        # obtener una fecha, el resultado seguirá siendo un objeto datetime.datetime. Para asignarlo a un campo de tipo Date, 
        # deberás extraer la parte de la fecha utilizando el método date().

        for record in self:  #revisar que durante la creación el sistema no reviente
            # print(f"SHOW THE {record.create_date}")
            # exceptions.ValidationError(f"SHOW THE RESULT!  {self.create_date}")
            if record.create_date: 
                dead_line = record.create_date + relativedelta(days=record.validity)
            # De esta manera, el campo date_deadline se establecerá con la fecha correspondiente, sin incluir la información de tiempo.
            # record.date_deadline = dead_line.date()
            # else:
            #     dead_line = relativedelta(days=record.validity)
            #     # De esta manera, el campo date_deadline se establecerá con la fecha correspondiente, sin incluir la información de tiempo.
            #     record.date_deadline = dead_line.date()

    def _inverse_dead_line(self):
        for record in self:
            if record.date_deadline:
                #En este caso, se está llamando al método date() en record.create_date para obtener el objeto datetime.date 
                #correspondiente a la fecha. Luego, se puede realizar la resta y obtener la diferencia de días utilizando el atributo days.
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                dead_line = record.create_date + relativedelta(days=record.validity)
                record.date_deadline = dead_line.date()

    def action_set_accept(self):
        '''isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface'''
        # values = super(EstateProperty, self).alias_get_creation_values()
        # values['selling_price'] = self.env['ir.model']._get('estate_property_offer').id
        for record in self:
            if float_is_zero(record.property_id.selling_price, 2):
                record.status = 'accepted'
                print(f'actual selling price {record.property_id.selling_price} , to change {record.price}')
                record.property_id.selling_price = record.price
                record.property_id.buyer_id = record.partner_id
            else:
                raise exceptions.UserError('Pay attention: in real life only one offer can be accepted for a given property!.')

        # isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface
        return True
    
    def action_set_refuse(self):
        '''isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface'''
        for record in self:
            record.status = 'refused'
            if record.property_id.buyer_id == record.partner_id:
                record.property_id.buyer_id = None
        # isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface
        return True
    
