from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_alter_inventoryreservation_expires_at_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="inventoryreservation",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="inventoryreservation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("cart__isnull", False)),
                fields=("cart", "product"),
                name="unique_cart_product_reservation",
            ),
        ),
        migrations.AddConstraint(
            model_name="inventoryreservation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("order__isnull", False)),
                fields=("order", "product"),
                name="unique_order_product_reservation",
            ),
        ),
    ]
