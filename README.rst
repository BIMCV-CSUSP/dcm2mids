.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/dcm2mids.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/dcm2mids
    .. image:: https://readthedocs.org/projects/dcm2mids/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://dcm2mids.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/dcm2mids/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/dcm2mids
    .. image:: https://img.shields.io/pypi/v/dcm2mids.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/dcm2mids/
    .. image:: https://img.shields.io/conda/vn/conda-forge/dcm2mids.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/dcm2mids
    .. image:: https://pepy.tech/badge/dcm2mids/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/dcm2mids
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/dcm2mids

.. image:: https://img.shields.io/pypi/v/dcm2mids.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/dcm2mids/

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/



dcm2mids
============


    DCM2MIDS is a software tool designed to convert DICOM (Digital Imaging and Communications in Medicine) files into the MIDS (Medical Imaging Data Structure) format. It facilitates the integration of medical imaging data into research and clinical workflows, enhancing interoperability and data analysis capabilities. DCM2MIDS supports efficient data conversion, ensuring the preservation of essential metadata and image quality, thereby aiding in advanced medical imaging research and diagnostics.



installation
============


To install the latest release from PyPI, use pip:

.. code-block:: bash

    pip install dcm2mids

If you need to install from git, Clone the repository and install from source as a pip package:

.. code-block:: bash

    git clone https://github.com/BIMCV-CSUSP/dcm2mids.git
    cd dcm2mids
    pip install -e .




Usage
============

DCM2MIDS Script
-------------------------------
This script reads a folder containing medical images and converts them to a BIDS/MIDS structure. It is designed to streamline the organization and standardization of medical imaging data, ensuring compatibility with BIDS (Brain Imaging Data Structure) and MIDS (Medical Imaging Data Structure) standards.

Arguments
-------------------------------

- **-i, --input**:

  - **Type**: str
  - **Description**: Path to the input folder containing the images in dicom format.
  - **Required**: Yes

- **-o, --output**:

  - **Type**: str
  - **Description**: Path to the output folder where the converted images will be stored.
  - **Required**: Yes

- **-bp, --body-part**:

  - **Type**: str
  - **Description**: Specify which part of the body is in the dataset.
  - **Required**: Yes

- **-b, --bids**:

  - **Action**: store_true
  - **Description**: Use BIDS standard. Only applicable for protocols/body parts considered in BIDS.

- **-v, --verbose**:

  - **Choices**: "DEBUG", "INFO", "WARNING", "ERROR"
  - **Default**: "INFO"
  - **Description**: Set the verbosity level of the script. Options are DEBUG, INFO, WARNING, ERROR.

- **-log, --logfile**:

  - **Type**: Path
  - **Description**: Path to the file where logs will be stored.

#### Example Usage

.. code-block:: bash

   python3 -m dcm2mids.py -i /path/to/input/folder -o /path/to/output/folder -bp eye -b -v DEBUG -log /path/to/logfile.log

This example reads images from `/path/to/input/folder`, converts them to a BIDS structure with the body part specified as 'head', sets the verbosity level to DEBUG, and stores logs in `/path/to/logfile.log`.

For more detailed information, refer to the script's help message by running:

.. code-block:: bash

   python -m dcm2mids.py --help

License
============

This project is licensed under the GNU General Public License v3.0. You are free to use, modify, and distribute this software under the following conditions:

GNU General Public License v3.0
-------------------------------

.. code-block:: text

    Copyright (C) [2024] [Jose Manuel Saborit Torres]

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

For a full license copy, refer to the `LICENSE` file included in this repository or visit the official GNU website at <https://www.gnu.org/licenses/gpl-3.0.html>.


For questions or comments about dcm2mids, you can open an issue in the repository or contact the project maintainers directly.

Contact Options:

Open an issue: Visit the Issues section of the repository and create a new issue describing your question or comment.

Contact the maintainers: Send an email to the project maintainers. You can find their contact information on the repository's main page or in the MAINTAINERS.md file.

We look forward to your feedback and questions!
