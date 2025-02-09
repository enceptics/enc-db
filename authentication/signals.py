from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Review)
def update_place_rating_on_save(sender, instance, **kwargs):
    place = instance.place
    reviews = place.reviews.all()
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
    place.average_rating = round(average_rating, 2)
    place.total_reviews = total_reviews
    place.save()

@receiver(post_delete, sender=Review)
def update_place_rating_on_delete(sender, instance, **kwargs):
    place = instance.place
    reviews = place.reviews.all()
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
    place.average_rating = round(average_rating, 2)
    place.total_reviews = total_reviews
    place.save()
