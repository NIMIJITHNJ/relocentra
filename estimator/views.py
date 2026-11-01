from django.shortcuts import render
from estimator.forms import AssignmentCostForm
from estimator.services.cost_estimate import estimate_assignment

# Display the assignment form and calculate the two-year cost
def assignment_view(request):
    result = None

    if request.method == "POST":
        form = AssignmentCostForm(request.POST)

        if form.is_valid():
            result = estimate_assignment(**form.cleaned_data)
    else:
        form = AssignmentCostForm()

    return render(
        request,
        "estimator/assignment.html",
        {
            "form": form,
            "result": result
        }
    )
