from django.db import migrations


def classify(apps, schema_editor):
    Cafe = apps.get_model('cafeapp', 'Cafe')
    for cafe in Cafe.objects.using(schema_editor.connection.alias).all():
        location = (cafe.address + ' ' + cafe.area).lower()
        for terms, country, city in (
            (('new york', '뉴욕'), 'US', 'new-york'),
            (('san francisco', '샌프란시스코'), 'US', 'san-francisco'),
            (('tokyo', '도쿄'), 'JP', 'tokyo'),
            (('osaka', '오사카'), 'JP', 'osaka'),
        ):
            if any(term in location for term in terms):
                cafe.country, cafe.city = country, city
                cafe.save(update_fields=['country', 'city'])
                break


class Migration(migrations.Migration):
    dependencies = [('cafeapp', '0011_cafe_city_cafe_country')]
    operations = [migrations.RunPython(classify, migrations.RunPython.noop)]
