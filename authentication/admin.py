from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import About, Room, Customer, Payment, CheckIn,   CheckOut, RoomDisplayImages, Place, PlaceInfo, Booking, ExtraCharge


def update_room_is_booked_to_false(model_admin, request, query_set):
    query_set.update(is_booked=False)


update_room_is_booked_to_false.short_description_message = "Update all is_booked to False"


class RoomDisplayImagesStacked(admin.StackedInline):
    model = RoomDisplayImages


class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomDisplayImagesStacked]

    class Meta:
        model = Room

    list_display = ['__str__', 'is_booked']    
    actions = [update_room_is_booked_to_false]

# blog


admin.site.register(About) 
admin.site.register(Place)
admin.site.register(PlaceInfo)
admin.site.register(Booking)
admin.site.register(ExtraCharge)



# booking
admin.site.register(Room, RoomAdmin)
admin.site.register(Customer)
admin.site.register(Payment)
admin.site.register(CheckIn)
admin.site.register(CheckOut)
admin.site.register(RoomDisplayImages)
