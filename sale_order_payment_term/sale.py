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

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.addons.order_payment_term.order import Order


class SaleOrder(Order, orm.Model):
    _inherit = 'sale.order'
    _payment_term_key = 'payment_term'

    def action_button_confirm(self, cr, uid, ids, context=None):
        for sale_id in ids:
            result = self.check_payment_term(cr, uid, sale_id, context)
            if result == True:
                return super(SaleOrder, self).action_button_confirm(cr, uid, ids, context)
            else:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order that is not paid.'))
