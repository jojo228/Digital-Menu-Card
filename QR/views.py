from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.shortcuts import HttpResponse
from .models import *
from cart.cart import Cart
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.conf import settings
# from paypal.standard.forms import PayPalPaymentsForm


# Create your views here.

present_pk=0

def home(request):

    return render(request, 'base.html')


def generate_code(request):

    return render(request, 'generate_qr_code.html')


def store(request,pk):
    products = Item.objects.all()
    global present_pk
    present_pk = pk
    pizza = Item.objects.filter(desc="Pizza")
    sandwich = Item.objects.filter(desc="Sandwichs")
    burger = Item.objects.filter(desc="Burgers")
    boisson = Item.objects.filter(desc="Boissons")
    salade = Item.objects.filter(desc="Salades")
    context = {'products': products,
               'pizza': pizza,
               'sandwich': sandwich,
               'burger': burger,
               'boisson': boisson,
               'salade': salade,
               'pk':pk,
               }

    return render(request, 'store.html', context)


# Add to cart
def add_to_cart(request):
	global present_pk
    
	cart_p={}
	cart_p[str(request.GET['id'])]={
		'image':request.GET['image'],
		'name':request.GET['name'],
		'qty':request.GET['qty'],
		'price':request.GET['price'],
	}
	
	if 'cartdata' in request.session:
		if str(request.GET['id']) in request.session['cartdata']:
			cart_data=request.session['cartdata']
			cart_data[str(request.GET['id'])]['qty']=int(cart_p[str(request.GET['id'])]['qty'])
			cart_data.update(cart_data)
			request.session['cartdata']=cart_data
			global present_pk
			print(present_pk)
		else:
			cart_data=request.session['cartdata']
			cart_data.update(cart_p)
			request.session['cartdata']=cart_data
			print(present_pk)
	else:
		request.session['cartdata']=cart_p
	return JsonResponse({'data':request.session['cartdata'],'totalitems':len(request.session['cartdata'])})


# Cart List Page
def cart_list(request):
	global present_pk
	total_amt=0
	if 'cartdata' in request.session:
		global present_pk
		for p_id,item in request.session['cartdata'].items():
			total_amt+=int(item['qty'])*float(item['price'])
		return render(request, 'cart.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt, 'table_no':present_pk})
	else:
		print(present_pk)
		return render(request, 'cart.html',{'cart_data':'','totalitems':0,'total_amt':total_amt, 'table_no':present_pk})


# Delete Cart Item
def delete_cart_item(request):
	p_id=str(request.GET['id'])
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			del request.session['cartdata'][p_id]
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id,item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
	return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})


# update Cart Item
def update_cart_item(request):
	p_id=str(request.GET['id'])
	p_qty=request.GET['qty']
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			cart_data[str(request.GET['id'])]['qty']=p_qty
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id,item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
	return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})


# Checkout
def checkout(request):
	global present_pk
	table_obj = Table.objects.get_or_create(table_no=present_pk)
	total_amt=0
	totalAmt=0
	cart = Cart(request)
	
	if 'cartdata' in request.session:
		for p_id,item in request.session['cartdata'].items():
			total_amt+=int(item['qty'])*float(item['price'])
			# OrderItems
			items=OrderItem.objects.create(
				table=table_obj[0],
				name=item['name'],
				quantity=item['qty'],
				price=item['price'],
				)
		tab_obj = Table.objects.filter(table_no=present_pk)
		tab_obj.total = float(item['qty'])*float(item['price'])
		cart_data=request.session['cartdata']    
		cart_data.clear()    
	return redirect('store', present_pk)


#admin dash
def orders_display(request):
    d = {} 
    tables = [elem[0] for elem in list(Table.objects.all().values_list('table_no'))]
    #print(tables)
    for i in range(len(tables)):
        table_obj = Table.objects.get(table_no = tables[i])
        orders = OrderItem.objects.filter(table=table_obj)
        d[tables[i]] = list(orders.values())
    #print(d)
    context = {"d":d}
    return render(request, 'orders_display.html',context)


def order_status(request,pk):
    d = {}
    tables = [elem[0] for elem in list(Table.objects.all().values_list('table_no'))]
    if pk in tables:
        table_obj = Table.objects.get(table_no = pk)
        order = OrderItem.objects.filter(table=table_obj)
        d[pk] = list(order.values())
        context = {'d':d}
        return render(request, 'order_status.html',context)
    else:
        return HttpResponse('<br><br><br><h2><center>Votre commande est prête ✔️</center></h2>')
    

def order_update(request,id):
    t = Table.objects.get(table_no = id)
    #o = OrderItem.objects.get(table=t)
    """    
    for ord in o:
        PreviousOrders.objects.create(table=id,name=ord.name,price=ord.price,quantity=ord.quantity)
    """
    t.delete()
    return redirect('orders_display')