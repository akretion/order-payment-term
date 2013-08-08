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


class Order(object):

    def _check_amount(self, cr, uid, order_id, total_paid_amount, total_blocking_amount):
        return total_paid_amount >= total_blocking_amount

    def check_payment_term(self, cr, uid, order_id, context=None):
        order = self.browse(cr, uid, order_id, context=context)
        payment_term = order[self._payment_term_key]

        if not payment_term:
            return True

        on_order = any([line.on_order for line in payment_term.line_ids])
        if not on_order:
            return True

        total_paid_amount = 0
        total_blocking_amount = order.amount_total #TODO support percentage on the payment term
        for line in order.payment_ids:
            total_paid_amount += line.debit - line.credit

        if self._check_amount(cr, uid, order_id, total_paid_amount, total_blocking_amount):
            return True
        return False

