from django.db import migrations
import json

def seed_nepal_address(apps, schema_editor):
    State = apps.get_model('base', 'State')
    Municipality = apps.get_model('base', 'Municipality')
    # Add to seed_nepal_address in the migration
    Department = apps.get_model('base', 'Department')
    departments = [
        {"name": "Health Services"},
        {"name": "Education"},
        {"name": "Public Works"},
    ]
    for dept in departments:
        dept_obj, created = Department.objects.get_or_create(name=dept["name"])
        if created:
            print(f"Created department: {dept['name']}")
        # Optionally link to all municipalities
        dept_obj.municipalities.set(Municipality.objects.all())

    # Hardcoded provinces
    provinces = [
        {"id": 1, "name": "Koshi"},
        {"id": 2, "name": "Madhesh"},
        {"id": 3, "name": "Bagmati"},
        {"id": 4, "name": "Gandaki"},
        {"id": 5, "name": "Lumbini"},
        {"id": 6, "name": "Karnali"},
        {"id": 7, "name": "Sudurpashchim"},
    ]

    # Sample municipalities (subset)
    municipalities_data = [
        {"name": "Biratnagar Metropolitan City", "province_id": 1},
        {"name": "Itahari Sub-Metropolitan City", "province_id": 1},
        {"name": "Dharan Sub-Metropolitan City", "province_id": 1},
        {"name": "Birgunj Metropolitan City", "province_id": 2},
        {"name": "Janakpur Sub-Metropolitan City", "province_id": 2},
        {"name": "Kathmandu Metropolitan City", "province_id": 3},
        {"name": "Lalitpur Metropolitan City", "province_id": 3},
        {"name": "Pokhara Metropolitan City", "province_id": 4},
        {"name": "Bharatpur Metropolitan City", "province_id": 3},
        {"name": "Nepalgunj Sub-Metropolitan City", "province_id": 5},
        {"name": "Dhangadhi Sub-Metropolitan City", "province_id": 7},
    ]

    # Insert provinces
    state_map = {}
    for province in provinces:
        try:
            state_obj, created = State.objects.get_or_create(name=province["name"])
            if created:
                print(f"Created state: {province['name']}")
            state_map[province["id"]] = state_obj
        except Exception as e:
            print(f"Error creating province '{province['name']}': {e}")
            continue

    # Insert municipalities
    created_count = 0
    for mun in municipalities_data:
        try:
            province_id = int(mun.get("province_id", 0))
            state_obj = state_map.get(province_id)
            if not state_obj:
                print(f"Skipping municipality '{mun.get('name')}': No state for province_id {province_id}")
                continue
            mun_name = mun.get("name", "").strip().title()
            if not mun_name:
                print(f"Skipping empty municipality name for province_id {province_id}")
                continue
            if not Municipality.objects.filter(name=mun_name, state=state_obj).exists():
                Municipality.objects.create(name=mun_name, state=state_obj)
                created_count += 1
                print(f"Created municipality: {mun_name} in {state_obj.name}")
        except Exception as e:
            print(f"Error creating municipality '{mun.get('name')}': {e}")
            continue

    print(f"Total states created: {State.objects.count()}")
    print(f"Total municipalities created: {created_count}")

def unseed_nepal_address(apps, schema_editor):
    State = apps.get_model('base', 'State')
    Municipality = apps.get_model('base', 'Municipality')
    Municipality.objects.all().delete()
    State.objects.all().delete()
    print("Cleared all Municipalities and States")

class Migration(migrations.Migration):
    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_nepal_address, unseed_nepal_address),
    ]