from django.shortcuts import render
from django.views import View

# Create your views here.
class AdminDashboard(View):
    def get(self, request):
        return render(request, "AdminDashboard.html")
    def post(self):
        pass
