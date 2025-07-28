from tenants.models import Clinica

output = ["--- Listado de Tenants Registrados ---"]
for clinica in Clinica.objects.all():
    output.append(f"Nombre: {clinica.nombre}, Schema Name: {clinica.schema_name}")
output.append("------------------------------------")

print("\n".join(output))

exit()

