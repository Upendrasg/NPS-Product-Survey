from django.urls import path
from .views import send_surveys, receive_survey_response

urlpatterns = [
    path("send_surveys/", send_surveys, name="send_surveys"),
    path(
        "receive_survey_response/",
        receive_survey_response,
        name="receive_survey_response",
    ),
]
