from django.shortcuts import render, get_object_or_404, redirect
from jobs.models import JobPosting


def index(request):
    jobs_in_cart = []

    # Get the cart from the user's session.
    # If there is no cart yet, use an empty dictionary.
    cart = request.session.get('cart', {})

    # The keys of the cart are the IDs of saved jobs.
    job_ids = list(cart.keys())

    # Get the actual JobPosting objects from the database.
    if job_ids:
        jobs_in_cart = JobPosting.objects.filter(id__in=job_ids)

    template_data = {}
    template_data['title'] = 'Cart'
    template_data['jobs_in_cart'] = jobs_in_cart

    return render(
        request,
        'cart/index.html',
        {'template_data': template_data}
    )


def add(request, id):
    # Make sure the job actually exists.
    get_object_or_404(JobPosting, id=id)
    cart = request.session.get('cart', {})
    cart[str(id)] = True
    request.session['cart'] = cart

    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

def remove(request, id):
    cart = request.session.get('cart', {})
    job_id = str(id)
    if job_id in cart:
        del cart[job_id]

    request.session['cart'] = cart
    return redirect('cart.index')

