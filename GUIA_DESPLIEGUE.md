# Cómo desplegar la réplica de SEMVETO en tu suscripción (versión 0)

El botón «Deploy to Azure» del README abre el portal de Azure con la plantilla `templates/azuredeploy.json` y su formulario, `templates/createUiDefinition.json`.

## Qué crea

Todo va en un grupo de recursos **nuevo**, que eliges en el formulario, con nombres derivados del propio grupo:

- una máquina virtual Ubuntu 24.04 con identidad administrada. No tiene ninguna regla de entrada: se administra con Run Command;
- un Key Vault con permisos RBAC. La plantilla no lleva ningún secreto;
- una cuenta de almacenamiento sin claves compartidas, con los contenedores del estudio:
  - `ledger`, con retención temporal sin bloquear;
  - `ops`, `sellos` e `informes`;
- un área de trabajo de Log Analytics;
- un aviso por correo, a la dirección del formulario, si la máquina deja de estar disponible;
- una cuenta de AI Services con dos despliegues de los mismos modelos y versiones del estudio, sin actualización automática.

La identidad de la máquina recibe roles solo sobre esos recursos.

## Qué no hace todavía

Esta versión despliega la infraestructura y nada más:
- el código del motor no se instala;
- no se autoriza ninguna cuenta demo de cTrader;
- no arranca ningún servicio.

Esos pasos llegarán en una versión posterior, cuando también estén probados en un grupo vacío.

## Paso a paso

1. Pulsa el botón y elige suscripción, **un grupo de recursos nuevo** y región.
2. Rellena tu correo de avisos y tu clave pública SSH. La clave no abre ninguna puerta: no hay regla de entrada.
3. **Opcional:** ajusta el tamaño de la máquina, la capacidad de los modelos y la retención del contenedor `ledger`.
4. Crea el despliegue. Es posible que la cuota de los modelos no alcance en tu región o suscripción; en ese caso Azure lo dice al validar. Prueba con menos capacidad o en otra región.

## Cómo quitarlo todo

1. Borra el área de trabajo con `--force`, para que no quede en borrado temporal.
2. Borra la política de retención del contenedor `ledger`, que no está bloqueada.
3. Borra el grupo de recursos.
4. Purga el Key Vault y la cuenta de AI Services, que quedan en borrado temporal.

## Coste

- La máquina virtual se cobra mientras existe.
- Los modelos se pagan por uso: sin llamadas, no hay consumo.
- El almacenamiento y el área de trabajo cuestan poco con el volumen del estudio.

Consulta los precios de tu región antes de desplegar.

## Pruebas de cada versión

Antes de publicar una versión de la plantilla, se despliega en un grupo de recursos temporal vacío y se desmonta entero. La versión 0 se probó el 10-11-2026:
- 12 recursos creados en 72 s;
- los dos modelos respondieron a la identidad de la máquina;
- ninguna regla de entrada;
- al desmontarla, no quedó nada, tampoco en borrado temporal.

## El canal de consulta con IA

El segundo botón del README despliega la infraestructura del servidor MCP de solo lectura con el que se consulta el estudio desde Claude. Usa la plantilla `templates/mcp_azuredeploy.json`.

**Qué pide:**
- `domainName`: un subdominio de un dominio tuyo, por ejemplo `s1.example.com`. Solo ese subdominio pasa a Azure DNS: el resto del dominio sigue en tu registrador, sin cambios. Su nombre aparecerá en los registros públicos de certificados, así que conviene que sea neutro;
- `budgetUsd` y `budgetStart`: el presupuesto mensual del grupo y el primer día del mes.

**Qué crea**, en un grupo de recursos **nuevo**, con nombres derivados del propio grupo:
- la zona DNS pública del subdominio, con SPF `-all`, DMARC `reject` y una CAA que solo admite a DigiCert, que emite el certificado gratuito de Container Apps;
- una identidad administrada asignada por el usuario;
- un registro de imágenes privado, sin usuario administrador;
- una cuenta de almacenamiento sin claves compartidas ni acceso público, con los contenedores `cache`, `consultas` (un año de retención) y `control`. La identidad solo puede escribir aquí;
- un presupuesto con avisos al 80 % y al 100 % para los propietarios de la suscripción.

**Después del despliegue:** en el panel DNS de tu registrador, crea cuatro registros **NS** con el nombre del subdominio (`s1` en el ejemplo) y como valores los cuatro de la salida `nameServers`. No cambies los servidores de nombres del dominio entero.

**Qué no hace todavía:** la imagen del servidor lleva el código del motor, que es privado. Por eso esta versión no crea:
- la aplicación (Container App);
- las dos aplicaciones de Entra ID: la API, con el ámbito `mcp.read`, y el cliente de Claude;
- los permisos de lectura sobre los datos del estudio.

**Desmontarlo:**
1. Borra el grupo de recursos.
2. Borra aparte el presupuesto, porque **un presupuesto de grupo no se borra con el grupo**: Cost Management → Presupuestos, o `az consumption budget delete`.
3. Borra los cuatro registros NS del subdominio en el registrador.

**Probado** en un grupo vacío el 25-11-2026: 35 s, todo dentro del grupo. Desmontado sin dejar recursos, roles ni presupuestos.
