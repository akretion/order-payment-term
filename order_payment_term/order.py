# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    order_payment_term for OpenERP                                          #
#    Copyright (C) 2013 Akretion Chafique DELLI <chafique.delli@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################


from openerp.osv.orm import Model, AbstractModel
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_payment_term_line(Model):
    _inherit = "account.payment.term.line"

    _columns = {
        'on_order': fields.boolean('On Order',
                help='The payment term line will be applied on the order'),

    }

    _defaults = {
        'on_order': False,
    }


class Order(object):

    def _check_amount(self, cr, uid, sale_id, total_paid_amount, total_blocking_amount):
        return total_paid_amount >= total_blocking_amount

    def check_payment_term(self, cr, uid, sale_id, context=None):
        sale_obj = self.pool.get('sale.order')
        move_obj = self.pool.get('account.move')
        #sale_payment_term_obj = self.pool.get('sale.order.payment.term')
        sale = sale_obj.browse(cr, uid, sale_id, context=context)
        #sale_payment_term = sale_payment_term_obj.browse(cr, uid, sale_id, context=context)
        if not sale.payment_term:
            return True

        on_order = any([line.on_order for line in sale.payment_term.line_ids])
        if not on_order:
            return True

        move_ids = move_obj.search(cr, uid, [('ref', '=', sale.name)], context=context)
        total_paid_amount = 0
        total_blocking_amount = sale.amount_total #TODO support percentage on the payment term
        for move_id in move_ids:
            move = move_obj.browse(cr, uid, move_id, context)
            total_paid_amount += move.amount

        if self._check_amount(cr, uid, sale_id, total_paid_amount, total_blocking_amount):
            return True
        return False


class SaleOrderPaymentTerm(Order, Model):
    _inherit = 'sale.order'

    def confirm(self, cr, uid, ids, context=None):
        for sale_id in ids:
            result = self.check_payment_term(cr, uid, sale_id, context)
            if result == True:
                return self.action_button_confirm(cr, uid, ids, context)
            else:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order that is not paid.'))
