#!/usr/bin/env python
#
#

import subprocess, sys, logging

def get_iftable(host, community):
    cmd = "snmptable -Cf ,  -c " + community + " -v 2c -M /var/lib/snmp/mibs/ietf/:/var/lib/snmp/mibs/iana/ -m IF-MIB " + host + "  ifTable"
    cmd = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = cmd.communicate()
    if cmd.returncode != 0:
        # output[1] is stderr
        logging.error("snmptable failed: %s" % (output[1]))
        return None
    output = output[0].split("\n")
    output = output[2:]
    header = output[0]
    header = header.split(',')
    output = output[1:]

    ret = {}
    for l in output:
        l = l.split(',')
        if len(l) != len(header):
            continue
        ret[l[0]] = {}
        for idx, item in enumerate(header):
            ret[l[0]][item] = l[idx]

    return ret

#['ifIndex', 'ifDescr', 'ifType', 'ifMtu', 'ifSpeed', 'ifPhysAddress', 'ifAdminStatus', 'ifOperStatus', 'ifLastChange', 'ifInOctets', 'ifInUcastPkts', 'ifInNUcastPkts', 'ifInDiscards', 'ifInErrors', 'ifInUnknownProtos', 'ifOutOctets', 'ifOutUcastPkts', 'ifOutNUcastPkts', 'ifOutDiscards', 'ifOutErrors', 'ifOutQLen', 'ifSpecific']

things = ['ifDescr', 'ifSpeed', 'ifInOctets', 'ifOutOctets']

def get_speeds_snmp(host, ifname = 'ppp0', community = 'public'):
    table = get_iftable(host, community)
    if not table:
        return (None, None)
    inoct = outoct = None
    for idx in list(table.keys()):
        if table[idx]['ifType'] == 'ethernetCsmacd' or table[idx]['ifType'] == 'ppp':
            if table[idx]['ifDescr'] == ifname:
                inoct = int(table[idx]['ifInOctets'])
                outoct = int(table[idx]['ifOutOctets'])
    return (inoct, outoct)

if __name__ == "__main__":
    args = sys.argv[1:]
    print(get_speeds_snmp(*args))
