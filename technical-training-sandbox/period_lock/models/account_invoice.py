# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

MYCLASS = 'period.lock'
MYPERMISO = 'period_lock.group_period_lock'
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super(AccountPayment,self).action_post()
        lock_period = self.env[MYCLASS].search([('state','=','lock')])
        another = self.env['account.move']
        for rec in self:
            if not self.env.user.has_group(MYPERMISO):
                for lp in lock_period:
                    another.validar_periodos(objeto_move = rec, objeto_bloqueo = lp)

        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove,self).action_post()
        lock_period = self.env[MYCLASS].search([('state','=','lock')])

        if not self.env.user.has_group(MYPERMISO):
            for lp in lock_period:
                self.validar_periodos(objeto_bloqueo=lp)
        return res


    @api.model
    def create(self, vals):
        lock_period = self.env[MYCLASS].search([('state','=','lock')])
        res = super(AccountMove,self).create(vals)

        for record in self:
            logging.info('Record ID: %s', record.id)
            for field_name in record._fields:
                value = getattr(record, field_name, None)
                logging.info('Field: %s, Value: %s', field_name, value)

        if not self.env.user.has_group(MYPERMISO):
            for lp in lock_period:
                self.validar_periodos(objeto_move = res, objeto_bloqueo = lp)
        return res
    
    def validar_periodos(self, objeto_move=None, objeto_bloqueo=None):
        '''Raise Error is Date is in Periodos'''
        if objeto_move is None:
            objeto_move = self

        if objeto_move.invoice_date: #Facturas
            logging.info("Invoice Date :::::::::::" + str(objeto_move.invoice_date))
            self.verification(objeto_bloqueo, objeto_move.invoice_date, objeto_move.journal_id)

        elif objeto_move.date and objeto_move.invoice_date == False: #Asientos
            logging.info("Raise Error :::::::::::" + str("Invoice Date False"))
            self.verification(objeto_bloqueo, objeto_move.date, objeto_move.journal_id)

        else: #Pagos
            logging.info("Fechas en pagos vacios :::::::::::")

    def verification(self, objeto_bloqueo, fecha, journal):
        if objeto_bloqueo.from_date <= fecha and objeto_bloqueo.to_date >= fecha:
            logging.info("Date:::::::::::" + str(fecha))
            if journal in objeto_bloqueo.journal_ids:
                msg="Accounting period locked from "+str(objeto_bloqueo.from_date)+ " to "+ str(objeto_bloqueo.to_date)+" Dates for this journal: "+str(journal.name)+"..!"  
                raise ValidationError(_(msg))

    #@api.model
    def button_draft(self):
        
        for record in self:
            logging.info('Record ID: %s', record.id)
            for field_name in record._fields:
                value = getattr(record, field_name, None)
                logging.info('Field: %s, Value: %s', field_name, value)
                # print('Field: %s, Value: %s', field_name, value)
        
        lock_period = self.env[MYCLASS].search([('state','=','lock')])
        if not self.env.user.has_group(MYPERMISO):
            for lp in lock_period:
                self.validar_periodos(objeto_move = None, objeto_bloqueo = lp)
                        
        res = super(AccountMove,self).button_draft() 
        return res