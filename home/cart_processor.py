def cart_item_count(request):
    cart = request.session.get('cart', {})
    count = sum(cart.values())  # sum of all quantities
    return {'cart_count': count}