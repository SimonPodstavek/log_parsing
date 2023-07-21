# Use this template to add new parameters to LPT based on 3224 MAP S LPT.
# First level comments are intended for the person adding the parameter.
# Idented comments should be coied with the code, or be changed depending on the requirements

############################################################ PAP ############################################################





# Parameter is NOT compulsory, DOESN'T have minimal date, is NOT replacable and doesn't have specific formatting (PAP 0.0.0.0)

    #Find xyz
    parameter_found = False
    try:
        response = re.findall(regex_expressions['PAP_xyz'], record)

#Select just first matching REGEX group. This can be changed based on requirements
        response = ''.join(filter(None, response[0])).strip()
        #Remove closing parenthesis if they do not match opening parenthesis
        response = response.strip()
        
        record_object.set_xyz(response)
        parameter_found = True
        record_object.set_xyz(response)
    except:
        failures['PAP_xyz']+=1

    

# Parameter is compulsory, DOESN'T have minimal date, is NOT replacable, and doesn't have specific formatting (PAP 1.0.0.0)

    #Find xyz
    parameter_found = False
    try:
        response = re.findall(regex_expressions['PAP_xyz'], record)
#Select just first matching REGEX group. This can be changed based on requirements
        response = ''.join(filter(None, response[0])).strip()
        #Remove closing parenthesis if they do not match opening parenthesis
        response = response.strip()
        
        record_object.set_xyz(response)
        parameter_found = True
        record_object.set_xyz(response)
    except:
        failures['PAP_xyz']+=1
        return None





# Parameter is compulsory, DOESN'T have minimal date, is replaceable and doesn't have specific formatting  (PAP 1.0.1.0)


    #Find xyz
    parameter_found = False
    try:
        response = re.findall(regex_expressions['PAP_xyz'], record)

#The matching REGEX group can be changed depending on the requirements
#Select just first matching REGEX group. This can be changed based on requirements
        response = ''.join(filter(None, response[0])).strip()
        
        parameter_found=True
    except:
        pass

    if parameter_found == False:

# XYZ_REGEX != regex_expressions['PAP_xyz'], instead it should be modified so that it matches only the sought after expression
# E.g. regex_expressions['PAP_xyz'] = (?:Parameter XYZ\s*:\s*(\d{4}-\d{4}))
# XYZ_REGEX = \d{4}-\d{4}

        response = error_handler(record_object, 105,"V zadanom zázname neexistuje xyz. Zadajte xyz vo formáte NNNN-NNNN",True, "N/A",re.compile(r'XYZ_REGEX'))
        if response == None:
            failures['PAP_xyz'] += 1
            return None

        elif response == 111:
            return 111
        else:
            response = response.strip().split(' ')
            parameter_found=True   


    record_object.set_xyz(response)







# Parameter is compulsory, DOESN'T have minimal date, is replacable and has specific formatting (PAP 1.0.1.1)
    
    
    
    parameter_found = False
    try:
        response = re.search(regex_expressions['PAP_xyz'], record)
#Select just first matching REGEX group. This can be changed based on requirements
        response = response.group(0).strip()
# Date specific replacement. Replaces spaces with dots with dots
        response = response.replace('. ', '.')
    except:
        pass

# Date specific loop. It identifies whether a date is in specific format.
# This part should be changed depending on the parameter requirements

    for format in ('%Y.%m.%d %H:%M:%S','%Y.%m.%d %H:%M:%S;','%m/%d/%Y %H:%M:%S'):
        
        try:
            response = datetime.strptime(response, format)
            header_pap_datetime = response
            parameter_found=True
            break
        except:
            pass

# If date is not found.
# This part should be changed depending on the requirements

    if parameter_found == False:
            response = error_handler(record_object, 105,"V zadanom zázname neexistuje dátum a čas. Zadajte dátum a čas v formáte dd.mm.yyyy hh:mm:ss",True, "N/A",re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}\s\d{1,2}:\d{1,2}:\d{1,2}'))
            if response == None:
                failures['PAP_xyz']+=1
                return None
            elif response == 111:
                return 111
            else:
                response = datetime.strptime(response, '%d.%m.%Y %H:%M:%S')
                parameter_found = True
                record_object.set_xyz(response)          


############################################################ KAM ############################################################

# Parameter is NOT compulsory, has minimal date, is replacable, has specific formatting and is multichannel  (KAM 0.1.1.1.1)
    #Find KAM xyz
    parameter_found = False
    M_response = ''
    C_response = ''
    try:
# Change 2014, 1, 1 to minimal date, that contains this parameter
        if datetime.date(record_object.get_config_datetime()) > date(2014,1,1):
            response = re.findall(regex_expressions['KAM_xyz'],record)
#Select just first matching REGEX group. This can be changed based on requirements
            M_response = ''.join(filter(None, response[0])).strip()
            if len(response) == 2:
                C_response = ''.join(filter(None, response[1])).strip()
            elif multichannel:
                C_response = M_response
            parameter_found = True
    except:
        pass

# Change 2014, 1, 1 to minimal date, that contains this parameter
    if parameter_found == False and datetime.date(record_object.get_config_datetime()) > date(2014,1,1):
        M_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza xyz. Zadajte xyz pre kanál M vo formáte A.B.C",False, "N/A",re.compile(r'.*'))
        C_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza xyz. Zadajte xyz pre kanál C vo formáte A.B.C (Ak je totožna ako kanál M, zadajte \'-\'). ",False, "N/A",re.compile(r'.*'))
        if M_response == None:
            failures['KAM_xyz_M']+=1
            return None
        elif M_response == 111:
            return 111
        
        if not multichannel:
            pass
        elif C_response == None:
            failures['KAM_xyz_C']+=1
            return N    one
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = M_response

        parameter_found=True
            
    record_object.set_M_xyz(M_response)
    record_object.set_C_xyz(C_response)


# Parameter is compulsory, DOESN'T have minimal date, is replacable, DOESN'T have specific formatting and is NOT multichannel  (KAM 1.0.1.0.0)
    #Find KAM xyz
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_xyz'], record)
        #Select just first matching REGEX group
        response = ''.join(filter(None, response[0])).strip()
        response = response.strip()
        
        response = response.replace('-', '')

        record_object.set_xyz(response)
        parameter_found=True
    except:
        pass

    if parameter_found == False:
        response = error_handler(record_object, 105,"V zadanom zázname neexistuje xyz. Zadajte xyz vo formáte  alebo XXXXXXX",True, "N/A",re.compile(r'.*-.*'))
        if response == None:
            failures['KAM_xyz']+=1
            return None
        elif response == 111:
            return 111
        else:
            parameter_found=True
            
    record_object.set_xyx(response)



# Parameter is NOT compulsory, DOESN'T have minimal date, is NOT replacable, DOESN'T have specific formatting and is NOT multichannel  (KAM 0.0.0.0.0)
    #Find KAM xyz
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_xyz'], record)
        #Select just first matching REGEX group
        response = ''.join(filter(None, response[0])).strip()
        response = response.strip()
        
        response = response.replace('-', '')

        record_object.set_xyz(response)
        parameter_found=True
    except:
        pass

    record_object.set_xyx(response)


# Parameter is compulsory, DOESN'T have minimal date, is NOT replacable, DOESN'T have specific formatting and is NOT multichannel  (KAM 1.0.0.0.0)
    #Find KAM xyz
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_xyz'], record)
        #Select just first matching REGEX group
        response = ''.join(filter(None, response[0])).strip()
        response = response.strip()
        
        response = response.replace('-', '')

        record_object.set_xyz(response)
        parameter_found=True
    except:
        failures['KAM_xyz']+= 1
        return None

    record_object.set_xyx(response)


# Parameter is compulsory, DOESN'T have minimal date, is replacable, DOESN'T have specific formatting and is NOT multichannel  (KAM 1.0.1.0.0)
    #Find KAM xyz
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_xyz'], record)
        #Select just first matching REGEX group
        response = ''.join(filter(None, response[0])).strip()
        response = response.strip()
        
        response = response.replace('-', '')

        record_object.set_xyz(response)
        parameter_found=True
    except:
        pass

    if parameter_found == False:
        response = error_handler(record_object, 105,"V zadanom zázname neexistuje xyz. Zadajte xyz vo formáte  alebo XXXXXXX",True, "N/A",re.compile(r'.*-.*'))
        if response == None:
            failures['KAM_xyz']+=1
            return None
        elif response == 111:
            return 111
        else:
            parameter_found=True
            
    record_object.set_xyx(response)


# Parameter is compulsory, DOESN'T have minimal date, is replacable, has specific formatting and is NOT multichannel  (KAM 1.0.1.1.0)
 
    #Find KAM xyz
    parameter_found=False
    try:
        response = re.search(regex_expressions['KAM_xyz'], record)  
        response = response.group(0).strip()

# Changed based on requirements
        # Replace multiple white space character with just one
        response = re.sub(r'\s+', ' ', response)
        # Replace dot with space with dot
        response = response.replace('. ', '.')
    except:
        pass

# Change based on requirements
    for format in ('%d.%m.%Y %H:%M:%S','%m/%d/%Y %H:%M:%S'):
        try:
            response = datetime.strptime(response, format)
            record_object.set_xyz(response)
            parameter_found=True
            break
        except:
            pass


    if parameter_found == False:
# Change based on requirments
        response = error_handler(record_object, 105,"V zadanom zázname neexistuje xyz. Zadajte xyz vo formáte dd.mm.yyyy hh:mm:ss",True, "N/A",re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}\s\d{1,2}:\d{1,2}:\d{1,2}'))
        if response == None:
            failures['KAM_xyz']+=1
            return None
        elif response == 111:
            return 111
        else:
            response = datetime.strptime(response.strip(), '%d.%m.%Y %H:%M:%S')
            parameter_found = True

    record_object.set_xyz(response)


# Parameter is compulsory, has minimal date, is replacable, DOESN'T have specific formatting and is multichannel  (KAM 1.0.1.0.1)
    #Find KAM xyz
    parameter_found = False
    M_response = ''
    C_response = ''
    try:
        response = re.findall(regex_expressions['KAM_xyz'],record)
#Select just first matching REGEX group. This can be changed based on requirements
        M_response = ''.join(filter(None, response[0])).strip()
        if len(response) == 2:
            C_response = ''.join(filter(None, response[1])).strip()
        elif multichannel:
            C_response = M_response
        parameter_found = True
    except:
        pass

    if parameter_found == False:
        M_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza xyz. Zadajte xyz pre kanál M vo formáte A.B.C",False, "N/A",re.compile(r'.*'))
        C_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza xyz. Zadajte xyz pre kanál C vo formáte A.B.C (Ak je totožna ako kanál M, zadajte \'-\'). ",False, "N/A",re.compile(r'.*'))
    
        if M_response == None:
            failures['KAM_xyz_M']+= 1
            return None
        elif M_response == 111:
            return 111
        
        if not multichannel:
            pass
        elif C_response == None:
            failures['KAM_xyz_C']+= 1
            return None
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = M_response

        parameter_found=True
            
    record_object.set_M_xyz(M_response)
    record_object.set_C_xyz(C_response)

