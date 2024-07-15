from django.shortcuts import render

# Create your views here.
def index(request):
        context = {"info":"Hello world"}
        return render(request, "games/index.html", context)

