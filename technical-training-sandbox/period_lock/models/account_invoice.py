# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super(AccountPayment,self).action_post()
        
        lock_period = self.env['period.lock'].search([('state','=','lock')])        
        logging.info('********** \nField: %s', self)
        logging.info("Raise Error:::::::::::" + str("Invoice Date False"))
        for lp in lock_period:
            self.validar_periodos(res, lp)

        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove,self).action_post()
        lock_period = self.env['period.lock'].search([('state','=','lock')])


        if not self.env.user.has_group('period_lock.group_period_lock'):
            for lp in lock_period:
                self.validar_periodos(objeto_bloqueo=lp) 
        return res


    @api.model
    def create(self, vals):
        lock_period = self.env['period.lock'].search([('state','=','lock')])
        res = super(AccountMove,self).create(vals)

        for record in self:
            logging.info('Record ID: %s', record.id)
            for field_name in record._fields:
                value = getattr(record, field_name, None)
                logging.info('Field: %s, Value: %s', field_name, value)

        if not self.env.user.has_group('period_lock.group_period_lock'):
            for lp in lock_period:
                self.validar_periodos(res, lp)
        return res
    
    def validar_periodos(self, objeto_move=None, objeto_bloqueo=None):
        '''Raise Error is Date is in Periodos'''
        if objeto_move is None:
            objeto_move = self

        if objeto_move.invoice_date: #Facturas
            logging.info("Invoice Date:::::::::::" + str(self.invoice_date))
            if objeto_bloqueo.from_date <= objeto_move.invoice_date and objeto_bloqueo.to_date >= objeto_move.invoice_date:
                if objeto_move.journal_id in  objeto_bloqueo.journal_ids:
                    msg="Accounting period locked from "+str(objeto_bloqueo.from_date)+ " to "+ str(objeto_bloqueo.to_date)+" Dates for this journal: "+str(objeto_move.journal_id.name)+"..!"  
                    raise ValidationError(_(msg))
        elif objeto_move.date and objeto_move.invoice_date == False: #Asientos
            logging.info("Raise Error:::::::::::" + str("Invoice Date False"))
            if objeto_bloqueo.from_date <= objeto_move.date and objeto_bloqueo.to_date >= objeto_move.date:
                logging.info("Date:::::::::::" + str(self.date))
                if objeto_move.journal_id in  objeto_bloqueo.journal_ids:
                    msg="Accounting period locked from "+str(objeto_bloqueo.from_date)+ " to "+ str(objeto_bloqueo.to_date)+" Dates for this journal: "+str(objeto_move.journal_id.name)+"..!"  
                    raise ValidationError(_(msg))
        else: #Pagos
            logging.info("Buscar Fecha:::::::::::")

    @api.model
    def button_draft(self):
        res = super(AccountMove,self).button_draft() 
        for record in self:
            logging.info('Record ID: %s', record.id)
            for field_name in record._fields:
                value = getattr(record, field_name, None)
                logging.info('Field: %s, Value: %s', field_name, value)
                # print('Field: %s, Value: %s', field_name, value)
        
        lock_period = self.env['period.lock'].search([('state','=','lock')])
        if not self.env.user.has_group('period_lock.group_period_lock'):
            for lp in lock_period:
                self.validar_periodos(res, lp)
                        
        
        return res