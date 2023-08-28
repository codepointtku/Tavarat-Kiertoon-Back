from products.models import Color


def my_scheduled_job():
    Color(name="JEE", default=True).save()

    Color(name="Vihreä", default=True).save()
    pass
