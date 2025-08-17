from django.db import migrations
import requests
import json

def seed_nepal_address(apps, schema_editor):
    State = apps.get_model('base', 'State')
    Municipality = apps.get_model('base', 'Municipality')

    # Fetch provinces
    provinces_url = 'https://raw.githubusercontent.com/bimalstha23/Nepal-Address-API/main/data/provinces.json'
    try:
        response = requests.get(provinces_url, timeout=10)
        response.raise_for_status()
        provinces_data = json.loads(response.text)
        provinces = provinces_data.get('provinces', [])
        if not provinces:
            print("No provinces found in JSON response")
            return
    except Exception as e:
        print(f"Error fetching provinces: {e}")
        return

    for province_name in provinces:
        state, created = State.objects.get_or_create(name=province_name.lower())
        if created:
            print(f"Seeded state: {province_name}")

        # Fetch districts for province
        districts_url = f'https://raw.githubusercontent.com/bimalstha23/Nepal-Address-API/main/data/districts/{province_name}.json'
        try:
            response = requests.get(districts_url, timeout=10)
            response.raise_for_status()
            districts_data = json.loads(response.text)
            districts = districts_data.get('districts', [])
            if not districts:
                print(f"No districts found for {province_name}")
                continue
        except Exception as e:
            print(f"Error fetching districts for {province_name}: {e}")
            continue

        for district_name in districts:
            municipals_url = f'https://raw.githubusercontent.com/bimalstha23/Nepal-Address-API/main/data/municipals/{district_name}.json'
            try:
                response = requests.get(municipals_url, timeout=10)
                response.raise_for_status()
                municipals_data = json.loads(response.text)
                municipals = municipals_data.get('municipals', [])
                if not municipals:
                    print(f"No municipalities found for {district_name}")
                    continue
                for municipal_name in municipals:
                    _, created = Municipality.objects.get_or_create(
                        name=municipal_name.lower(),
                        state=state
                    )
                    if created:
                        print(f"Seeded municipality: {municipal_name} for state {province_name}")
            except Exception as e:
                print(f"Error fetching municipalities for {district_name}: {e}")
                continue

class Migration(migrations.Migration):
    dependencies = [
        ('base', '0004_remove_department_municipality_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_nepal_address),
    ]
    