import csv
from django.http import HttpResponse
from django.utils import timezone
from .models import (
    Order,
    OrderItem,
    NPSSurveyCustomer,
    NPSSurveyPrimaryResponse,
    NPSSurveyQuestionResponse,
)
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


def send_surveys(request):
    current_date = timezone.now().date()
    # Get the current date and calculate the target date (30 days before)
    DAY_BEFORE_30 = current_date - timedelta(days=30)
    # Get the current date and calculate the target date (90 days before)
    DAY_BEFORE_90 = current_date - timedelta(days=90)

    survey_id = 1
    form_id = "RVcdBbTG"
    survey_type = "V1"

    # Filter eligible customers
    eligible_orders = Order.objects.filter(delivery_time__date=DAY_BEFORE_30)
    customers = []

    for order in eligible_orders:
        customer_id = order.customer_id
        order_items = OrderItem.objects.filter(order_id=order.order_id)

        # Segmentation logic
        product_categories = [item.product_category for item in order_items]
        if any(pc in ["Netraa", "Conditioner"] for pc in product_categories):
            continue

        # Customers should not receive two surveys back to back in a span of 90 days
        if NPSSurveyCustomer.objects.filter(
            customer_id=customer_id, sent_date__gte=DAY_BEFORE_90
        ):
            continue

        # Customer has not filled 3 consecutive surveys in a row customer is to be omitted
        if (
            NPSSurveyCustomer.objects.filter(
                customer_id=customer_id, survey_filled=False
            )
            .order_by("sent_date")
            .count()
            >= 3
        ):
            continue

        # Add logic to determine survey version (V1 or V2)
        if NPSSurveyCustomer.objects.filter(
            customer_id=customer_id, survey_id=survey_id
        ):
            survey_id = 2
            form_id = "bXFb9h7f"
            survey_type = "V2"

        # Select a product category to send the survey
        for selected_product_category in product_categories:
            # Record the customer in the NPSSurveyCustomer table
            nps_survey_customer = NPSSurveyCustomer.objects.create(
                customer_id=customer_id,
                customer_mobile=order.customer_mobile,
                sent_date=timezone.now(),
                product_category=selected_product_category,
                survey_id=survey_id,  # survey_id=1 Means V1 and survey_id=1 Means V2
                order_id=order.order_id,
                utm_parameter=f"utm={customer_id}",
            )
            nps_survey_id = nps_survey_customer.nps_survey_id

            survey_link = f"https://nathabit.typeform.com/to/{form_id}#customer_id={customer_id}&product_category={selected_product_category}&nps_survey_id={nps_survey_id}"
            # https://nathabit.typeform.com/to/RVcdBbTG#customer_id=xxxxx&product_category=xxxxx&nps_survey_id=xxxxx

            # Collect data for the CSV
            customers.append(
                {
                    "order_id": order.order_id,
                    "customer_id": customer_id,
                    "customer_phone": order.customer_mobile,
                    "product_category": selected_product_category,
                    "survey_type": survey_type,
                    "survey_link": survey_link,
                }
            )

    # Create CSV
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="survey_customers.csv"'

    writer = csv.DictWriter(
        response,
        fieldnames=[
            "order_id",
            "customer_id",
            "customer_phone",
            "product_category",
            "survey_type",
            "survey_link",
        ],
    )
    writer.writeheader()
    for customer in customers:
        writer.writerow(customer)

    return response


@csrf_exempt
def receive_survey_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        response_data = {}
        age = None
        gender = None
        # nps_survey_id = data.get('event_id')
        form_responses = data.get("form_response")
        form_id = form_responses.get("form_id")
        customer_id = form_responses.get("hidden").get("customer_id")
        product_category = form_responses.get("hidden").get("product_category")
        nps_survey_id = form_responses.get("hidden").get("nps_survey_id")

        for response in form_responses.get("answers"):
            response_data[response.get("field").get("id")] = response.get(
                response.get("type")
            )

        responses = form_responses.get("answers", [])
        if form_id == "RVcdBbTG":
            age = response_data.get("r7TMRukeAETP").get("label")
            gender = response_data.get("AYd3C9b0fXiJ").get("label")
            survey_id = 1
        else:
            survey_id = 2

        # Save primary response
        NPSSurveyPrimaryResponse.objects.create(
            nps_survey_id=nps_survey_id,
            customer_id=customer_id,
            age=age,
            gender=gender,
            survey_filled_date=timezone.now(),
        )

        # Save question responses
        for response in responses:
            type = response.get("type")
            if type in ["number", "text"]:
                answer = response.get(type)
            if type == "choice" and form_id == "RVcdBbTG":
                answer = response.get(type).get("label")

            question_id = response.get("field").get("id")
            NPSSurveyQuestionResponse.objects.create(
                nps_survey_id=nps_survey_id, question_id=question_id, response=answer
            )
        # Record if the customer filled the survery form or not.
        nps_survey_customer = NPSSurveyCustomer.objects.filter(
            customer_id=customer_id,
            survey_id=survey_id,
            product_category=product_category,
        ).order_by("sent_date")

        if nps_survey_customer:
            obj = nps_survey_customer.first()
            obj.survey_filled = True
            obj.save()

        return JsonResponse({"status": "success"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)
