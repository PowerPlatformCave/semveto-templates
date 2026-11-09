# Cómo verificar un sello diario de SEMVETO

Necesitas tres cosas, que se publicarán con el registro del estudio en OSF:
1. el manifiesto del día, `manifiesto_AAAA-MM-DD.json`;
2. su prueba de OpenTimestamps, `manifiesto_AAAA-MM-DD.json.ots`, o la versión con la confirmación de Bitcoin, `manifiesto_AAAA-MM-DD.json-bitcoin.ots`;
3. una copia del registro de eventos del sistema (`base` o `A`), es decir, el directorio con sus ficheros `events_AAAA-MM-DD.jsonl`.

## Paso 1: el registro coincide con el manifiesto

```
python tools/semveto_verify.py --manifest manifiesto_2026-11-10.json --system base --ledger-dir <directorio del registro>
```

La herramienta rehace la cadena desde el primer evento. El *hash* de cada evento es el SHA-256 de su JSON canónico sin el campo `hash`: claves ordenadas, sin espacios, UTF-8. El `prev_hash` de cada evento tiene que ser el *hash* del anterior; el del primero es `GENESIS`.

Llega así hasta el evento que nombra el manifiesto. El número, el identificador y el *hash* de ese evento tienen que coincidir con los del manifiesto. Si alguien hubiera cambiado un evento anterior, la cadena no llegaría a ese mismo *hash*.

## Paso 2: el manifiesto existía en esa fecha

La herramienta imprime el SHA-256 del manifiesto: es lo que compromete la prueba. Hay dos maneras de comprobarla:
- **Con el cliente de OpenTimestamps** (`pip install opentimestamps-client`) y un nodo de Bitcoin Core; un nodo podado sirve. La herramienta ejecuta `ots verify` si lo encuentra.
- **Sin nodo:** sube la prueba y el manifiesto al verificador web de https://opentimestamps.org.

La prueba confirmada en Bitcoin dice en qué bloque, y por tanto antes de qué hora, existía ese manifiesto.

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | El registro coincide con el manifiesto y la prueba se verificó |
| 1 | No coincide |
| 2 | Uso incorrecto |
| 3 | El registro coincide, pero la prueba no se pudo comprobar en este equipo (falta el cliente o el nodo) |
