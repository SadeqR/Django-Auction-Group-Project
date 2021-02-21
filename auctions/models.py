from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from datetime import datetime, timedelta
from PIL import Image
import pytz
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
CONDITION_CHOICES = [
    ('New', 'New'),
    ('Used', 'Used'),
    ('Brand New', 'Brand New'),
    ('Like New', 'Like New'),
    ('Very Good', 'Very Good'),
    ('New with tags', 'New with tags'),
    ('New without tags', 'New without tags'),
    ('New with defects', 'New with defects'),
    ('For parts or not working', 'For parts or not working'),
    ('Seller refurbished', 'Seller refurbished'),
]

class Auction(models.Model):
    title = models.CharField(max_length=255)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, default='New')
    description = models.TextField()
    image = models.ImageField(default='default.jpg', upload_to='images_auctions')
    date_created = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_expired = models.DateTimeField(default=datetime.now()+timedelta(days=7))
    # Variables to save having to traverse through all bids etc here
    price = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    amount_of_bids = models.IntegerField(default=0)
    closed = models.BooleanField(default=False)
    winnerBid = models.ForeignKey('Bid', blank=True, null=True, on_delete=models.CASCADE, related_name='winner')


    @property
    def expired(self):
        expiry = self.date_expired.replace(tzinfo=None)
        now = timezone.now().replace(tzinfo=None)
        if now > expiry:
            return True
        return False

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auction-detail', kwargs={'pk' : self.pk})

    #override save method
    def save(self, *args, **kwargs):
        # call parent save method
        super(Auction, self).save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class Bid(models.Model):
    price = models.IntegerField(default=1)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    winningBid = models.BooleanField(default=False)

class Comment(models.Model):
	auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	message = models.TextField()
	date_created = models.DateTimeField()
