from django.shortcuts import render
from .forms import ImmigrationForm
from .services.assessment import assess_immigration


# Process and display the immigration assessment
def immigration_view(request):
    result = None

    if request.method == "POST":
        form = ImmigrationForm(request.POST)

        if form.is_valid():
            try:
                result = assess_immigration(form.cleaned_data)
            except ValueError as error:
                form.add_error(None, str(error))
    else:
        form = ImmigrationForm()

    return render(request, "immigration/index.html", {
        "form": form,
        "result": result,
    })
