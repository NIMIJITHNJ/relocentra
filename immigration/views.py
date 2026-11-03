from django.shortcuts import render

# Display the immigration assessment page
def immigration_view(request):
    return render(request, "immigration/index.html")

