from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from stripe.api_resources import charge
from .models import *
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms  import CheckoutForm
import stripe

# stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

# Create your views here.
def products(request):
    return render(request,"home.html")

def maleproducts(request):
    item=Product.objects.filter(category='M')
    items={
        'items': item,
    }
    return render(request,"male.html",items)

def femaleproducts(request):
    item=Product.objects.filter(category="F")
    items={
        'items': item,
    }
    return render(request,"female.html",items)

def kidsproducts(request):
    item=Product.objects.filter(category="K")
    items={
        'items': item,
    }
    return render(request,"kids.html",items)

@login_required
def add_to_cart(request,id):
    item=Product.objects.get(id=id)
    order_item=Cart.objects.get_or_create(user=request.user, item=item)
    c=Cart.objects.get(user=request.user,item=item)
    ordered_date=timezone.now()
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        if order_item[1]==False:
            c.quantity += 1
            c.save()
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, orderd_date=ordered_date)
        order.items.add(c.id)    
    
    
    if item.category=="M":
        messages.info(request, "This item was added to your cart.")
        return redirect("maleproducts")
    elif item.category=="F":
        messages.info(request, "This item was added to your cart.")
        return redirect("femaleproducts")
    else:
        messages.info(request, "This item was added to your cart.")
        return redirect("kidsproducts")

@login_required
def remove_from_cart(request, id):
    item = Product.objects.get(id=id)
    try:
        c=Cart.objects.get(user=request.user,item=item)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        order = order_qs[0]
        
        if order_qs.exists():
            order.items.remove(c.item.id)
            c.delete()
            
            if item.category=="M":
                messages.info(request, "This item was removed from your cart.")
                return redirect("maleproducts")
            elif item.category=="F":
                messages.info(request, "This item was removed from your cart.")
                return redirect("femaleproducts")
            else:
                messages.info(request, "This item was removed from your cart.")
                return redirect("kidsproducts")
    
    except:
        messages.info(request, "This item was not in your cart")
        return redirect("products")

@login_required
def remove_one_item_from_cart(request, id):
    item = Product.objects.get(id=id)
    try:
        c=Cart.objects.get(user=request.user,item=item)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        
        if order_qs.exists():
            c.quantity -= 1
            c.save()
            
            if item.category=="M":
                messages.info(request, "This item quantity was updated")
                return redirect("maleproducts")
            elif item.category=="F":
                messages.info(request, "This item quantity was updated.")
                return redirect("femaleproducts")
            else:
                messages.info(request, "This item quantity was updated.")
                return redirect("kidsproducts")
    
    except:
        messages.info(request, "This item was not in your cart")
        return redirect("products")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            cart=Cart.objects.filter(user=self.request.user,ordered=False)
            y=self.request.user
            x=get_total(y)
            order.t=x
            context = {
                'object': cart,
                'order':order
            }
            return render(self.request, 'order_summary.html',context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

def get_total(y):
    total = 0
    cart=Cart.objects.filter(user=y,ordered=False)  
    for order_item in cart:
        total += order_item.get_final_price()
    return int(total)


class checkout(View):
    def get(self, *args, **wargs):
        form=CheckoutForm()
        context={
            'form': form
        }
        return render(self.request,"checkout.html", context)

    def post(self, *args, **wargs):
        form= CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                shipping_address = form.cleaned_data.get('shipping_address')
                shipping_address2 = form.cleaned_data.get('shipping_address2 ')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_zip= form.cleaned_data.get('shipping_zip')
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # set_default_shipping= form.cleaned_data.get('set_default_shipping')
                payment_option= form.cleaned_data.get('payment_option')
                address= Address(
                    user=self.request.user,
                    shipping_address=shipping_address,
                    shipping_address2=shipping_address2,
                    shipping_country=shipping_country,
                    shipping_zip=shipping_zip,
                )
                address.save()
                order.billing_address=address
                order.save()

                if payment_option=='S':
                    return redirect("payment",payment_option='stripe')
                elif payment_option=='P':
                    return redirect("payment",payment_option='paypal')
                else:     
                    messages.warning(self.request,"Invalid Payment Choice")
                    return redirect("checkout")

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("ordersummary")

     
class PaymentView(View):
    
    def get(self, *args, **kwargs):
        order=Order.objects.get(user=self.request.user, ordered=False)
        cart=Cart.objects.filter(user=self.request.user,ordered=False)
        y=self.request.user
        x=get_total(y)
        order.t=x
        sum=0
        for i in cart:
            sum=i.quantity+sum
        cart.sum=sum    
        context={
            'object': cart,
            'order':order
        }
        print(cart.count())
        return render(self.request,"payment.html",context)

    def post(self, *args, **kwargs):
        
        order=Order.objects.get(user=self.request.user, ordered=False)
        token= self.request.POST.get('stripeToken')
        amount=get_total(self.request.user) 
        try:
            charge =stripe.Charge.create(
                amount=int(amount*100),
                currency="USD",
                source='tok_visa',
            )
            #create the payment
            payment=Payment()
            payment.stripe_charge_id=charge['id']
            payment.user=self.request.user
            payment.amount=get_total(self.request.user)
            payment.save()

            # assign the payment to order
            cart=Cart.objects.filter(user=self.request.user,ordered=False)
            #cart.update(ordered=True)

            # order_items=order.items.all()
            # order_items.update(ordered=True)
            for item in cart:
                item.ordered=True
                item.save()

            order.ordered = True 
            order.payment= payment
            order.save()
        
            messages.success(self.request, "Your order was successfull")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")

        # messages.warning(self.request, "Invalid data received")
        # return redirect("/payment/stripe/")


       




