from django import template

register = template.Library()

@register.filter
def total_amount(orders):
    total = sum(order['total_amount'] for order in orders)
    return total
