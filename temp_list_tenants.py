from tenants.models import Clinica

print("--- Listado de Tenants Registrados ---")
for clinica in Clinica.objects.all():
    print(f"Nombre: {clinica.nombre}, Schema Name: {clinica.schema_name}")
print("------------------------------------")

exit()
