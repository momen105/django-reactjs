from django.views import generic
from product.models import Variant, Product
from product.forms import ProductForm


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
        print(self.request.GET)
        for key in self.request.GET:
            if self.request.GET.get(key):
                filter_string[key] = self.request.GET.get(key)
        return Product.objects.filter(**filter_string)

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

        if self.request.GET:
            context["request"] = self.request.GET["title__icontains"]
        return context
