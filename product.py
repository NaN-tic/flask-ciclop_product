from flask import Blueprint, render_template, current_app, abort, g, url_for, \
    session, request
from ciclop.tryton import tryton
from ciclop.helpers import login_required
from flask.ext.babel import gettext as _

product = Blueprint('product', __name__, template_folder='templates')

Template = tryton.pool.get('product.template')
Product = tryton.pool.get('product.product')

LIMIT = current_app.config.get('TRYTON_PRODUCT_LIMIT', 100)

@product.route("/", endpoint="products")
@login_required
@tryton.transaction()
def product_products(lang):
    '''Products'''
    # limit
    if request.args.get('limit'):
        try:
            limit = int(request.args.get('limit'))
            session['product_limit'] = limit
        except:
            limit = LIMIT
    else:
        limit = LIMIT

    domain = []
    if request.args.get('q'):
        q = request.args.get('q')
        session['product_q'] = q
        domain = [('rec_name', 'ilike', q)]
    else:
        if session.get('product_q'):
            session.pop('product_q', None)

    total = Product.search_count([])
    products = Product.search(domain, limit=limit)

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('.products', lang=g.language),
        'name': _('Products'),
        }]

    return render_template('products.html',
            breadcrumbs=breadcrumbs,
            total=total,
            products=products,
            )

@product.route("/<int:id>", endpoint="product")
@login_required
@tryton.transaction()
def product_product(lang, id):
    '''Product'''
    products = Product.search([
        ('id', '=', id),
        ], limit=1)
    if not products:
        abort(404)
    product, = products

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('.products', lang=g.language),
        'name': _('Products'),
        }, {
        'slug': url_for('.product', lang=g.language, id=product.id),
        'name': product.rec_name,
        }]

    return render_template('product.html',
            breadcrumbs=breadcrumbs,
            product=product,
            )
