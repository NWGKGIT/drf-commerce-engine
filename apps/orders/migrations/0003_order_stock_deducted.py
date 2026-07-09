from django.db import migrations, models


def mark_existing_orders_as_stock_deducted(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(items__isnull=False).distinct().update(stock_deducted=True)


def unmark_existing_orders_as_stock_deducted(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.update(stock_deducted=False)


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_alter_order_created_at_alter_order_order_number_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="stock_deducted",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            mark_existing_orders_as_stock_deducted,
            unmark_existing_orders_as_stock_deducted,
        ),
    ]
