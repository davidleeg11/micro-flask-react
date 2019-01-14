# services/users/project/api/users.py


from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc
from project.api.models import Site
# from project.api.models import User
from project import db
from project.utils import sliped, get_jinja_vars, tower_files


sites_blueprint = Blueprint('sites', __name__, template_folder='./templates')
# users_blueprint = Blueprint('users', __name__, template_folder='./templates')


@sites_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        exec_workflow(site)
        site = request.form['site']
        db.session.add(Site(site=site))
        db.session.commit()
    sites = Site.query.all()
    return render_template('index.html', sites=sites)


@sites_blueprint.route('/sites/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@sites_blueprint.route('/sites', methods=['POST'])
def add_site():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    sitename = post_data.get('site')
    try:
        site_item = Site.query.filter_by(site=sitename).first()
        if not site_item:
            db.session.add(Site(site=sitename))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{sitename} was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That site already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400

@sites_blueprint.route('/sites/<site_id>', methods=['GET'])
def get_single_site(site_id):
    """Get single site details"""
    response_object = {
        'status': 'fail',
        'message': 'Site does not exist'
    }
    try:
        site = Site.query.filter_by(id=int(site_id)).first()
        if not site:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': site.id,
                    'site': site.site,
                    'active': site.active
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404

@sites_blueprint.route('/sites', methods=['GET'])
def get_all_sites():
    """Get all sites"""
    response_object = {
        'status': 'success',
        'data': {
            'sites': [site.to_json() for site in Site.query.all()]
        }
    }
    return jsonify(response_object), 200


def exec_workflow(site): 
    print("execute workflow" + site, file=sys.stderr)
    #use sliped API to get Backhaul Data and Site Data
    s = sliped.SlipedApi()  
    #DB Component options: 
    #CONFIG, AAV, NODEB, CORENET_IP, NMNET_IP, ACCESS_IP
    backhaul = s.getBackhaulDetails(site, "CONFIG")
    backhaul_access_ip = s.getBackhaulDetails(site, "ACCESS_IP")
    backhaul_corenet_ip = s.getBackhaulDetails(site, "CORENET_IP")
    backhaul_nmnet_ip = s.getBackhaulDetails(site, "NMNET_IP")
    backhaul_aav = s.getBackhaulDetails(site, "AAV")
    site = s.getSite(site)

    print("\n", file=sys.stderr)
    print("backhaul: \n\n" + str(backhaul), file=sys.stderr)
    print("\n"   , file=sys.stderr)
    print("site:  \n\n" + str(site), file=sys.stderr)


    current_data = backhaul["Data"]["Current"]["config"][0]
    current_data_access_ip = backhaul_access_ip["Data"]["Current"]["access_ip"]
    current_data_corenet_ip = backhaul_corenet_ip["Data"]["Current"]["corenet_ip"]
    current_data_nmnet_ip = backhaul_nmnet_ip["Data"]["Current"]["nmnet_ip"]
    current_data_aav = backhaul_aav["Data"]["Current"]["aav"][0]
    proposed_data = backhaul["Data"]["Proposed"]["config"][0]
    proposed_data_access_ip = backhaul_access_ip["Data"]["Proposed"]["access_ip"]
    proposed_data_corenet_ip = backhaul_corenet_ip["Data"]["Proposed"]["corenet_ip"]
    proposed_data_nmnet_ip = backhaul_nmnet_ip["Data"]["Proposed"]["nmnet_ip"]
    proposed_data_aav = backhaul_aav["Data"]["Proposed"]["aav"][0]

    #Sliped pre-checks:

    #1 show that there is a current record 
    #2 show that there is a proposed complete record that matches 1 of 3 change values associated: 
    #3 Inter MSO Rehome (AAV Termination Unchanged), Inter Chassis Rehome, Inter MSO Rehome (AAV Termination Change)  

    current_record = False;
    proposed_complete = False;
    inter_chassis_check = False;
    intra_chassis_check = False;

    #output json response from SLIPED
    #print("\n\ncurrent: " + str(current_data), file=sys.stderr)
    #print("\n\ncurrent_aav: " + str(current_data_aav), file=sys.stderr)
    #print("\n\ncurrent access_ip: " + str(current_data_access_ip), file=sys.stderr)
    #print("\n\ncurrent corenet_ip: " + str(current_data_corenet_ip), file=sys.stderr)
    #print("\n\ncurrent nmnet_ip: " + str(current_data_nmnet_ip), file=sys.stderr)
    #print("\n\nproposed: " + str(proposed_data), file=sys.stderr)
    #print("\n\nproposed_aav: " + str(proposed_data_aav), file=sys.stderr)
    #print("\n\nproposed access_ip: " + str(proposed_data_access_ip), file=sys.stderr)
    #print("\n\nproposed corenet_ip: " + str(proposed_data_corenet_ip), file=sys.stderr)
    #print("\n\nproposed nmnet_ip: " + str(proposed_data_nmnet_ip), file=sys.stderr)

    #1
    if (current_data["status_tx"] == "Current" and 
        current_data["change_type_tx"] == "AAV 2.0 E/// Pure IP + Pseudowire" or "E/// Pure IP + Pseudowire" or 
        "AAV 2.0 NSN Pure IP + Pseudowire" or "NSN Pure IP + Pseudowire" or "NSN PureIP + Packet ABIS" or 
        "AAV 2.0 NSN PureIP + Packet ABIS"):
        current_record = True;
    else:
        print("Does not support change type . . . ", file=sys.stderr)
    #2
    if (proposed_data["status_tx"] == "Proposed Complete" and 
        proposed_data["change_type_tx"] == "Inter MSO Rehome (AAV Termination Unchanged)" 
        or "Inter Chassis Rehome" or "Inter MSO Rehome (AAV Termination Change)" ): 
        proposed_complete = True;
    #3
    if current_data["ng_rtr_1_id_tx"] != proposed_data["ng_rtr_1_id_tx"]:
        inter_chassis_check = True;
    else:
        intra_chassis_check = True; 

    #Show test results
    if current_record and proposed_complete and inter_chassis_check:
        print("All sliped checks passed for 'INTER' chassis migration . . . ", file=sys.stderr)
    elif current_record and proposed_complete and inter_chassis_check:
        print("All sliped checks passed for 'INTRA' chassis migration . . .", file=sys.stderr)

    #   conn.send("show router interface to-7705-" + str(proposed_data_aav["primary_access_vlan"]) + "\n") #check that vlan  

    #CSR pre-checks:
    
    #requires OAM IP
#       a = current_data["cellsite_subnet_addr"].split('.') 
#       oam_ip = a[0] + '.' + a[1] + '.' + a[2] + '.' + str(int(a[3]) + 28)
#       print("OAM_IP:  " + oam_ip   , file=sys.stderr)

    print("\n\n" , file=sys.stderr)

    #login and validate chassis name (first 8 characters match with site)
    #CSR pre command: environment no more 
    #CSR post command: environment more 


    #Source/Current: MAD Odd and Even
    template_variables = OrderedDict()

    template_variables['current_mad_odd'] = current_data["ng_rtr_1_id_tx"]
    template_variables['current_mad_even'] = current_data["ng_rtr_2_id_tx"]
    print("\nMAD1: " + template_variables['current_mad_odd'], file=sys.stderr)
    print("\nMAD2: " + template_variables['current_mad_even'], file=sys.stderr)
    
    c_mad_routers = [template_variables['current_mad_odd'], template_variables['current_mad_even']]

    template_variables['c_primary_access_vlan'] = str(current_data_aav["primary_access_vlan"])  
    template_variables['c_ng_rtr_port'] = str(current_data["ng_rtr_port"])  
    template_variables['p_primary_access_vlan'] = str(proposed_data_aav["primary_access_vlan"]) 
    template_variables['p_ng_rtr_port'] = str(proposed_data["ng_rtr_port"]) 


    for x in range(0, 2):                
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(c_mad_routers[x], username='dlee104', password=pwd, look_for_keys= False, allow_agent= False)

        #nested ssh into CSR (need to revisit with best practice)
#           csr_transport = session.get_transport()
#           dest_addr = ('51.43.125.177', 22)
#           local_addr = (mad_routers[x], 22)
#           csr_channel = csr_transport.open_channel("direct-tcpip", dest_addr, local_addr)
#           #
#           csrhost = paramiko.SSHClient()
#           csrhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#           csrhost.connect('51.43.125.177', username='dlee104', password=pwd, look_for_keys=False, allow_agent=False, sock=csr_channel)
        #
        conn = session.invoke_shell()
        output = conn.recv(65534)
        conn.send("environment no more \n")
    #   conn.send("show chassis | match Name\n") 

#       client = SSHClient() 
#       client.set_missing_host_key_policy(AutoAddPolicy())
#       client.connect(oam_ip, username='dlee104',password=pwd,look_for_keys=False, timeout=20)
#       print("login successful")
#       shell = client.invoke_shell()
#       output = shell.recv(1000)
#       shell.exec_command('show chassis \n')
#       time.sleep(1)
#       if shell.recv_ready():
#           output = shell.recv(1000)
#       print(output)
#       client.close()
#       print(put    , file=sys.stderr)

        #get output of show commands and display

        #>show card         (only to log pre migration)
        #>show version   (only to log pre migration)
        #>show port         (only to log pre migration) 
        #>show system information ( 
            #SNMP Admin State          : Enabled
            #SNMP Oper State              : Enabled
            #SNMP Index Boot Status : Persistent )      
        #>show router interface (All Adm interfaces are UP)
        #>show router bfd session (all State Protocols = UP)
        #>show service sdp (SDPs Adm/Opr = UP)
        #>environment more


        
        #MAD: pre/migration checks  
        template_variables['c_ip_host_address_csr_system'] = None
        template_variables['c_ip_host_address_csr_interface'] = None
        template_variables['c_cellsite_subnet_address'] = None

        for idx, val in enumerate(current_data_access_ip):
            if val["ip_host_desc_tx"] == "CSR System IP Address":
                template_variables['c_ip_host_address_csr_system'] = str(current_data_access_ip[idx]["cellsite_subnet_addr"])
                print("\n\ncurrent CSR System {{ ip_host_addr }}: " + str(template_variables['c_ip_host_address_csr_system']), file=sys.stderr)
            if val["ip_host_desc_tx"] == "CSR Interface" :
                template_variables['c_ip_host_address_csr_interface'] = str(current_data_access_ip[idx]["cellsite_subnet_addr"])
                print("\n\ncurrent CSR Interface {{ ip_host_addr }}: " + str(template_variables['c_ip_host_address_csr_interface']), file=sys.stderr)

        for idx, val in enumerate(current_data_corenet_ip):
            if val["cellsite_subnet_desc_tx"] == "Cell site's /27 CORENET subnet" and template_variables['c_cellsite_subnet_address'] == None:
                template_variables['c_cellsite_subnet_address'] = str(current_data_corenet_ip[idx]["cellsite_subnet_addr"])
                print("\n\ncurrent Cellsite Subnet {{ ip_host_addr }}: " + str(template_variables['c_cellsite_subnet_address']), file=sys.stderr)

        #Get source QoS to variable 
        conn.send("admin display-config | match \"EQG-" + str(current_data_aav["primary_access_vlan"]) + "\" context all\n")    
        time.sleep(2)
        qos_output = str(conn.recv(65534))
        template_variables['qos_policy'] = qos_output.split("#--------------------------------------------------")[1].split('\"', 4)[4]


        #Get source A_CIR to variable
        template_variables['source_a_cir'] = qos_output.split("parent")[1].split('\"')[1].split('M')[0]
        print(str(template_variables['source_a_cir']), file=sys.stderr)
#           template_variables['qos_policy'] = template_variables['qos_policy'].replace('\r','')

#           conn.send("show router interface to-7705-" + str(current_data_aav["primary_access_vlan"]) + "\n") #(Port matches {{ ng_rtr_port }} ) 
#           conn.send("show router bfd session | match " + str(current_data_aav["primary_access_vlan"]) + "\n") #( to-7705-{{ corenet_vlan }} )
#           conn.send("show service sdp 1" + str(current_data_aav["primary_access_vlan"]) + "\n") #( 2 MAC Address, local and CSR* )
#           conn.send("show router ldp session | match " + str(template_variables['c_ip_host_address_csr_system']) + "\n") #( 2 MAC Address, local and CSR* )
#           conn.send("show router arp | match " + str(current_data_aav["primary_access_vlan"]) + "\n") #( 2 MAC Address, local and CSR* )
#           conn.send("show qos queue-group egress EQG-" + str(current_data_aav["primary_access_vlan"]) + " detail \n") #( 2 MAC Address, local and CSR* )
#           conn.send("show port " + str(current_data["ng_rtr_port"]) + " | match \"Admin State\"\n") #(Admin/Oper State = UP)
#           conn.send("show port " + str(current_data["ng_rtr_port"]) + " | match \"Oper State\"\n") #(Admin/Oper State = UP)
#           conn.send("admin display-config | match \"next-hop " + str(template_variables['c_ip_host_address_csr_interface']) + "\" context all\n") 
#           conn.send("admin display-config | match " + str(template_variables['c_cellsite_subnet_address']) + " context all\n") 
        conn.send("environment more\n") 

#           time.sleep(15)
        output = conn.recv(65534)
        print("\n " + c_mad_routers[x] + ": \n" + output)
        




    #Destination/Target: MAD Odd and Even           
    template_variables['datetime'] = str(datetime.now()) 
    template_variables['site_cd'] = backhaul["Data"]["Current"]["config"][0]['site_cd'] 

    #need to find out if 7950, this is a temporary value
    template_variables['is7950'] = True 
    template_variables['primary_access_vlan'] = proposed_data_aav["primary_access_vlan"]
    template_variables['secondary_access_vlan'] = proposed_data_aav["secondary_access_vlan"]
    template_variables['proposed_mad_odd'] = proposed_data["ng_rtr_1_id_tx"]
    template_variables['proposed_mad_even'] = proposed_data["ng_rtr_2_id_tx"]

    p_mad_routers = [template_variables['proposed_mad_odd'], template_variables['proposed_mad_even']]

    print("\nMAD1: " + template_variables['current_mad_odd'], file=sys.stderr)
    print("\nMAD2: " + template_variables['current_mad_even'], file=sys.stderr)

    template_variables['p_ip_host_address_csr_system'] = None
    template_variables['p_ip_host_address_csr_interface'] = None
    template_variables['p_cellsite_subnet_address'] = None

    template_variables['p_ip_host_address_mad1_e'] = None
    template_variables['p_ip_host_address_mad2_e'] = None
    template_variables['p_ip_host_address_mad1_ic'] = None
    template_variables['p_ip_host_address_mad2_ic'] = None
    template_variables['p_ip_host_address_mad1_to_csr_interface'] = None
    template_variables['p_ip_host_address_mad2_to_csr_interface'] = None
    template_variables['p_ip_host_address_csr_to_mad1_interface'] = None
    template_variables['p_ip_host_address_csr_to_mad2_interface'] = None    
    template_variables['p_ip_host_address_nmnet_subnet'] = None
    template_variables['p_ip_host_address_corenet_subnet'] = None
    template_variables['p_ip_host_address_csr_system_loopback'] = None



    for x in range(0, 2):                
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(p_mad_routers[x], username='dlee104', password=pwd, look_for_keys= False, allow_agent= False)

        conn = session.invoke_shell()
        output = conn.recv(65534)
        conn.send("environment no more \n")


        #MAD: pre/migration checks  
        for idx, val in enumerate(proposed_data_access_ip):
            #CSR System 
            if val["ip_host_desc_tx"] == "CSR System IP Address":
                template_variables['p_ip_host_address_csr_system'] = str(proposed_data_access_ip[idx]["cellsite_subnet_addr"])
                print("\n\nproposed CSR System {{ ip_host_addr }}: " + template_variables['p_ip_host_address_csr_system'], file=sys.stderr)
            #CSR Interface
            if val["ip_host_desc_tx"] == "CSR Interface" :
                template_variables['p_ip_host_address_csr_interface'] = str(proposed_data_access_ip[idx]["cellsite_subnet_addr"])
                print("\n\nproposed CSR Interface {{ ip_host_addr }}: " + template_variables['p_ip_host_address_csr_interface'], file=sys.stderr)

        for idx, val in enumerate(proposed_data_corenet_ip):
            #Cell Site Subnet
            if val["cellsite_subnet_desc_tx"] == "Cell site's /27 CORENET subnet" and template_variables['p_cellsite_subnet_address'] == None:
                template_variables['p_cellsite_subnet_address'] = str(proposed_data_corenet_ip[idx]["cellsite_subnet_addr"])
                print("\n\nproposed Cellsite Subnet {{ ip_host_addr }}: " + template_variables['p_cellsite_subnet_address'], file=sys.stderr)



#           conn.send("show router interface to-7705-" + str(proposed_data_aav["primary_access_vlan"]) + "\n") #(No matching entries found on both MADs) 
#           conn.send("show router bfd session | match " + str(proposed_data_aav["primary_access_vlan"]) + "\n") #(No matching entries) 
#           conn.send("show service sdp 1" + str(proposed_data_aav["primary_access_vlan"]) + "\n") #(No matching entries)
#           conn.send("show router ldp session | match " + str(template_variables['p_ip_host_address_csr_system']) + "\n") #(No matching entries) 
#           conn.send("show router arp | match " + str(proposed_data_aav["primary_access_vlan"]) + "\n") #(No matching entries)
#           conn.send("show qos queue-group egress EQG-" + str(proposed_data_aav["primary_access_vlan"]) + " detail \n") #(No matching entries)
#           conn.send("show port " + str(proposed_data["ng_rtr_port"]) + " | match \"Admin State\"\n") #(Admin/Oper State = UP)
#           conn.send("show port " + str(proposed_data["ng_rtr_port"]) + " | match \"Oper State\"\n") #(Admin/Oper State = UP)
#           conn.send("admin display-config | match \"next-hop " + str(template_variables['p_ip_host_address_csr_interface']) + "\" context all\n") 
#           conn.send("admin display-config | match " + str(template_variables['p_cellsite_subnet_address']) + " context all\n") 
        conn.send("environment more\n") 
        
#           time.sleep(15)
        output = conn.recv(65534)
        print("\n " + p_mad_routers[x] + ": \n" + output)



    #MAD: cleanup/post checks *PLACEHOLDER/TODO 
    #Destination/Target: MAD Odd and Even           
    #Source/Current: MAD Odd and Even


    #7750-to-7950 NSN 1.95 
    #Query config 
    template_variables['is_aav2_0'] = None
    if current_data_aav["primary_access_vlan"] - 2000 == current_data_aav["secondary_access_vlan"]:
        template_variables['is_aav2_0'] = True
    else:
        template_variables['is_aav2_0'] = False 

    print("\n primary_access_vlan: " + str(current_data_aav["primary_access_vlan"]))
    print("\n secondary_access_vlan: " + str(current_data_aav["secondary_access_vlan"]))
    print("\n template_variables['is_aav2_0']: " + str(template_variables['is_aav2_0']))



    for x in range(0, 2):                
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(c_mad_routers[x], username='dlee104', password=pwd, look_for_keys= False, allow_agent= False)

        conn = session.invoke_shell()
        output = conn.recv(65534)
        conn.send("environment no more \n")
    

        for idx, val in enumerate(proposed_data_access_ip):
            #MAD Interfaces
            if template_variables['is_aav2_0']:
                if val["ip_host_nm"] == p_mad_routers[0] + "_E System":
                    template_variables['p_ip_host_address_mad1_e'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                    print("\n\nproposed mad1 e {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad1_e'], file=sys.stderr)
                if val["ip_host_nm"] == p_mad_routers[1] + "_E System":
                    template_variables['p_ip_host_address_mad2_e'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                    print("\n\nproposed mad2 e {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad2_e'], file=sys.stderr)
            else:
                if val["ip_host_nm"] == "NG_" + p_mad_routers[0] + "_E System":
                    template_variables['p_ip_host_address_mad1_e'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                    print("\n\nproposed mad1 e {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad1_e'], file=sys.stderr)
                if val["ip_host_nm"] == "NG_" + p_mad_routers[1] + "_E System":
                    template_variables['p_ip_host_address_mad2_e'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                    print("\n\nproposed mad2 e {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad2_e'], file=sys.stderr)

            #MAD IC Interfaces
            if val["ip_host_nm"] == "NG_" + p_mad_routers[0] + "_E IC Interface":
                template_variables['p_ip_host_address_mad1_ic'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                print("\n\nproposed mad1 ic {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad1_ic'], file=sys.stderr)
            if val["ip_host_nm"] == "NG_" + p_mad_routers[1] + "_E IC Interface":
                template_variables['p_ip_host_address_mad2_ic'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                print("\n\nproposed mad2 ic {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad2_ic'], file=sys.stderr)

            #MADs to CSR Interface
            if val["ip_host_nm"] == p_mad_routers[0] + " to CSR Interface":
                template_variables['p_ip_host_address_mad1_to_csr_interface'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                print("\n\nproposed mad1_to_csr_interface {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad1_to_csr_interface'], file=sys.stderr)
            if val["ip_host_nm"] == p_mad_routers[1] + " to CSR Interface": 
                template_variables['p_ip_host_address_mad2_to_csr_interface'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                print("\n\nproposed mad2_to_csr_interface {{ ip_host_addr }}: " + template_variables['p_ip_host_address_mad2_to_csr_interface'], file=sys.stderr)
            #CSR to MAD Interfaces
            if val["ip_host_nm"] == "CSR interface to " + p_mad_routers[0]:
                template_variables['p_ip_host_address_csr_to_mad1_interface'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                print("\n\nproposed csr_to_mad1_interface {{ ip_host_addr }}: " + template_variables['p_ip_host_address_csr_to_mad1_interface'], file=sys.stderr)
            if val["ip_host_nm"] == "CSR interface to " + p_mad_routers[1]: 
                template_variables['p_ip_host_address_csr_to_mad2_interface'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                print("\n\nproposed csr_to_mad2_interface {{ ip_host_addr }}: " + template_variables['p_ip_host_address_csr_to_mad2_interface'], file=sys.stderr)
            if val["ip_host_nm"] == "PTP Loopback CSR IP address":
                template_variables['p_ip_host_address_csr_system_loopback'] = str(proposed_data_access_ip[idx]["ip_host_addr"])
                print("\n\nproposed CSR system loopback {{ ip_host_addr }}: " + template_variables['p_ip_host_address_csr_system_loopback'], file=sys.stderr)

        for idx, val in enumerate(proposed_data_nmnet_ip):
            if val["ip_host_nm"] == "Start combined SiteLAN(NodeB_OAM) and CellSiteLAN subnet host range":
                template_variables['p_ip_host_address_nmnet_subnet'] = str(proposed_data_nmnet_ip[idx]["ip_host_addr"])
                print("\n\nproposed nmnet_subnet {{ ip_host_addr }}: " + template_variables['p_ip_host_address_nmnet_subnet'], file=sys.stderr)

        for idx, val in enumerate(proposed_data_corenet_ip):
            if val["ip_host_nm"] == "Default Gateway":
                template_variables['p_ip_host_address_corenet_subnet'] = str(proposed_data_corenet_ip[idx]["cellsite_subnet_addr"])
                print("\n\nproposed corenet_subnet {{ ip_host_addr }}: " + template_variables['p_ip_host_address_corenet_subnet'], file=sys.stderr)



        conn.send("environment more\n") 

        time.sleep(2)
        output = conn.recv(65534)
        print("\n " + c_mad_routers[x] + ": \n" + output)

    print("\n\n\n" + str(template_variables) + "\n\n\n", file=sys.stderr)



    tower_files.generate_cfg(template_variables, p_mad_routers[0] + "_" + str(template_variables['site_cd']) + "_7950_dest_migration", str(template_variables['site_cd']), 'odd_7950_dest_migration.j2')
    tower_files.generate_cfg(template_variables, p_mad_routers[1] + "_" + str(template_variables['site_cd']) + "_7950_dest_migration", str(template_variables['site_cd']), 'even_7950_dest_migration.j2')

    
    group = str(template_variables['site_cd']) 
    device1 = p_mad_routers[0] + "_" + group + "_7950_dest_migration.cfg"   
    device2 = p_mad_routers[1] + "_" + group + "_7950_dest_migration.cfg"       
    path = settings.BASE_DIR + settings.STATIC_URL + 'csr_rehome/generated_vars_files/' + group + '/'   


    cfg1 = open(path + p_mad_routers[0] + "_" + group + "_7950_dest_migration.cfg", 'r')
    cfg2 = open(path + p_mad_routers[1] + "_" + group + "_7950_dest_migration.cfg", 'r')
    cfg_content1 = cfg1.readlines()
    cfg_content2 = cfg2.readlines()
    cfg1.close()
    cfg2.close()
    


    context = {"response": str(request.method),
            "path": path,
            "group" : group,
            "vars_1": template_variables, 
            "vars_2": template_variables,
            "vars_file1": group + " 511",
            "vars_file2": group + " 512", 
            "cfg_filepath_1": path + device1,
            "cfg_filepath_2": path + device2,
            "cfg_file1": device1,
            "cfg_file2": device2,
            "cfg_content1": cfg_content1,
            "cfg_content2": cfg_content2,   
            "job_status": "Status",
            "job_message": "Message",

            }

# @users_blueprint.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         db.session.add(User(username=username, email=email))
#         db.session.commit()
#     users = User.query.all()
#     return render_template('index.html', users=users)


# @users_blueprint.route('/users/ping', methods=['GET'])
# def ping_pong():
#     return jsonify({
#         'status': 'success',
#         'message': 'pong!'
#     })


# @users_blueprint.route('/users', methods=['POST'])
# def add_user():
#     post_data = request.get_json()
#     response_object = {
#         'status': 'fail',
#         'message': 'Invalid payload.'
#     }
#     if not post_data:
#         return jsonify(response_object), 400
#     username = post_data.get('username')
#     email = post_data.get('email')
#     try:
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             db.session.add(User(username=username, email=email))
#             db.session.commit()
#             response_object['status'] = 'success'
#             response_object['message'] = f'{email} was added!'
#             return jsonify(response_object), 201
#         else:
#             response_object['message'] = 'Sorry. That email already exists.'
#             return jsonify(response_object), 400
#     except exc.IntegrityError as e:
#         db.session.rollback()
#         return jsonify(response_object), 400
# 
# 
# @users_blueprint.route('/users/<user_id>', methods=['GET'])
# def get_single_user(user_id):
#     """Get single user details"""
#     response_object = {
#         'status': 'fail',
#         'message': 'User does not exist'
#     }
#     try:
#         user = User.query.filter_by(id=int(user_id)).first()
#         if not user:
#             return jsonify(response_object), 404
#         else:
#             response_object = {
#                 'status': 'success',
#                 'data': {
#                     'id': user.id,
#                     'username': user.username,
#                     'email': user.email,
#                     'active': user.active
#                 }
#             }
#             return jsonify(response_object), 200
#     except ValueError:
#         return jsonify(response_object), 404


# @users_blueprint.route('/users', methods=['GET'])
# def get_all_users():
#     """Get all users"""
#     response_object = {
#         'status': 'success',
#         'data': {
#             'users': [user.to_json() for user in User.query.all()]
#         }
#     }
#     return jsonify(response_object), 200
