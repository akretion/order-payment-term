# -*- coding: utf-8 -*-
###############################################################################
#
#   order_payment_term for OpenERP 
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   @author Chafique DELLI <chafique.delli@akretion.com>
#           Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm, osv
from openerp.tools.translate import _
from openerp.addons.order_payment_term.order import Order


class SaleOrder(Order, orm.Model):
    _inherit = 'sale.order'
    _payment_term_key = 'payment_term'

    def remove_payment_term_exception(self, cr, uid, ids, context=None):
        for xml_id in ['excep_no_payment_exist', 'excep_incorrect_amount_paid']:
            self.remove_exception(cr, uid, ids, 'sale_order_payment_term', xml_id, context=context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if 'payment_term' in vals or 'payment_ids' in vals:
            self.remove_payment_term_exception(cr, uid, ids, context=context)
        return super(SaleOrder, self).write(cr, uid, ids, vals, context=context)


class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'

    def _get_sale_ids_to_update(self, cr, uid, vals_sale_ids, move_ids=None, context=None):
        sale_ids = []
        for val_sale_ids in vals_sale_ids:
            code = val_sale_ids[0]
            if code not in [3, 4, 5, 6]:
               raise osv.except_osv(_('Error Sale Order Payment Term'),
                       _('Only mode "3", "4", "5" and "6"'
                       'are supported for the field sale_ids'))
            
            if code in [3, 4]:
                sale_ids.append(val_sale_ids[1])
            elif code == 6:
                sale_ids += val_sale_ids[2]
            else:
                sale_ids = []

            if code in [5, 6] and move_ids:
                #update previous sale order already linked to the move
                for line in self.browse(cr, uid, move_ids, context=context):
                    for sale in line.sale_ids:
                        if not sale.id in sale_ids:
                            sale_ids.append(sale.id)
        return sale_ids

    def create(self, cr, uid, vals, context=None):
        if 'sale_ids' in vals:
            sale_ids = self._get_sale_ids_to_update(cr, uid, vals['sale_ids'],\
                                                            context=context)
            self.pool['sale.order'].remove_payment_term_exception(cr, uid,\
                                    sale_ids, context=context)
        return super(AccountMoveLine, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None, **kwargs):
        if 'sale_ids' in vals:
            sale_ids = self._get_sale_ids_to_update(cr, uid, vals['sale_ids'],\
                                                move_ids=ids, context=context)
            self.pool['sale.order'].remove_payment_term_exception(cr, uid,\
                                                sale_ids, context=context)
        return super(AccountMoveLine, self).write(cr, uid, ids, vals,\
                                                context=context, **kwargs)
