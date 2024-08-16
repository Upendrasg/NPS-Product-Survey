from django.contrib import admin
from .models import (
    Order,
    OrderItem,
    NPSSurveyCustomer,
    NPSSurveyPrimaryResponse,
    NPSSurveyQuestionResponse,
    NPSSurveyQuestionnaire,
    NPSSurveyQuestions,
)

# Register your models here.


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ["order_id", "customer_id", "customer_mobile", "delivery_time"]


@admin.register(OrderItem)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = ["order_id", "product_category"]


@admin.register(NPSSurveyCustomer)
class NPSSurveyCustomerModelAdmin(admin.ModelAdmin):
    list_display = [
        "nps_survey_id",
        "customer_id",
        "customer_mobile",
        "product_category",
        "sent_date",
        "survey_id",
        "order_id",
        "utm_parameter",
        "survey_filled",
    ]


@admin.register(NPSSurveyQuestionnaire)
class NPSSurveyQuestionnaireModelAdmin(admin.ModelAdmin):
    list_display = ["survey_id", "product_category"]


@admin.register(NPSSurveyPrimaryResponse)
class NPSSurveyPrimaryResponseModelAdmin(admin.ModelAdmin):
    list_display = [
        "nps_survey_id",
        "customer_id",
        "age",
        "gender",
        "survey_filled_date",
    ]


@admin.register(NPSSurveyQuestionResponse)
class NPSSurveyQuestionResponseModelAdmin(admin.ModelAdmin):
    list_display = ["customer_id", "nps_survey_id", "question_id", "response"]

    def customer_id(self, request):
        nps_primary_res = NPSSurveyPrimaryResponse.objects.filter(
            nps_survey_id=request.nps_survey_id
        )
        if nps_primary_res:
            return nps_primary_res.first().customer_id


@admin.register(NPSSurveyQuestions)
class NPSSurveyQuestionResponseModelAdmin(admin.ModelAdmin):
    list_display = ["question_description", "survey_id", "question_id"]
