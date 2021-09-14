from django import template
from demo.models import Order, Cart

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        cart=Cart.objects.filter(user=user,ordered=False)
        if qs.exists():
            sum=0
            for i in cart:
                sum=i.quantity+sum
            
           
            return sum
    return 0  