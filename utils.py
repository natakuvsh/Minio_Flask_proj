import time

def millisec_to_age(birthts):
    """
    Transform from timestamp ms to age in years
    :param birthts: the timestamp ms
    :return:
    """
    now = time.time() * 1000
    return int((now - birthts) / (3.1536 * 10 ** 10))




