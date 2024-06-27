# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


# class period_lock(models.Model):
#     _name = 'period_lock.period_lock'
#     _description = 'period_lock.period_lock'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class PeriodLock(models.Model):
    _name = 'period.lock'
    _description = 'Perido Lock'

    name = fields.Char()
    company_id = fields.Many2one('res.company', default = lambda self: self.env.user.company_id, required = True)
    user_id = fields.Many2one('res.users', default = lambda self: self.env.user, required = True)
    company_ids = fields.Many2many('res.company', 'company_period_lock_rel', 'period_id', 'company_id', required = True)
    journal_ids = fields.Many2many('account.journal', 'journal_period_lock_rel', 'period_id', 'journal_id', required = True)
    from_date = fields.Date(required = True)
    to_date = fields.Date(required = True)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked'), ('unlock', 'Unlocked')], default = 'draft')    

    @api.onchange('from_date', 'to_date')
    def check_valid_date(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError(_("Please enter valid 'To date' or 'From Date' must be less than and 'To Date' must be Greater..! "))
            
    @api.constrains('journal_ids')
    def _check_unique_journal(self):
        if self.journal_ids:
            if self.search(['&', ('id', '!=', self.id), ('journal_ids','in', self.journal_ids.ids), '&', ('from_date', '<=', self.from_date), ('to_date','>=',self.from_date)]):
                raise ValidationError("Account period lock journal already exist, must be unique journal..!!!")
    
    def period_set_lock(self):
        self.write({'state':'lock'})

    def period_set_unlock(self):
        self.write({'state':'unlock'})

    def period_set_draft(self):
        self.write({'state':'draft'})