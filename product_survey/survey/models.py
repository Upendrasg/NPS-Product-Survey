from django.db import models


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    customer_id = models.IntegerField()
    customer_mobile = models.CharField(max_length=15)
    delivery_time = models.DateTimeField()

    def __str__(self) -> str:
        return f'{self.order_id} - {self.delivery_time.date().strftime("%b %d %Y")}'


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_category = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.order_id}-{self.product_category}"


class NPSSurveyCustomer(models.Model):
    nps_survey_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField()
    customer_mobile = models.CharField(max_length=15)
    sent_date = models.DateTimeField()
    product_category = models.CharField(max_length=100)
    survey_id = models.IntegerField()
    order_id = models.IntegerField()
    utm_parameter = models.CharField(max_length=100)
    survey_filled = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.customer_id}-{self.survey_id}-{self.product_category}"


class NPSSurveyPrimaryResponse(models.Model):
    nps_survey_id = models.CharField(primary_key=True, max_length=50)
    customer_id = models.IntegerField()
    age = models.CharField(null=True, max_length=50)
    gender = models.CharField(max_length=10, null=True)
    survey_filled_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.customer_id} - {self.nps_survey_id}"


class NPSSurveyQuestionnaire(models.Model):
    survey_id = models.IntegerField(primary_key=True)
    product_category = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.survey_id}-{self.product_category}"


class NPSSurveyQuestions(models.Model):
    survey_id = models.IntegerField()
    question_id = models.CharField(max_length=50)
    question_description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.survey_id}-{self.question_id}-{self.question_description}"


class NPSSurveyQuestionResponse(models.Model):
    nps_survey_id = models.CharField(max_length=50)
    question_id = models.CharField(max_length=50)
    response = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.nps_survey_id}-{self.question_id}-{self.response}"
