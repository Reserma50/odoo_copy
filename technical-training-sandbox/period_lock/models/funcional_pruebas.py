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
        for record in self:
            print("******************* \n \n \n " + str(record.id))
            for field_name in record._fields:
                value = getattr(record, field_name, None)
                
            logging.info('********** \nField: %s', self)
            logging.info("Raise Error:::::::::::" + str("Invoice Date False"))
            for lp in lock_period:
                if lp.from_date <= self.date and lp.to_date >= self.date:
                    logging.info("Date:::::::::::" + str(self.date))
                    if self.journal_id in  lp.journal_ids:
                        msg="Accounting period locked from "+str(lp.from_date)+ " to "+ str(lp.to_date)+" Dates for this journal: "+str(self.journal_id.name)+"..!"  
                        raise ValidationError(_(msg))


        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove,self).action_post()
        lock_period = self.env['period.lock'].search([('state','=','lock')])

        for record in self:
            
            print("******************* \n \n \n " + str(record.id))
            # for field_name in record._fields:
            #     value = getattr(record, field_name, None)
        logging.info('********** \nField: %s', self)

        if not self.env.user.has_group('period_lock.group_period_lock'):
            for lp in lock_period:
                
                if self.invoice_date: #Facturas
                    if lp.from_date <= self.invoice_date and lp.to_date >= self.invoice_date:
                        logging.info("Invoice Date:::::::::::" + str(self.invoice_date))
                        if self.journal_id in  lp.journal_ids:
                            msg="Accounting period locked from "+str(lp.from_date)+ " to "+ str(lp.to_date)+" Dates for this journal: "+str(self.journal_id.name)+"..!"  
                            raise ValidationError(_(msg))
                elif self.date and self.invoice_date == False: #Asientos
                    logging.info("Raise Error:::::::::::" + str("Invoice Date False"))
                    if lp.from_date <= self.date and lp.to_date >= self.date:
                        logging.info("Date:::::::::::" + str(self.date))
                        if self.journal_id in  lp.journal_ids:
                            msg="Accounting period locked from "+str(lp.from_date)+ " to "+ str(lp.to_date)+" Dates for this journal: "+str(self.journal_id.name)+"..!"  
                            raise ValidationError(_(msg))
                else:
                    logging.info("Buscar Fecha Pagos:::::::::::") 
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
                if res.invoice_date:
                    if lp.from_date <= res.invoice_date and lp.to_date >= res.invoice_date:
                        if res.journal_id in  lp.journal_ids:
                            msg="Accounting period locked from "+str(lp.from_date)+ " to "+ str(lp.to_date)+" Dates for this journal: "+str(res.journal_id.name)+"..!"  
                            raise ValidationError(_(msg))
                else:
                    if lp.from_date <= res.date and lp.to_date >= res.date:
                        if res.journal_id in  lp.journal_ids:
                            msg="Accounting period locked from "+str(lp.from_date)+ " to "+ str(lp.to_date)+" Dates for this journal: "+str(res.journal_id.name)+"..!"  
                            raise ValidationError(_(msg))
        return res

    @api.model
    def button_draft(self):

        for record in self:
            logging.info('Record ID: %s', record.id)
            for field_name in record._fields:
                value = getattr(record, field_name, None)
                logging.info('Field: %s, Value: %s', field_name, value)
                # print('Field: %s, Value: %s', field_name, value)

        
        lock_period = self.env['period.lock'].search([('state','=','lock')])
        if not self.env.user.has_group('period_lock.group_period_lock'):
            for lp in lock_period:
                if self.invoice_date == False: #Pagos #Asientos
                    if lp.from_date <= self.date and lp.to_date >= self.date:
                        logging.info("Date:::::::::::" + str(self.date))
                        if self.journal_id in  lp.journal_ids:
                            msg="Accounting period locked from "+str(lp.from_date)+ " to "+ str(lp.to_date)+" Dates for this journal: "+str(self.journal_id.name)+"..!"  
                            raise ValidationError(_(msg))
                else: #Facturas
                    if lp.from_date <= self.invoice_date and lp.to_date >= self.invoice_date:
                        logging.info("Date:::::::::::" + str(self.invoice_date))
                        if self.journal_id in  lp.journal_ids:
                            msg="Accounting period locked from "+str(lp.from_date)+ " to "+ str(lp.to_date)+" Dates for this journal: "+str(self.journal_id.name)+"..!"  
                            raise ValidationError(_(msg))
                        
        res = super(AccountMove,self).button_draft() 
        return res