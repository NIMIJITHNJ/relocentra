from django.shortcuts import render
from estimator.forms import AssignmentCostForm, AccommodationAssessmentForm
from estimator.services.cost_estimate import estimate_assignment
from estimator.sources import SOURCE_GROUPS, SECTION_SOURCES

# Display the assignment form and calculate the two-year cost
def assignment_view(request):
    result = None
    
    # Prepare separate accommodation forms for both assignment years
    housing_mode = (
        request.method == "POST"
        and request.POST.get("housing_mode") == "assessed"
    )

    if housing_mode:
        housing_form1 = AccommodationAssessmentForm(
            request.POST, prefix="housing1"
        )
        housing_form2 = AccommodationAssessmentForm(
            request.POST, prefix="housing2"
        )
    else:
        housing_form1 = AccommodationAssessmentForm(prefix="housing1")
        housing_form2 = AccommodationAssessmentForm(prefix="housing2")
    
    if request.method == "POST":
        form = AssignmentCostForm(request.POST)

        main_valid = form.is_valid()
        housing_valid = True

        if housing_mode:
            year1_valid = housing_form1.is_valid()
            year2_valid = housing_form2.is_valid()

            housing_valid = year1_valid and year2_valid
        
        if main_valid and housing_valid:
            try:
                inputs = form.cleaned_data.copy()

                if housing_mode:
                    inputs["housing_data1"] = housing_form1.housing_data()
                    inputs["housing_data2"] = housing_form2.housing_data()

                result = estimate_assignment(**inputs)

            except ValueError as error:
                form.add_error(None, str(error))

    else:
        form = AssignmentCostForm()
    
    return render(
        request,
        "estimator/assignment.html",        
        {
            "form": form,
            "result": result,
            "housing_form1": housing_form1,
            "housing_form2": housing_form2,
            "housing_mode": housing_mode,
            "source_groups": SOURCE_GROUPS,
            "section_sources": SECTION_SOURCES
        }
    )