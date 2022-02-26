from .helper import lin_to_db, db_to_lin

# ---------------------------------------------------------------------------//
# Additional Border Noise Removal
# ---------------------------------------------------------------------------//

def maskAngLT452(image):
    ang = image.select(['angle'])
    return image.updateMask(ang.lt(45.23993)).set('system:time_start', image.get('system:time_start'))

def maskAngGT30(image):
    ang = image.select(['angle'])
    return image.updateMask(ang.gt(30.63993)).set('system:time_start', image.get('system:time_start'))

def maskEdge(image):
    mask = image.select(0).unitScale(-25, 5).multiply(255).toByte()#.connectedComponents(ee.Kernel.rectangle(1,1), 100)
    return image.updateMask(mask.select(0)).set('system:time_start', image.get('system:time_start')) 

def f_mask_edges(image):
    db_img = lin_to_db(image)
    output = maskAngGT30(db_img)
    output = maskAngLT452(output)
    #output = maskEdge(output)
    output = db_to_lin(output)
    return output.set('system:time_start', image.get('system:time_start'))