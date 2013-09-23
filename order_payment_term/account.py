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

from openerp.osv import orm, fields


class account_payment_term_line(orm.Model):
    _inherit = "account.payment.term.line"

    _columns = {
        'on_order': fields.boolean('On Order',
                help='The payment term line will be applied on the order'),

    }

    _defaults = {
        'on_order': False,
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('on_order'):
            vals.update({'days': 0, 'days2': 0})
        return super(account_payment_term_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('on_order'):
            vals.update({'days': 0, 'days2': 0})
        return super(account_payment_term_line, self).write(cr, uid, ids, vals, context=context)
