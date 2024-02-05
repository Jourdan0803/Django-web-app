from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(verbose_name='username', max_length=32, unique=True)
    password = models.CharField(verbose_name='password', max_length=64)
    email = models.CharField(verbose_name='email', max_length=32)

    is_driver = models.IntegerField(verbose_name='driver status', default= 0) # 0->not dirver, 1->driver

    # vehicle_choices = (
    #     (0, "car"),
    #     (1, "van"),
    #     (2, "bus"),
    #     (3, "big bus"),
    # )
    # vehicle_type = models.IntegerField(verbose_name='vehicle type', choices=vehicle_choices, default=0)
    vehicle_type = models.TextField(verbose_name='vehicle type', default="")
    driver_license = models.IntegerField(verbose_name='driver license', default=00000000)
    seats_num = models.IntegerField(verbose_name='maximum number of passengers', default=0)
    special_info = models.TextField(verbose_name='special vehicle info', default = "")
    # age = models.IntegerField()
    # UserInfo.objects.filter(username = "jourdan").delete()
    # UserInfo.objects.create(username = "admin")
    # datalist = UserInfo.object.all()
    # print(datalist)

class OrderInfo(models.Model):
    order_owner = models.CharField(verbose_name='order owner name', max_length=32)
    # order_owner = models.ForeignKey(verbose_name='order owner name', to='UserInfo', to_field='username', null=True, blank=True, on_delete=models.SET_NULL)
    owner_num = models.IntegerField(verbose_name='number of total passengers')
    
    location = models.CharField(verbose_name='location', max_length=256)
    destination = models.CharField(verbose_name='destination', max_length=256)

    date = models.TextField(verbose_name='date') # MM/DD/YYYY
    time = models.TextField(verbose_name='time') # xx:xx
    time_earlist = models.TextField(verbose_name='earliest acceptable arrival time')
    time_latest = models.TextField(verbose_name='latest acceptable arrival time')

    driver = models.CharField(verbose_name='driver name', max_length=32, null=True, blank=True)
    # dirver = models.ForeignKey(verbose_name='driver name', to='UserInfo', to_field='username', null=True, blank=True, on_delete=models.SET_NULL)
    # vehicle_choices = (
    #     (0, "car"),
    #     (1, "van"),
    #     (2, "bus"),
    #     (3, "big bus"),
    #     (4, "default")
    # )
    # vehicle_type = models.SmallIntegerField(verbose_name='vehicle type', choices=vehicle_choices, default=4)
    vehicle_type = models.TextField(verbose_name='vehicle type', default="")
    seats_num = models.IntegerField(verbose_name='number of seats in vehicle', default=0)
    
    is_share = models.BooleanField(verbose_name='whether to share', default = False)
    share_user = models.CharField(verbose_name='share user name', max_length=32,null=True, blank=True)
    share_num = models.IntegerField(verbose_name='shared number of total passengers', null=True, blank=True)

    is_confirm = models.BooleanField(verbose_name='whether has been confirmed', default=False)
    status = models.CharField(verbose_name='ride status', default="open") # open, confirmed, complete
    info = models.TextField(verbose_name='special vehicle info', null=True, blank=True, default="None")