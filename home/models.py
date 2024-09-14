from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import random
from django.utils import timezone
from datetime import timedelta

# class Container(models.Model):
#     container_name= models.CharField(max_length=50)
#     length = models.FloatField()
#     width = models.FloatField()
#     height = models.FloatField()
#     max_weight = models.FloatField()


#     def __str__(self):
#         return self.container_name



class Company(models.Model):
    company_name = models.CharField(max_length=50, primary_key=True)
    company_code = models.CharField(max_length=10, unique=True)

    plan_choices = [
        ('A', 'PlanA'),
        ('B', 'PlanB'),
        ('C', 'PlanC')
    ]
    access_roles_choices = [
        ('L', 'Loader'),
        ('P', 'Planner'),
        ('H', 'Leadership')
    ]
    container_type_choices = [
        ('Gen20F', 'General 20 ft container'),
        ('Gen40F', 'General 40 ft container'),
        ('High40F', 'HighCube 40 ft container'),
        # Add other choices here
    ]
    standard_source_choices=[

    ]
    standard_destination_choices=[

    ]

    SKUs = models.ManyToManyField('SKU', related_name='companies_as_SKU')
    plan = models.CharField(max_length=1, choices=plan_choices)
    access_roles = models.CharField(max_length=1, choices=access_roles_choices)
    standard_container_type = models.CharField(max_length=20, choices=container_type_choices)
    # choice_of_container = models.cha
    standard_source = models.CharField(max_length=100, choices=standard_source_choices)
    standard_destination = models.CharField(max_length=100,choices=standard_destination_choices)
    user_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.user_count > 100:
            return JsonResponse({"ERROR": "Users limit exceeded"}, status=404)
            raise ValidationError("user_count cannot exceed 2.")
        if not self.company_code:
            self.company_code = self.generate_unique_code()
        super(Company, self).save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = f'{random.randint(1000, 9999)}'  # Generate a random 4-digit number
            if not Company.objects.filter(company_code=code).exists():
                return code

    def __str__(self):
        return self.company_name


class SKU(models.Model):
    sku_code = models.CharField(max_length=50, unique=True,primary_key=True)
    sku_name = models.CharField(max_length=50, unique=True)
    sku_description = models.TextField()
    type_choices=[
        ('A','A'),
        ('B','B')
    ]
    sku_type = models.CharField(max_length=1,choices=type_choices)
    gross_weight = models.FloatField()
    net_weight = models.FloatField()
    volume = models.FloatField()
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    #  What is product hierarchy
    product_hierarchy =models.TextField()
    incompatibility = models.CharField(max_length=100)
    max_stack_height = models.IntegerField()  #number of boxes that can be accomodated , think about the default put it as the container heights


    def __str__(self):
        return self.sku_code


class Users(models.Model):
    user_id = models.CharField(max_length=10, primary_key=True, default='000000')
    email_id = models.EmailField(max_length=254)
    password = models.CharField(max_length=128)  # Field to store hashed passwords

    user_type_choices = [
        ('SuperAdmin', 'SuperAdmin'),
        ('Admin', 'Admin'),
        ('OptipackTeam', 'OptipackTeam'),
        ('Company_SuperAdmin', 'Company_SuperAdmin'),
        ('Company_Admin', 'Company_Admin'),
        ('Company_loader', 'Company_loader'),
        ('Company_planner', 'Company_planner')
    ]
    status_choices=[
        ('Exp','expired'),
        ('Active','Active'),
        ('Dormant','Dormant')
        # Others after discussing 
    ]
    user_type = models.CharField(max_length=20, choices=user_type_choices)
    user_first_name = models.CharField(max_length=100)
    user_last_name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', default='0000')
    user_status = models.CharField(max_length=100,choices= status_choices)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_authenticated =models.BooleanField(default=False)

    class Meta:
        unique_together = ('user_id', 'email_id')  # Ensures the combination of user_id and email_id is unique

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.user_id} - {self.email_id}"

class Container(models.Model):
    container_id = models.CharField(max_length=20,primary_key=True)  ## Put a unique random geenarator
    container_name = models.CharField(max_length=50)
    container_volume = models.FloatField()
    container_length = models.FloatField()
    container_width = models.FloatField()
    container_height = models.FloatField()
    payload_capacity= models.FloatField()
    container_type_choices = [
        ('A','A'),
        ('B','B')
    ]
    container_type = models.CharField(max_length=100,choices= container_type_choices)
    volume_capacity= models.FloatField()
    seperator_pallet = models.BooleanField(default=False)
    door_opening_width = models.FloatField()
    door_opening_length=models.FloatField()
    cubic_capacity = models.FloatField()
    tare_weight =models.FloatField()
    max_gross_weight =models.FloatField()

    def __str__(self):
        return self.container_id

class Order(models.Model):
    order_id = models.CharField(max_length=20, primary_key=True, unique=True)
    skus = models.ManyToManyField(SKU, through='OrderSKU', related_name='orders')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    container = models.ManyToManyField(Container, related_name='orders')
    product_hierarchy = models.CharField(max_length=100)
    source_location = models.CharField(max_length=100)
    shipping_point = models.CharField(max_length=100)
    destination_location = models.CharField(max_length=100)
    destination_point = models.CharField(max_length=100)
    planned_start_date = models.DateField()
    planned_delivery_date = models.DateField()




    def __str__(self):
        return self.order_id

class OrderSKU(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.order.order_id} - {self.sku.sku_code}: {self.quantity}"

class LoadPlan(models.Model):
    plan_id = models.CharField(max_length=20, primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='load_plan')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='load_plan')
    utilization = models.FloatField()
    volume_untilized = models.FloatField()
    volume_available = models.FloatField()
    orderSKU = models.ManyToManyField(OrderSKU, related_name='load_plan')
    load_details = models.TextField()
    unplanned_load = models.TextField()
    image_top = models.ImageField(upload_to='top_images')
    image_bottom = models.ImageField(upload_to='bottom_images')
    image_left = models.ImageField(upload_to='left_images')
    image_right = models.ImageField(upload_to='right_images')

    def __str__(self):
        return self.plan_id
    
    def get_sku_details(self):
        sku_details = []
        for order_sku in self.orderSKU.all():
            detail = {
                "order_id": order_sku.order.order_id,
                "sku_code": order_sku.sku.sku_code,
                "quantity": order_sku.quantity
            }
            sku_details.append(detail)
        return sku_details

class OTPRegistration(models.Model):
    email_id = models.EmailField(max_length=255, unique=True)  # Store the user's email
    otp = models.CharField(max_length=6)  # Store the OTP
    isVerified = models.BooleanField(default=False)  # To check if the OTP is verified
    otp_sent_time = models.DateTimeField(default=timezone.now)  # Time when OTP was sent
    expired = models.BooleanField(default=False)  # To track if the OTP is expired

    def save(self, *args, **kwargs):
        # Automatically set expired flag if OTP is older than 15 minutes
        if timezone.now() > self.otp_sent_time + timedelta(minutes=15):
            self.expired = True
        super(OTPRegistration, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.email_id} - OTP: {self.otp} - Verified: {self.isVerified} - Expired: {self.expired}"




