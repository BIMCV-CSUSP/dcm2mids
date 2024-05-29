# dcm2mids

`dcm2mids` es una herramienta para convertir imágenes DICOM a la estructura BIDS/MIDS. Este proyecto ha sido creado utilizando PyScaffold.

## Instalación

## Installation

There are three options:

- Clone the repository and add the folder to the `PYTHONPATH` (recommended if you wish to contribute, or develop on top of the existing methods):

```bash
git clone https://github.com/BIMCV-CSUSP/dcm2mids.git
export PYTHONPATH="<PATH>/dcm2mids:$PYTHONPATH"
```

Replacing `<PATH>` with the proper value to generate a global path to the `dcm2mids` folder. The configuration of the `PYTHONPATH` may vary for your system.

- Clone the repository, and install from source as a pip package:

```bash
git clone https://github.com/BIMCV-CSUSP/dcm2mids.git
cd dcm2mids
pip install -e .
```

- Install as a standalone pip package using:

```bash
pip install git+https://github.com/BIMCV-CSUSP/dcm2mids.git#egg=dcm2mids
```


## Uso

Después de la instalación, puedes usar `dcm2mids` desde la línea de comandos. Aquí hay un ejemplo básico de cómo usar la herramienta:

```sh
dcm2mids /ruta/a/tu/archivo.dcm /ruta/de/salida
```

## Desarrollo

Si deseas contribuir al desarrollo de `dcm2mids`, sigue estos pasos:

1. Clona el repositorio:
    ```sh
    git clone https://github.com/tu-usuario/dcm2mids.git
    cd dcm2mids
    ```

2. Crea un entorno virtual (opcional pero recomendado):
    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias para el desarrollo:
    ```sh
    pip install -U pip setuptools wheel
    pip install -e .[dev]
    ```

4. Realiza tus cambios y asegúrate de que los tests pasen:
    ```sh
    pytest
    ```

5. Realiza un pull request con tus cambios.

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Para preguntas o comentarios sobre `dcm2mids`, puedes abrir un issue en el repositorio o contactar a los mantenedores del proyecto.

```

Este `README.md` incluye instrucciones para la instalación, uso y desarrollo del proyecto `dcm2mids`, así como información sobre la licencia y el contacto para soporte adicional. Asegúrate de reemplazar `https://github.com/tu-usuario/dcm2mids.git` con la URL real de tu repositorio de GitHub.