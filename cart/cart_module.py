from products.models import Product

CART_SESSION_ID = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        cart = self.cart.copy()

        for item in cart.values():
            product_id = item.get('id')
            if not product_id:
                continue
            product = Product.objects.get(id=int(item['id']))
            item['product'] = product
            item['total'] = int(item['number']) * int(item['price'])
            item['total_discount'] = int(item['number']) * int(item.get('discount', 0))
            item['final_total'] = item['total'] - item['total_discount']
            item['unique_id'] = self.unique_id_generator(product.id, item['color'], item['warranty'])

            yield item

    def unique_id_generator(self, id, color, warranty):
        resuit = f'{id}-{color}-{warranty}'
        return resuit

    def add(self, product, number, color, warranty, size):
        unique = self.unique_id_generator(product.id, color, warranty)

        if unique not in self.cart:
            self.cart[unique] = {'number': 0, 'price': str(product.price),
                                 'discount': str(product.discount) if product.discount else '0',
                                 'color': color, 'warranty': warranty, 'size': size,
                                 'id': product.id}
        if not self.cart[unique].get('discount'):
            self.cart[unique]['discount'] = 0
        self.cart[unique]['number'] += int(number)
        self.save()

    def save(self):
        self.session.modified = True

    def delete(self, id):
        if id in self.cart:
            del self.cart[id]
            self.save()

    def delete_all(self):
        self.cart.clear()
        self.save()

    def get_total_price_all(self):
        total = 0

        for item in self:
            total += item['final_total']

        return total

    def get_total_discount(self):
        total = 0

        for item in self:
            total += item['total_discount']

        return total

    def get_total_price(self):
        total = 0

        for item in self:
            total += item['final_total']

        return total
