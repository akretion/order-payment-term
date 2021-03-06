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

from openerp.osv import fields, orm

class Record2CheckTerm(orm.AbstractModel):
    _name = "record2checkterm"

    def _get_blocking_amount(self, cr, uid, order, context=None):
        amount = order.amount_total
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        payment_term = order[self._payment_term_key]

        res = 0
        for line in payment_term.line_ids:
            if line.on_order:
                if line.value == 'fixed':
                    res += round(line.value_amount, prec)
                elif line.value == 'procent':
                    res += round(order.amount_total * line.value_amount, prec)
                elif line.value == 'balance':
                    res += round(amount, prec)
        return res

    def need_payment(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This method should only be used for a single id at a time'
        order = self.browse(cr, uid, ids[0], context=context)
        payment_term = order[self._payment_term_key]
        if not payment_term or not payment_term.line_ids:
            return False

        return any([line.on_order for line in payment_term.line_ids])

    def check_payment(self, cr, uid, ids, delta_min=None, delta_max=None, context=None):
        """
        :param delta_min: tolerated minimal diference should be negative
        :param delta_max: toterated maximal diference should be positive
        :return: True or False
        :rtype: boolean
        """
        assert len(ids) == 1, 'This method should only be used for a single id at a time'
        assert not (delta_min is None and delta_max is None), 'You must check at least on delta max or min'

        if delta_min is not None:
            assert delta_min <= 0, 'Delta Min should be negative'
        if delta_max is not None:
            assert delta_max >= 0, 'Delta Max should be positive'

        if not self.need_payment(cr, uid, ids, context=context):
            return True
        order = self.browse(cr, uid, ids[0], context=context)

        total_blocking_amount = self._get_blocking_amount(cr, uid, order, context=context)
        
        diff_amount = order.amount_paid - total_blocking_amount
        decimal_precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Account')
        float_delta = pow(0.1, decimal_precision + 1)
        if delta_min is not None and diff_amount < (delta_min - float_delta):
            return False
        if delta_max is not None and diff_amount > (delta_max + float_delta):
            return False
        return True

