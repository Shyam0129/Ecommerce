import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, Category, Cart, Order, SupportQuery, Review

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    logger.info("Home view accessed")
    books = Product.objects.filter(category__name='Books')[:4]
    shoes = Product.objects.filter(category__name='Shoes')[:6]
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/home.html', {'books': books, 'shoes': shoes, 'cart_item_count': cart_item_count})

def books(request):
    logger.info("Books view accessed")
    products = Product.objects.filter(category__name='Books')[:12]
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/books.html', {'products': products, 'cart_item_count': cart_item_count})

def shoes(request):
    logger.info("Shoes view accessed")
    products = Product.objects.filter(category__name='Shoes')[:12]
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/shoes.html', {'products': products, 'cart_item_count': cart_item_count})

def product_detail(request, product_id):
    logger.info(f"Product detail view accessed for product {product_id}")
    product = get_object_or_404(Product, id=product_id)
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    reviews = product.review_set.all()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart_item_count': cart_item_count,
        'reviews': reviews,
        'category': product.category.name
    })

@login_required
def add_to_cart(request, product_id):
    logger.info(f"Add to cart accessed for product {product_id}")
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login first to add to cart', 'redirect': '/login/'}, status=403)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = Product.objects.get(id=product_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()
        return redirect('store:cart_detail')
    return redirect('store:books')

@login_required
def cart_detail(request):
    logger.info("Cart detail view accessed")
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.quantity * item.product.price for item in cart_items)
    for item in cart_items:
        item.subtotal = item.quantity * item.product.price
    cart_item_count = cart_items.count()
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total, 'cart_item_count': cart_item_count})

@login_required
def update_cart(request, item_id):
    logger.info(f"Update cart accessed for item {item_id}")
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity >= 1:
            cart_item.quantity = quantity
            cart_item.save()
            return redirect('store:cart_detail')
    return HttpResponseBadRequest("Invalid quantity")

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        Order.objects.create(
            user=request.user,
            product=product,
            quantity=1,
            total_amount=product.price,
            shipping_address=request.user.profile.address if hasattr(request.user, 'profile') else "Default Address",
            status='Order Placed'
        )
        return redirect('store:order_history')
    return redirect('store:product_detail', product_id=product_id)

@login_required
def remove_from_cart(request, item_id):
    logger.info(f"Remove from cart accessed for item {item_id}")
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        cart_item.delete()
        return redirect('store:cart_detail')
    return HttpResponseBadRequest("Invalid request")

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def checkout(request):
    logger.info("Checkout view accessed")
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.quantity * item.product.price for item in cart_items)
    for item in cart_items:
        item.subtotal = item.quantity * item.product.price
    if not cart_items:
        return redirect('store:cart_detail')
    cart_item_count = cart_items.count()
    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total, 'cart_item_count': cart_item_count})

@login_required
def confirm_order(request):
    logger.info("Confirm order view accessed")
    if request.method == "POST" and request.headers.get('X-Confirmed') == 'true':
        cart_items = Cart.objects.filter(user=request.user)
        if cart_items:
            for item in cart_items:
                Order.objects.create(user=request.user, product=item.product, quantity=item.quantity, total_amount=item.subtotal, shipping_address="Sample Address", status="Pending")
            cart_items.delete()
        return JsonResponse({'message': 'Order confirmed', 'redirect': '/profile/'})
    return redirect('store:checkout')

def login_view(request):
    logger.info("Login view accessed")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store:home')
        else:
            messages.error(request, "Invalid username or password.")
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/login.html', {'cart_item_count': cart_item_count})

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        request.session['temp_email'] = email
        messages.success(request, "Verification email sent. Please create your password.")
        return redirect('store:create_password')
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/signup.html', {'cart_item_count': cart_item_count})

def create_password(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        email = request.session.get('temp_email')
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'store/create_password.html', {'cart_item_count': Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0})
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'store/create_password.html', {'cart_item_count': Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0})
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        del request.session['temp_email']
        return redirect('store:home')
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/create_password.html', {'cart_item_count': cart_item_count})

def logout_view(request):
    logout(request)
    return redirect('store:home')

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/myaccount.html', {'orders': orders, 'cart_item_count': cart_item_count})

@login_required
def write_review(request, category, product_id):
    logger.info(f"Write review accessed for product {product_id} in category {category}")
    product = get_object_or_404(Product, id=product_id, category__name=category)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
            return redirect('store:view_reviews', category=category, product_id=product_id)
        else:
            messages.error(request, "Rating and comment are required.")
    return render(request, 'store/write_review.html', {'product': product})

@login_required
def view_reviews(request, category, product_id):
    product = get_object_or_404(Product, id=product_id, category__name=category)
    reviews = Review.objects.filter(product=product)
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/reviews.html', {'product': product, 'reviews': reviews, 'cart_item_count': cart_item_count})

@login_required
def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('store:admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials.")
    return render(request, 'store/admin_login.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('store:home')
    products = Product.objects.all()
    return render(request, 'store/admin_dashboard.html', {'products': products})

@login_required
def support(request):
    logger.info("Support view accessed")
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        query = request.POST.get('query')
        if name and email and phone and subject and query:
            SupportQuery.objects.create(user=request.user, query=query, name=name, email=email, phone=phone, subject=subject)
            messages.success(request, "Query submitted successfully.")
            return redirect('store:support')
        messages.error(request, "All fields are required.")
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'store/support.html', {'cart_item_count': cart_item_count})

@login_required
def support_dashboard(request):
    if not request.user.groups.filter(name='Support').exists():
        return redirect('store:home')
    queries = SupportQuery.objects.filter(resolved=False)
    orders = Order.objects.all()
    return render(request, 'store/support_dashboard.html', {'queries': queries, 'orders': orders})

@login_required
def respond_query(request, query_id):
    logger.info(f"Respond query accessed for query {query_id}")
    query = get_object_or_404(SupportQuery, id=query_id)
    if request.method == 'POST':
        response = request.POST.get('response')
        query.response = response
        query.resolved = True
        query.save()
        return redirect('store:support_dashboard')
    return HttpResponseBadRequest("Invalid request")

@login_required
def fulfill_order(request, order_id):
    logger.info(f"Fulfill order accessed for order {order_id}")
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = 'Fulfilled'
        order.save()
        return redirect('store:support_dashboard')
    return HttpResponseBadRequest("Invalid request")