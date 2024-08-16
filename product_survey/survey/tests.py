from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem, NPSSurveyCustomer, NPSSurveyPrimaryResponse
from django.urls import reverse
import json


class NPSSurveyTestCase(TestCase):

    def setUp(self):
        # Set up test data

        # Create some orders
        self.order1 = Order.objects.create(
            order_id=1,
            customer_id=101,
            customer_mobile="1234567890",
            delivery_time=timezone.now() - timedelta(days=30),
        )

        self.order2 = Order.objects.create(
            order_id=2,
            customer_id=102,
            customer_mobile="0987654321",
            delivery_time=timezone.now() - timedelta(days=30),
        )

        # Create order items for those orders
        OrderItem.objects.create(order_id=self.order1, product_category="lepa")
        OrderItem.objects.create(
            order_id=self.order2, product_category="Netraa"
        )  # Should be excluded

        # Create a previous survey entry to test exclusion
        NPSSurveyCustomer.objects.create(
            customer_id=101,
            customer_mobile="1234567890",
            sent_date=timezone.now() - timedelta(days=100),
            product_category="lepa",
            survey_id=1,
            order_id=1,
            utm_parameter="utm=101",
            survey_filled=True,
        )

    def test_survey_eligibility_logic(self):
        # Test if the right orders are selected for survey
        response = self.client.get(reverse("send_surveys"))

        # Check if the response is a valid CSV
        self.assertEqual(response.status_code, 200)
        self.assertIn("lepa", response.content.decode("utf-8"))

        # Ensure 'Netraa' category was excluded
        self.assertNotIn("Netraa", response.content.decode("utf-8"))

    def test_survey_version_selection(self):
        # Verify the correct version of the survey is selected
        response = self.client.get(reverse("send_surveys"))
        content = response.content.decode("utf-8")

        # If a V1 survey has been filled before, V2 should be sent next
        self.assertIn("V2", content)

    def test_receive_survey_response(self):
        # Test the API that receives survey responses

        # Mock survey response data
        survey_response_data = {
            "event_id": "01J58GMMHQN5VR11NF5879YJ85",
            "event_type": "form_response",
            "form_response": {
                "form_id": "RVcdBbTG",
                "token": "dhgazi98vd7jd33dhgaz0wlk06oqsjpo",
                "landed_at": "2024-08-14T13:18:17Z",
                "submitted_at": "2024-08-14T13:18:36Z",
                "hidden": {"customer_id": "8", "product_category": "Tikta"},
                "definition": {
                    "id": "RVcdBbTG",
                    "title": "Survey - V1",
                    "fields": [
                        {
                            "id": "1q9jwqqMvbvP",
                            "ref": "a618176f-502d-409a-a14b-58ecf80583a6",
                            "type": "opinion_scale",
                            "title": "Rate the brand on the below scale.",
                            "properties": {},
                        },
                        {
                            "id": "KW2jgYqWNMCG",
                            "ref": "28bbc0f3-6eee-43e0-85dd-5db8f609a254",
                            "type": "opinion_scale",
                            "title": "Rate the product on the below scale.",
                            "properties": {},
                        },
                        {
                            "id": "OculzI47RCHJ",
                            "ref": "ab4eda13-e499-4afb-9397-2dadf65999af",
                            "type": "long_text",
                            "title": "Share what you like or dislike about the brand.",
                            "properties": {},
                        },
                        {
                            "id": "AYd3C9b0fXiJ",
                            "ref": "906e7086-e6f6-4d79-8719-d756063fde2b",
                            "type": "multiple_choice",
                            "title": "What is your gender?",
                            "properties": {},
                            "choices": [
                                {
                                    "id": "40zC7jOTNJAo",
                                    "ref": "7a0b60d2-c7a8-4b79-9613-ba27b3044649",
                                    "label": "Male",
                                },
                                {
                                    "id": "d94V2E8owXo6",
                                    "ref": "983158d6-350d-4099-856e-5b09bc4dac60",
                                    "label": "Female",
                                },
                                {
                                    "id": "ctRjJMGeY9jT",
                                    "ref": "18d5d658-f2a6-4ac6-a1d3-71f2f87c33ed",
                                    "label": "Non-Binary",
                                },
                                {
                                    "id": "DAIrMAVD3xDD",
                                    "ref": "e38fd602-3459-481f-9dc1-a82e9eb839ae",
                                    "label": "Prefer not to say",
                                },
                            ],
                        },
                        {
                            "id": "r7TMRukeAETP",
                            "ref": "e8574d17-c567-4099-ab5c-299974137965",
                            "type": "dropdown",
                            "title": "What is your age group?",
                            "properties": {},
                            "choices": [
                                {
                                    "id": "AhlTH1iAqnZS",
                                    "ref": "570f7c6f-44be-47e6-977f-4e463f10c810",
                                    "label": "Under 18",
                                },
                                {
                                    "id": "wZetnz9UOC8B",
                                    "ref": "1d8c49f8-3f38-474f-a881-82f930db3df1",
                                    "label": "18-24",
                                },
                                {
                                    "id": "B9M7vOq3uV71",
                                    "ref": "f7f77475-82e9-43bb-831b-4859f36d76bb",
                                    "label": "25-34",
                                },
                                {
                                    "id": "22yvRT0dJwgR",
                                    "ref": "187ccb3e-b191-474c-af16-25d24df0794b",
                                    "label": "35-44",
                                },
                                {
                                    "id": "CX63lw2UUHHT",
                                    "ref": "70e0e596-244b-4c99-8ad8-04b225ae79af",
                                    "label": "45-54",
                                },
                                {
                                    "id": "lTVLQWUWlp6a",
                                    "ref": "cb818a0e-b44e-43f9-98a9-160ac1afcc90",
                                    "label": "55-64",
                                },
                                {
                                    "id": "spJ8P8e5N21B",
                                    "ref": "40255298-ea45-4ec7-a650-99dc60fc9e53",
                                    "label": "65+",
                                },
                            ],
                        },
                        {
                            "id": "CMCdKUnCoByY",
                            "ref": "9d2a9878-699a-4aca-a0eb-b4a36539e06b",
                            "type": "dropdown",
                            "title": "What is your skin type?",
                            "properties": {},
                            "choices": [
                                {
                                    "id": "Hp111VKHRKLW",
                                    "ref": "20a74b21-3cfb-4b09-adf2-c3d7a76207d8",
                                    "label": "Dry",
                                },
                                {
                                    "id": "cfmTEpi50aBA",
                                    "ref": "6857cb0c-801a-4f63-8cef-4c74d80f62a9",
                                    "label": "Oily",
                                },
                                {
                                    "id": "dyxQDYdPhvQ4",
                                    "ref": "ccb2bc47-b8fb-480d-8267-69e8a79a38b2",
                                    "label": "Combination",
                                },
                                {
                                    "id": "nbMXo4GyW6we",
                                    "ref": "1560ebd6-e701-4507-acc8-568a023ff770",
                                    "label": "Sensitive",
                                },
                                {
                                    "id": "dfpDLO8EJAma",
                                    "ref": "db83090a-cca6-4931-9fbb-c5b316f32ec9",
                                    "label": "Normal",
                                },
                                {
                                    "id": "3pIuqbZCxrxG",
                                    "ref": "3b4ba684-b57a-43e6-86f2-ccf69a09aa96",
                                    "label": "Other",
                                },
                            ],
                        },
                        {
                            "id": "jrGb2aRggV32",
                            "ref": "9ab1dc71-1db6-49ed-bf07-73afb7ae8cb3",
                            "type": "dropdown",
                            "title": "What is your hair type?",
                            "properties": {},
                            "choices": [
                                {
                                    "id": "kasJSUSzNS8v",
                                    "ref": "537bb548-f18e-41f5-a706-e7c451e7b24a",
                                    "label": "Straight",
                                },
                                {
                                    "id": "clTNZBSHMWFZ",
                                    "ref": "1a77f771-9860-4bd0-bfa2-a857d786f516",
                                    "label": "Wavy",
                                },
                                {
                                    "id": "WJDXRM6Q9xpM",
                                    "ref": "dea92f1f-446d-46d3-93c2-20a2394a6c23",
                                    "label": "Curly",
                                },
                                {
                                    "id": "AiiF41Bo2xC0",
                                    "ref": "9507d58d-35f3-43f7-8167-e9476e8c6c4d",
                                    "label": "Coily",
                                },
                                {
                                    "id": "QzXvz6rChtk0",
                                    "ref": "0b4b6f95-344f-4881-952d-0934d6a84a9a",
                                    "label": "Bald",
                                },
                                {
                                    "id": "kYKBNaRmk5jz",
                                    "ref": "d788989a-c00a-474a-ab90-9583a6f01fe7",
                                    "label": "Other",
                                },
                            ],
                        },
                    ],
                    "endings": [
                        {
                            "id": "DefaultTyScreen",
                            "ref": "default_tys",
                            "title": "Thanks for completing this typeform\nNow *create your own* — it's free, easy, & beautiful",
                            "type": "thankyou_screen",
                            "properties": {
                                "button_text": "Create a *typeform*",
                                "show_button": True,
                                "share_icons": False,
                                "button_mode": "default_redirect",
                            },
                            "attachment": {
                                "type": "image",
                                "href": "https://images.typeform.com/images/2dpnUBBkz2VN",
                            },
                        }
                    ],
                },
                "answers": [
                    {
                        "type": "number",
                        "number": 10,
                        "field": {
                            "id": "1q9jwqqMvbvP",
                            "type": "opinion_scale",
                            "ref": "a618176f-502d-409a-a14b-58ecf80583a6",
                        },
                    },
                    {
                        "type": "number",
                        "number": 10,
                        "field": {
                            "id": "KW2jgYqWNMCG",
                            "type": "opinion_scale",
                            "ref": "28bbc0f3-6eee-43e0-85dd-5db8f609a254",
                        },
                    },
                    {
                        "type": "text",
                        "text": "dffs",
                        "field": {
                            "id": "OculzI47RCHJ",
                            "type": "long_text",
                            "ref": "ab4eda13-e499-4afb-9397-2dadf65999af",
                        },
                    },
                    {
                        "type": "choice",
                        "choice": {
                            "id": "d94V2E8owXo6",
                            "label": "Female",
                            "ref": "983158d6-350d-4099-856e-5b09bc4dac60",
                        },
                        "field": {
                            "id": "AYd3C9b0fXiJ",
                            "type": "multiple_choice",
                            "ref": "906e7086-e6f6-4d79-8719-d756063fde2b",
                        },
                    },
                    {
                        "type": "choice",
                        "choice": {
                            "id": "wZetnz9UOC8B",
                            "label": "18-24",
                            "ref": "1d8c49f8-3f38-474f-a881-82f930db3df1",
                        },
                        "field": {
                            "id": "r7TMRukeAETP",
                            "type": "dropdown",
                            "ref": "e8574d17-c567-4099-ab5c-299974137965",
                        },
                    },
                    {
                        "type": "choice",
                        "choice": {
                            "id": "dyxQDYdPhvQ4",
                            "label": "Combination",
                            "ref": "ccb2bc47-b8fb-480d-8267-69e8a79a38b2",
                        },
                        "field": {
                            "id": "CMCdKUnCoByY",
                            "type": "dropdown",
                            "ref": "9d2a9878-699a-4aca-a0eb-b4a36539e06b",
                        },
                    },
                    {
                        "type": "choice",
                        "choice": {
                            "id": "WJDXRM6Q9xpM",
                            "label": "Curly",
                            "ref": "dea92f1f-446d-46d3-93c2-20a2394a6c23",
                        },
                        "field": {
                            "id": "jrGb2aRggV32",
                            "type": "dropdown",
                            "ref": "9ab1dc71-1db6-49ed-bf07-73afb7ae8cb3",
                        },
                    },
                ],
                "ending": {"id": "DefaultTyScreen", "ref": "default_tys"},
            },
        }

        # Send the data to the API
        response = self.client.post(
            reverse("receive_survey_response"),
            data=json.dumps(survey_response_data),
            content_type="application/json",
        )

        # Check if the API returned a success status
        self.assertEqual(response.status_code, 200)

        # Verify the response was recorded in the database
        primary_response = NPSSurveyPrimaryResponse.objects.get(
            nps_survey_id="01J58GMMHQN5VR11NF5879YJ85"
        )
        self.assertEqual(primary_response.age, "18-24")
        self.assertEqual(primary_response.gender, "Female")

    def test_exclude_customers_based_on_survey_fill_rate(self):
        # Test exclusion of customers who haven't filled the last 3 consecutive surveys
        NPSSurveyCustomer.objects.create(
            customer_id=102,
            customer_mobile="0987654321",
            sent_date=timezone.now() - timedelta(days=90),
            product_category="ubtan",
            survey_id=2,
            order_id=2,
            utm_parameter="utm=102",
            survey_filled=False,
        )

        response = self.client.get(reverse("send_surveys"))
        content = response.content.decode("utf-8")

        # Customer 102 should be excluded because they haven't filled the last 3 surveys
        self.assertNotIn("ubtan", content)
