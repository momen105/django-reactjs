from django.views import generic
from product.models import Variant, Product, ProductVariant
from product.forms import ProductForm
from django.db.models import Prefetch


class CreateProductView(generic.TemplateView):
    template_name = "products/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values("id", "title")
        context["product"] = True
        context["variants"] = list(variants.all())
        return context


class BaseProductView(generic.View):
    form_class = ProductForm
    model = Product
    template_name = "products/create.html"
    success_url = "/product/list"


class ListProductView(BaseProductView, generic.ListView):
    template_name = "products/list.html"
    paginate_by = 2

    def get_queryset(self):
        filter_string = {}
        product_title = self.request.GET.get("title", "")
        product_variant = self.request.GET.get("variant", "")
        price_from = self.request.GET.get("price_from", "")
        price_to = self.request.GET.get("price_to", "")
        date = self.request.GET.get("date", "")

        if product_title:
            filter_string["title__icontains"] = product_title

        if product_variant:
            filter_string["productvariant__variant_title__icontains"] = product_variant

        if date:
            filter_string["created_at__date"] = date

        if price_from and price_to:
            filter_string["product_variant_price__price__range"] = (
                price_from,
                price_to,
            )
        queryset = Product.objects.filter(**filter_string)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = True
        context["request"] = ""

        # Get the current page and number of items per page
        page = self.request.GET.get("page", 1)
        per_page = self.paginate_by

        # Calculate the starting and ending item numbers
        start_item = (int(page) - 1) * per_page + 1
        end_item = start_item + per_page - 1
        total_items = self.get_queryset().count()

        # Adjust the end_item if it exceeds the total number of items
        end_item = min(end_item, total_items)

        context["start_item"] = start_item
        context["end_item"] = end_item
        context["total_items"] = total_items

        unique_variant_title = []
        product_variant_list = []
        variants = Variant.objects.filter(active=True)
        for i in variants:
            variant = {"title": i.title, "product_variant": []}
            for pv in i.ProductVariant_variant.all():
                if pv.variant_title not in unique_variant_title:
                    unique_variant_title.append(pv.variant_title)
                    variant["product_variant"].append(pv.variant_title)
            product_variant_list.append(variant)
        context["variants"] = product_variant_list
        return context
