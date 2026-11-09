# SEMVETO: verificación pública y plantillas de despliegue

SEMVETO es un estudio de investigación preregistrado: ¿reduce un modelo de lenguaje, usado como filtro semántico que puede vetar señales de un sistema de trading algorítmico, la varianza asimétrica de sus resultados? El estudio opera **solo en cuentas demo**, sin dinero real. Nada de lo que hay aquí es asesoramiento de inversión.

Este repositorio es público y contiene **solo** lo que un tercero necesita para comprobar el estudio o montar su propio entorno. No contiene el código del motor, ningún secreto, ningún identificador de las cuentas ni ningún nombre de los recursos de producción.

## Qué hay aquí

| Ruta | Qué es |
|---|---|
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

El botón «Deploy to Azure» está **en preparación**. Una versión de la plantilla solo se publica después de desplegarla en una suscripción de pruebas vacía. Entre otras cosas, esa prueba comprueba que una configuración que apunte a producción se niega a arrancar.

Lo que hará el botón:
- crear un grupo de recursos nuevo, con nombres derivados del propio grupo;
- usar las cuentas demo y la aplicación de cTrader de quien despliega;
- mandar los avisos a su propio correo.

La plantilla no aceptará ningún identificador de un recurso existente.

## Revisión automática

Antes de publicar, el repositorio privado del estudio revisa exactamente lo que se va a publicar. Busca una lista de nombres de producción, guardada solo como huellas SHA-256, y patrones genéricos:
- identificadores de Azure, direcciones de servicios, correos e IP;
- números de cuenta y cadenas de alta entropía;
- tipos de fichero no previstos.

Aquí, cada cambio pasa además por el flujo `secret-scan`. Solo se publica lo que pasa las dos revisiones.
