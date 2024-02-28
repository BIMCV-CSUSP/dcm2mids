from pydicom.dataset import Dataset

def dictify(ds: Dataset, stop_before_pixels: bool = True) -> dict:
    """Turn a pydicom Dataset into a dict with keys derived from the Element names."""
    output = dict()
    for elem in ds:
        if elem.name == "Pixel Data" and stop_before_pixels: continue
        if elem.VR != "SQ":
            output[elem.name] = str(elem.value)
        else:
            output[elem.name] = [dictify(item) for item in elem]
    return output