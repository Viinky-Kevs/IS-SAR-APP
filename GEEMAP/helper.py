import ee

# ---------------------------------------------------------------------------//
# Linear to db scale
# ---------------------------------------------------------------------------//

def lin_to_db(image):
    bandNames = image.bandNames().remove('angle')
    db = ee.Image.constant(10).multiply(image.select(bandNames).log10()).rename(bandNames)
    return image.addBands(db, None, True)


def db_to_lin(image):
    bandNames = image.bandNames().remove('angle')
    lin = ee.Image.constant(10).pow(image.select(bandNames).divide(10)).rename(bandNames)
    return image.addBands(lin, None, True)

def lin_to_db2(image):
    db = ee.Image.constant(10).multiply(image.select(['VV', 'VH']).log10()).rename(['VV', 'VH'])
    return image.addBands(db, None, True)

# ---------------------------------------------------------------------------//
# Add ratio bands
# ---------------------------------------------------------------------------//

def add_ratio_lin(image):
    ratio = image.addBands(image.select('VV').divide(image.select('VH')).rename('VVVH_ratio'))
    return ratio.set('system:time_start', image.get('system:time_start'))