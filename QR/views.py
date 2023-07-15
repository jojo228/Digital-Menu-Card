from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import HttpResponse
from .models import *
from cart.cart import Cart
from django.db.models import F, Q, Sum
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
    # Store the table ID in a global variable for future use
    global present_pk

    # Get the store object based on the provided slug
    store = Store.objects.get(slug=slug)

    # Check if the store is active
    if not store.is_active():
        # Handle the case when the store is not active
        return render(request, "inactive_store.html")

    # Store the table ID
    present_pk = table_id

    # Retrieve all items belonging to the specific store
    products = Item.objects.filter(store=store)

    # Filter products by category
    pizza = products.filter(categorie="Pizza")
    sandwich = products.filter(categorie="Sandwichs")
    burger = products.filter(categorie="Burgers")
    boisson = products.filter(categorie="Boissons")
    salade = products.filter(categorie="Salades")
    africaine = products.filter(categorie="Africaine")

    # Search functionality
    search_query = request.GET.get("search")
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Create a context dictionary with the retrieved data
    context = {
        "products": products,
        "pizza": pizza,
        "sandwich": sandwich,
        "burger": burger,
        "boisson": boisson,
        "salade": salade,
        "africaine": africaine,
        "store": store,
        "table": table_id,
    }

    # Render the store.html template with the provided context
    return render(request, "store.html", context)


# Add to cart
def add_to_cart(request, slug, table_id):
    # Get the store object based on the slug
    store = Store.objects.get(slug=slug)

    # Get the table ID
    present_pk = table_id

    # Create a dictionary to hold the cart data
    cart_p = {}

    # Populate the cart data with the received GET parameters
    cart_p[str(request.GET["id"])] = {
        "image": request.GET["image"],
        "name": request.GET["name"],
        "qty": request.GET["qty"],
        "price": request.GET["price"],
    }

    # Check if cart data already exists in the session
    if "cartdata" in request.session:
        # Check if the item already exists in the cart
        if str(request.GET["id"]) in request.session["cartdata"]:
            cart_data = request.session["cartdata"]

            # Update the quantity of the existing item in the cart
            cart_data[str(request.GET["id"])]["qty"] = int(
                cart_p[str(request.GET["id"])]["qty"]
            )

            cart_data.update(cart_data)

            # Update the cart data in the session
            request.session["cartdata"] = cart_data

            present_pk
            print(present_pk)
        else:
            cart_data = request.session["cartdata"]

            # Add the new item to the cart
            cart_data.update(cart_p)

            # Update the cart data in the session
            request.session["cartdata"] = cart_data

            print(present_pk)
    else:
        # If no cart data exists in the session, create a new cart
        request.session["cartdata"] = cart_p

    # Return a JSON response with the cart data and the total number of items in the cart
    return JsonResponse(
        {
            "data": request.session["cartdata"],
            "totalitems": len(request.session["cartdata"]),
        }
    )


# Cart List Page
def cart_list(request, slug, table_id):
    # Store the table ID in a global variable for future use
    global present_pk

    # Get the store object based on the provided slug
    store = Store.objects.get(slug=slug)

    # Store the table ID
    present_pk = table_id

    total_amt = 0

    # Check if cart data exists in the session
    if "cartdata" in request.session:
        table_id  # Not sure what this line does, seems redundant

        # Calculate the total amount by iterating over the cart items
        for p_id, item in request.session["cartdata"].items():
            total_amt += int(item["qty"]) * float(item["price"])

        # Render the cart.html template with the cart data, total items, total amount, table ID, and store object
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
        # If no cart data exists in the session, render the cart.html template with default values
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


@csrf_exempt
def delete_cart_item(request, slug, table_id):
    if request.method == "POST":
        product_id = request.POST.get("product_id")

        if "cartdata" in request.session:
            cart_data = request.session.get("cartdata", {})

            if product_id in cart_data:
                del cart_data[product_id]
                request.session["cartdata"] = cart_data
                request.session.modified = True  # Mark the session as modified

                return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "Product not found in cart"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


# Update Cart Item
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def update_cart_item(request, slug, table_id):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity"))

        if "cartdata" in request.session:
            cart_data = request.session["cartdata"]

            if product_id in cart_data:
                cart_data[product_id]["qty"] = quantity
                request.session["cartdata"] = cart_data
                request.session.modified = True  # Mark the session as modified

                return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "Product not found in cart"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


# Checkout
def checkout(request, slug, table_id):
    # Store the table ID in a global variable for future use
    global present_pk

    # Retrieve the store object based on the provided slug
    store = Store.objects.get(slug=slug)

    # Assign the present_pk value to the table_id
    table_id = present_pk

    # Get or create a table object for the store and table_id
    table, _ = Table.objects.get_or_create(store=store, table_no=table_id)

    # Retrieve the cart data from the session
    cart_data = request.session.get("cartdata", {})
    total_amt = 0

    # Iterate over the items in the cart and calculate the total amount
    for item in cart_data.values():
        total_amt += int(item["qty"]) * float(item["price"])

        # Create an OrderItem object for each item in the cart
        OrderItem.objects.create(
            table=table,
            name=item["name"],
            quantity=item["qty"],
            price=item["price"],
            total_amount=total_amt,
        )

    # Update the total amount of the table and save it
    table.total = total_amt
    table.save()

    # Clear the cart data and update the session
    cart_data.clear()
    request.session["cartdata"] = cart_data

    # Redirect to the store page
    return redirect("order_status", slug, table_id)


# Admin Dashboard
from django.db.models import Sum

from django.db.models import Sum

def orders_display(request, slug):
    store = Store.objects.get(slug=slug)
    orders_by_table = {}
    total_amount_by_table = {}  # Dictionary to store total amount for each table

    tables = [
        elem[0]
        for elem in list(
            Table.objects.all().filter(store=store).values_list("table_no")
        )
    ]

    for table_no in tables:
        table_obj = Table.objects.filter(store=store, table_no=table_no)
        orders = OrderItem.objects.filter(table__in=table_obj)
        orders_by_table[table_no] = list(orders.values())

        total_amount = orders.aggregate(total=Sum("total_amount"))
        total_amount_by_table[table_no] = total_amount["total"]

    context = {
        "orders_by_table": orders_by_table,
        "store": store,
        "total_amount_by_table": total_amount_by_table,
    }

    return render(request, "orders_display.html", context)




def order_status(request, slug, table_id):
    # Store the table ID in a global variable for future use
    global present_pk

    # Assign the present_pk value to the table_id
    table_id = present_pk

    # Retrieve the store object based on the provided slug
    store = Store.objects.get(slug=slug)

    d = {}

    # Get the list of table numbers from all the tables
    tables = [
        elem[0]
        for elem in list(
            Table.objects.all().filter(store=store).values_list("table_no")
        )
    ]

    if table_id in tables:
        table_obj = Table.objects.get(store=store, table_no=table_id)

        # Retrieve the order items for the specified table
        order = OrderItem.objects.filter(table=table_obj)

        d[table_id] = list(order.values())

        # Prepare the context dictionary for rendering the template
        context = {
            "d": d,
            "table": table_id,
            "store": store,
        }

        # Render the order_status.html template with the provided context
        return render(request, "order_status.html", context)
    else:
        # If the table is not found, display a message indicating that the order is ready
        return HttpResponse(
            "<br><br><br><h2><center>Vous n'avez aucune commande en cours ✔️</center></h2>"
        )


def order_update(request, slug, id):
    # Retrieve the store object based on the provided slug
    store = Store.objects.get(slug=slug)

    # Retrieve the Table object based on the store and table_no
    t = Table.objects.get(store=store, table_no=id)

    # Delete the table object
    t.delete()

    # Redirect to the orders_display page
    return redirect("orders_display", slug)


# Add this view to handle the redirection
def session_expired(request):
    return render(request, "session_expired.html")
