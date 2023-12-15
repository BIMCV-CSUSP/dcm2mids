# dcm2mids

## imput del programa : folder del pryecto
  
   para agrupar los dicoms por sujeto/session/scan/imagen
  - if existe:
    - TODO OK
  - else:
    - probar si se puede realizar con PYDICOM
    - If se puede:
      - buscar dicomdir en la carperta raiz
        - IF EXISTE:
          - Leerlo (ya tenemos una base de datos que explorar)¿COMO...?
        - ELSE:
          - Listar archivos .dcm y generar un fileset
    \\ - else:
    \\ - TOCA HACERLO A MANO (una tabla de todos los metadatos y agruparlos \\ para tener su acceso directo a la imagen)
    \\  - agrupar
- recorrer la estructura por sujeto/session/scan/imagen
  - crear estructura sujeto/session/scan/
  - for cada elemento:
    - convertir
    - taggear(RM)
      - if 3D:
        - NIfTi/BIDS extensions
      - if 2D
        - PNG//BIDS extensions (NOTA: revisar standar dicom para las imagenes 2D agrupadas)
    - copiar archivos
    - crear json
  - crear TSVs
  - sourcedata????