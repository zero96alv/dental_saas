from tenants.models import Domain, Clinica

# Configurar dominio para el esquema público
try:
    public_tenant = Clinica.objects.get(schema_name='public')
    Domain.objects.get_or_create(
        domain='admin.localhost',
        tenant=public_tenant,
        is_primary=False
    )
    print("Dominio 'admin.localhost' configurado para el esquema público.")
except Clinica.DoesNotExist:
    print("ERROR: No se encontró el tenant del esquema 'public'.")

# Configurar dominio para el tenant 'demo'
try:
    demo_tenant = Clinica.objects.get(schema_name='demo')
    Domain.objects.update_or_create(
        domain='demo.localhost',
        tenant=demo_tenant,
        defaults={'is_primary': True}
    )
    print("Dominio 'demo.localhost' configurado para el tenant 'demo'.")
except Clinica.DoesNotExist:
    print("ERROR: No se encontró el tenant 'demo'.")

exit()
