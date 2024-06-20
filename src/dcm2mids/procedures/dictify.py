from pydicom.dataset import Dataset
from pydicom.datadict import get_entry


def convert_string(input_string: str) -> str:
    """Split the string into words, capitalize each word, and then join them without spaces"""
    cleaned_string = input_string.replace('(', ' ').replace(')', ' ')
    return ''.join(word.capitalize() for word in cleaned_string.split())

def dictify(ds: Dataset, stop_before_pixels: bool = True) -> dict:
    """Turn a pydicom Dataset into a dict with keys derived from the Element names."""
    output = dict()
    for elem in ds:
        if elem.name == "Pixel Data" and stop_before_pixels:
            continue
        if elem.VR != "SQ":
            if not elem.tag.is_private:
                output[get_entry(elem.tag)[-1]] = str(elem.value)
            else:
                output[convert_string(elem.name)] = str(elem.value)
        else:
            if not elem.tag.is_private:
                output[get_entry(elem.tag)[-1]] = [dictify(item) for item in elem]
            else:
                output[convert_string(elem.name)] = [dictify(item) for item in elem]  
    return output
