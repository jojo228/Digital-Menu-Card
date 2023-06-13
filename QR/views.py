from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import HttpResponse
from .models import *
from cart.cart import Cart
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.conf import settings

# from paypal.standard.forms import PayPalPaymentsForm


# Create your views here.

present_pk = 0


def home(request):
    return render(request, "base.html")


def generate_code(request):
    return render(request, "generate_qr_code.html")


def store(request, slug, table_id):
    global present_pk
    store = Store.objects.get(slug=slug)
    present_pk = table_id
    products = Item.objects.filter(
        store=store
    )  # Retrieve items belonging to the specific store
    pizza = products.filter(categorie="Pizza")
    sandwich = products.filter(categorie="Sandwichs")
    burger = products.filter(categorie="Burgers")
    boisson = products.filter(categorie="Boissons")
    salade = products.filter(categorie="Salades")
    context = {
        "products": products,
        "pizza": pizza,
        "sandwich": sandwich,
        "burger": burger,
        "boisson": boisson,
        "salade": salade,
        "store": store,
        "table": table_id,
    }

    return render(request, "store.html", context)


# Add to cart
def add_to_cart(request, slug, table_id):
    store = Store.objects.get(slug=slug)
    present_pk = table_id

    cart_p = {}
    cart_p[str(request.GET["id"])] = {
        "image": request.GET["image"],
        "name": request.GET["name"],
        "qty": request.GET["qty"],
        "price": request.GET["price"],
    }

    if "cartdata" in request.session:
        if str(request.GET["id"]) in request.session["cartdata"]:
            cart_data = request.session["cartdata"]
            cart_data[str(request.GET["id"])]["qty"] = int(
                cart_p[str(request.GET["id"])]["qty"]
            )
            cart_data.update(cart_data)
            request.session["cartdata"] = cart_data
            present_pk
            print(present_pk)
        else:
            cart_data = request.session["cartdata"]
            cart_data.update(cart_p)
            request.session["cartdata"] = cart_data
            print(present_pk)
    else:
        request.session["cartdata"] = cart_p
    return JsonResponse(
        {
            "data": request.session["cartdata"],
            "totalitems": len(request.session["cartdata"]),
        }
    )


# Cart List Page
def cart_list(request, slug, table_id):
    global present_pk
    store = Store.objects.get(slug=slug)
    present_pk = table_id
    total_amt = 0
    if "cartdata" in request.session:
        table_id
        for p_id, item in request.session["cartdata"].items():
            total_amt += int(item["qty"]) * float(item["price"])
        return render(
            request,
            "cart.html",
            {
                "cart_data": request.session["cartdata"],
                "totalitems": len(request.session["cartdata"]),
                "total_amt": total_amt,
                "table": table_id,
                "store": store,
            },
        )
    else:
        return render(
            request,
            "cart.html",
            {
                "cart_data": "",
                "totalitems": 0,
                "total_amt": total_amt,
                "table_no": table_id,
            },
        )


# Delete Cart Item
def delete_cart_item(request):
    p_id = str(request.GET["id"])
    if "cartdata" in request.session:
        if p_id in request.session["cartdata"]:
            cart_data = request.session["cartdata"]
            del request.session["cartdata"][p_id]
            request.session["cartdata"] = cart_data
    total_amt = 0
    for p_id, item in request.session["cartdata"].items():
        total_amt += int(item["qty"]) * float(item["price"])
    t = render_to_string(
        "ajax/cart-list.html",
        {
            "cart_data": request.session["cartdata"],
            "totalitems": len(request.session["cartdata"]),
            "total_amt": total_amt,
        },
    )
    return JsonResponse({"data": t, "totalitems": len(request.session["cartdata"])})


# update Cart Item
def update_cart_item(request, slug, table_id):
    global present_pk
    store = Store.objects.get(slug=slug)
    present_pk = table_id

    p_id = str(request.GET["id"])
    p_qty = request.GET["qty"]
    if "cartdata" in request.session:
        if p_id in request.session["cartdata"]:
            cart_data = request.session["cartdata"]
            cart_data[str(request.GET["id"])]["qty"] = p_qty
            request.session["cartdata"] = cart_data
    total_amt = 0
    for p_id, item in request.session["cartdata"].items():
        total_amt += int(item["qty"]) * float(item["price"])
    t = render_to_string(
        "ajax/cart-list.html",
        {
            "cart_data": request.session["cartdata"],
            "totalitems": len(request.session["cartdata"]),
            "total_amt": total_amt,
            "table": table_id,
            "store": store,
        },
    )

    return JsonResponse({"data": t, "totalitems": len(request.session["cartdata"])})


# Checkout


def checkout(request, slug, table_id):
    global present_pk
    table_id = present_pk
    store = Store.objects.get(slug=slug)

    table, _ = Table.objects.get_or_create(store=store, table_no=table_id)

    cart_data = request.session.get("cartdata", {})
    total_amt = 0

    for item in cart_data.values():
        total_amt += int(item["qty"]) * float(item["price"])
        OrderItem.objects.create(
            table=table,
            name=item["name"],
            quantity=item["qty"],
            price=item["price"],
        )

    table.total = total_amt
    table.save()

    cart_data.clear()
    request.session["cartdata"] = cart_data

    return redirect("store", slug, table_id)


# admin dash
def orders_display(request, slug):
    store = Store.objects.get(slug=slug)
    orders_by_table = {}
    tables = [
        elem[0]
        for elem in list(
            Table.objects.all().filter(store=store).values_list("table_no")
        )
    ]
    for i in range(len(tables)):
        table_obj = Table.objects.filter(store=store, table_no=tables[i])
        orders = OrderItem.objects.filter(table__in=table_obj)
        orders_by_table[tables[i]] = list(orders.values())
    context = {"orders_by_table": orders_by_table, "store": store}
    return render(request, "orders_display.html", context)


def order_status(request, slug, table_id):
    global present_pk
    table_id = present_pk
    store = Store.objects.get(slug=slug)
    d = {}
    tables = [elem[0] for elem in list(Table.objects.all().values_list("table_no"))]
    if table_id in tables:
        table_obj = Table.objects.get(table_no=table_id)
        order = OrderItem.objects.filter(table=table_obj)
        d[table_id] = list(order.values())
        context = {"d": d}
        return render(request, "order_status.html", context)
    else:
        return HttpResponse(
            "<br><br><br><h2><center>Votre commande est prête ✔️</center></h2>"
        )


def order_update(request, slug, id):
    store = Store.objects.get(slug=slug)
    print(store)

    t = Table.objects.get(store=store, table_no=id)

    t.delete()
    return redirect("orders_display", slug)
