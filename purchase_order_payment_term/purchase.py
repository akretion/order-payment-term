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

class PurchaseOrder(orm.Model):
    _inherit = ['purchase.order', 'record2checkterm']
    _name = 'purchase.order'
    _payment_term_key = 'payment_term_id'

    def remove_payment_term_exception(self, cr, uid, ids, context=None):
        for xml_id in ['excep_no_payment_exist', 'excep_min_amount', 'excep_max_amount']:
            self.remove_exception(cr, uid, ids, 'purchase_order_payment_term', xml_id, context=context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if 'payment_term_id' in vals or 'payment_ids' in vals:
            self.remove_payment_term_exception(cr, uid, ids, context=context)
        return super(PurchaseOrder, self).write(cr, uid, ids, vals, context=context)


class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'

    def _get_purchase_ids_to_update(self, cr, uid, vals_purchase_ids, move_ids=None, context=None):
        purchase_ids = []
        for val_purchase_ids in vals_purchase_ids:
            code = val_purchase_ids[0]
            if code not in [3, 4, 5, 6]:
               raise osv.except_osv(_('Error Purchase Order Payment Term'),
                       _('Only mode "3", "4", "5" and "6"'
                       'are supported for the field purchase_ids'))
            
            if code in [3, 4]:
                purchase_ids.append(val_purchase_ids[1])
            elif code == 6:
                purchase_ids += val_purchase_ids[2]
            else:
                purchase_ids = []

            if code in [5, 6] and move_ids:
                #update previous purchase order already linked to the move
                for line in self.browse(cr, uid, move_ids, context=context):
                    for purchase in line.purchase_ids:
                        if not purchase.id in purchase_ids:
                            purchase_ids.append(purchase.id)
        return purchase_ids

    def create(self, cr, uid, vals, context=None):
        if 'purchase_ids' in vals:
            purchase_ids = self._get_purchase_ids_to_update(cr, uid, vals['purchase_ids'],\
                                                            context=context)
            self.pool['purchase.order'].remove_payment_term_exception(cr, uid,\
                                    purchase_ids, context=context)
        return super(AccountMoveLine, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None, **kwargs):
        if 'purchase_ids' in vals:
            purchase_ids = self._get_purchase_ids_to_update(cr, uid, vals['purchase_ids'],\
                                                move_ids=ids, context=context)
            self.pool['purchase.order'].remove_payment_term_exception(cr, uid,\
                                                purchase_ids, context=context)
        return super(AccountMoveLine, self).write(cr, uid, ids, vals,\
                                                context=context, **kwargs)
