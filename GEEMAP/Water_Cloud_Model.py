import math

def sm_wcm(sigma0, theta):
    A = 85.71200708
    B = -32.46500098
    C = 0.90101068
    D = 4.39382781
    V = -0.06860272

    #Equation (2) in Bousbih's 2018 study
    thao2 = math.exp(-2 * B * (V / math.cos(theta * (math.pi / 180))))

    #Equation (4) in Bousbih's 2018 study
    sigma_0_veg = A * V * math.cos(theta * math.pi / 180) * (1 - thao2)

    sigma_0_veg = 0 if sigma_0_veg < 0 else sigma_0_veg

    #sigma_0_veg_soil was set as zero
    sigma_0_veg_soil = 0

    #Inverted form of Equation (4) in Bousbih's 2018 study, in which the equation 
    # is solved for mv (volumetric soil moisture) 

    mv = 1 / D * math.log((sigma0 - sigma_0_veg - sigma_0_veg_soil) / (C * thao2))

    return mv

def theta_0_5_to_0_60(theta_0_5, lat, long):
    #Computing theta_0_60
    theta_0_60 = 0.19 * theta_0_5 + 2.12 * lat - 1.10 * long + 166.91
    
    return theta_0_60