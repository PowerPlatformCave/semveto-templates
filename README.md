# SEMVETO: verificación pública y plantillas de despliegue

SEMVETO es un estudio de investigación preregistrado: ¿reduce un modelo de lenguaje, usado como filtro semántico que puede vetar señales de un sistema de trading algorítmico, la varianza asimétrica de sus resultados? El estudio opera **solo en cuentas demo**, sin dinero real. Nada de lo que hay aquí es asesoramiento de inversión.

Este repositorio es público y contiene **solo** lo que un tercero necesita para comprobar el estudio o montar su propio entorno. No contiene el código del motor, ningún secreto, ningún identificador de las cuentas ni ningún nombre de los recursos de producción.

## Qué hay aquí

| Ruta | Qué es |
|---|---|
| `templates/` | La plantilla del botón (`azuredeploy.json`) y su formulario (`createUiDefinition.json`). |
| `GUIA_DESPLIEGUE.md` | Qué crea el botón, cómo desplegarlo y cómo quitarlo todo. |
| `tools/semveto_verify.py` | El verificador de los sellos diarios. Solo usa la biblioteca estándar de Python. |
| `GUIA_VERIFICACION.md` | Cómo comprobar un sello diario frente a una copia del registro. |
| `.github/workflows/secret-scan.yml` | La revisión automática de cada cambio: un detector estándar de secretos y los patrones genéricos. Si encuentra algo, el cambio no entra. |

## Los sellos diarios

Cada día de mercado, el servicio de operaciones del estudio escribe un manifiesto con la cabeza de la cadena de *hashes* de cada registro de eventos:
- el número de eventos;
- el identificador y el *hash* del último evento;
- la huella diaria.

El manifiesto no lleva saldos, cifras ni textos. Se sella con [OpenTimestamps](https://opentimestamps.org), así que cualquiera puede comprobar, sin confiar en el proveedor de la nube ni en los autores, que el registro no se reescribió después. Los manifiestos y sus pruebas se publicarán con el registro del estudio en OSF.

## Despliegue en otra suscripción de Azure

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FPowerPlatformCave%2Fsemveto-templates%2Fmain%2Ftemplates%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FPowerPlatformCave%2Fsemveto-templates%2Fmain%2Ftemplates%2FcreateUiDefinition.json)

**Versión 0: solo la infraestructura de una réplica,** en un grupo de recursos nuevo de quien despliega:
- máquina virtual sin reglas de entrada;
- Key Vault;
- almacenamiento con los contenedores del estudio;
- Log Analytics y un aviso por correo;
- una cuenta de AI Services con los dos modelos del estudio, en las mismas versiones y sin actualización automática.

El código del motor, las cuentas demo y el arranque de los servicios llegarán en una versión posterior. Pasos y desmontaje: [`GUIA_DESPLIEGUE.md`](GUIA_DESPLIEGUE.md).

**Lo que la plantilla garantiza:**
- no acepta ningún identificador de un recurso existente;
- `environment` solo admite `replica`;
- sus avisos van al correo del formulario;
- cada versión se prueba en un grupo vacío y se desmonta entera antes de publicarse.

## Revisión automática

Antes de publicar, el repositorio privado del estudio revisa exactamente lo que se va a publicar. Busca una lista de nombres de producción, guardada solo como huellas SHA-256, y patrones genéricos:
- identificadores de Azure, direcciones de servicios, correos e IP;
- números de cuenta y cadenas de alta entropía;
- tipos de fichero no previstos.

Aquí, cada cambio pasa además por el flujo `secret-scan`. Solo se publica lo que pasa las dos revisiones.
