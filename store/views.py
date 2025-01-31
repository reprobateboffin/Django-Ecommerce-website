import json
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import datetime
from .utils import cookieCart,cartData, guestOrder
# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context ={'products':products, 'cartItems':cartItems, 'shipping':False}
    return render(request, 'store/store.html', context)
def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
 

    context = {'items':items, 'order':order, 'cartItems':cartItems,'shipping':False}
    return render(request, 'store/cart.html', context)


def checkout(request):

    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
  
    context ={'items':items, 'order':order,'cartItems':cartItems,'shipping':False }  
    return render(request, 'store/checkout.html', context)

def sample(request):
    product = Product.objects.all()
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
    context ={'products':product}
    return render(request, 'store/sample.html',context)


def sampleCE(request):
    data = json.loads(request.body)
    name = data.get('name')
    action = data.get('action')

    product = Product.objects.get(name=name)
    order, created = Order.objects.get_or_create(complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity +=1
    elif action == 'remove':
        orderItem.quantity -=1
    orderItem.save()
    
    if orderItem.quantity <=0:
        orderItem.delete()
    return JsonResponse('item was added', safe=False)


def updateItem(request):
    data = json.loads(request.body)
    productId = data.get('productId')
    action = data.get('action')
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete = False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product = product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <=0:
        orderItem.delete()
    return JsonResponse('item was added', safe=False)
     

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = False)


    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == order.get_cart_total:
        order.complete = True
    order.save()
    if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    return JsonResponse('payment complete', safe=False)


     