# -*- coding: utf-8 -*-
from pyparsing import Optional, Literal, QuotedString, Word, Or, ZeroOrMore, OneOrMore, White, Group, Combine, Suppress
from pyparsing import alphas, nums, printables, restOfLine, lineEnd
from pyparsing import ParseException

def toInt(s, loc, toks):
    return int(toks[0])


def maybeToInt(s, loc, toks):
    if all(x.isdigit() for x in toks[0]):
        return int(toks[0])
    else:
        return toks[0]


pp_pri = Combine(Suppress(Literal("<")) + Word(nums, min=1, max=3) 
	+ Suppress(Literal(">"))).setParseAction(toInt).setResultsName('pri')
pp_key = Word(alphas)
pp_value = Or([Word(printables), QuotedString('"')])
pp_kvpair = pp_key + Suppress(Literal("=")) + pp_value
pp_log_message = Group(pp_pri.setResultsName("pri") + OneOrMore(pp_kvpair).setResultsName('msg'))



class ParseError(Exception):
    def __init__(self, description, message):
        self.description = description
        self.message = message

    def __repr__(self):
        return '{0}({1!r}, {2!r})'.format(self.__class__.__name__, self.description, self.message)  # pragma: no cover

    def __str__(self):
        return '{0}: {1!r}'.format(self.description, self.message)  # pragma: no cover
        

class SyslogMessage:
    def __init__(self, pri, msg, log_type, log_subtype, log_stamac, log_action):
        self.pri = pri
        self.msg = msg
        self.log_type = log_type
        self.log_subtype = log_subtype
        self.log_stamac = log_stamac
        self.log_action = log_action

    @classmethod
    def parse(cls, message_string):
        try:
            groups = pp_log_message.parseString(message_string)
            pri = groups[0]['pri']
            msg_list = groups[0]['msg']
            msg = dict(zip(msg_list[0::2], msg_list[1::2]))
        except ParseException:
            raise ParseError('Unable to parse message', message_string)
        log_type = None
        log_subtype = None
        log_stamac = None
        log_action = None

        if 'type' in msg:
            log_type = msg['type']
        if 'subtype' in msg:
            log_subtype = msg['subtype']
        if 'stamac' in msg:
            log_stamac = msg['stamac']
        if 'action' in msg:
            log_action = msg['action']
        return cls(pri, msg, log_type, log_subtype, log_stamac, log_action)


if __name__ == '__main__':
    text="""<37>date=2016-08-16 time=20:34:03 devname=FGT90D3Z15016773 devid=FGT90D3Z15016773 logid=0104043573 type=event subtype=wireless level=notice vd="root" logdesc="Wireless client authenticated" sn="FP221C3X15010403" ap="FP221C3X15010403" vap="wifi" ssid="fortinet" radioid=1 user="N/A" group="N/A" stamac=78:d7:5f:04:00:78 srcip=0.0.0.0 channel=1 radioband="802.11n" security="Captive Portal" encryption="N/A" action="client-authentication" reason="Reserved 0" msg="Client 78:d7:5f:04:00:78 authenticated."
            ('192.168.0.180 : ', '<38>date=2016-08-16 time=20:34:06 devname=FGT90D3Z15016773 devid=FGT90D3Z15016773 logid=0100026001 type=event subtype=system level=information vd="root" logdesc="DHCP Ack log" interface="wifi" dhcp_msg="Ack" mac=78:D7:5F:04:00:78 ip=192.168.10.8 lease=604800 hostname="XiaodondeiPhone" msg="DHCP server sends a DHCPACK"')
            2016-08-16 20:23:22,665 INFO: <38>date=2016-08-16 time=20:34:06 devname=FGT90D3Z15016773 devid=FGT90D3Z15016773 logid=0100026001 type=event subtype=system level=information vd="root" logdesc="DHCP Ack log" interface="wifi" dhcp_msg="Ack" mac=78:D7:5F:04:00:78 ip=192.168.10.8 lease=604800 hostname="XiaodondeiPhone" msg="DHCP server sends a DHCPACK"
            """
    log = SyslogMessage.parse(text)
    print log.log_stamac