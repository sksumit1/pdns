#!/usr/bin/env python
import dns
import clientsubnetoption
from dnsdisttests import DNSDistTest
from datetime import datetime, timedelta

class TestEDNSSelfGenerated(DNSDistTest):
    """
    Check that dnsdist sends correct EDNS data on
    self-generated (RCodeAction(), TCAction(), Lua..)
    """

    _config_template = """
    addAction("rcode.edns-self.tests.powerdns.com.", RCodeAction(dnsdist.REFUSED))
    addAction("tc.edns-self.tests.powerdns.com.", TCAction())

    function luarule(dq)
      return DNSAction.Nxdomain, ""
    end

    addLuaAction("lua.edns-self.tests.powerdns.com.", luarule)

    addAction("spoof.edns-self.tests.powerdns.com.", SpoofAction({'192.0.2.1', '192.0.2.2'}))

    setPayloadSizeOnSelfGeneratedAnswers(1042)

    newServer{address="127.0.0.1:%s"}
    """

    def testNoEDNS(self):
        """
        EDNS on Self-Generated: No existing EDNS
        """
        name = 'no-edns.rcode.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN')
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.REFUSED)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        name = 'no-edns.tc.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN')
        expectedResponse = dns.message.make_response(query)
        expectedResponse.flags |= dns.flags.TC

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        name = 'no-edns.lua.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN')
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.NXDOMAIN)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        name = 'no-edns.spoof.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN')
        # dnsdist set RA = RD for spoofed responses
        query.flags &= ~dns.flags.RD
        expectedResponse = dns.message.make_response(query)
        expectedResponse.answer.append(dns.rrset.from_text(name,
                                                           60,
                                                           dns.rdataclass.IN,
                                                           dns.rdatatype.A,
                                                           '192.0.2.1', '192.0.2.2'))

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

    def testWithEDNSNoDO(self):
        """
        EDNS on Self-Generated: EDNS with DO=0
        """
        name = 'edns-no-do.rcode.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.REFUSED)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-no-do.tc.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.flags |= dns.flags.TC

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-no-do.lua.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.NXDOMAIN)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-no-do.spoof.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        # dnsdist set RA = RD for spoofed responses
        query.flags &= ~dns.flags.RD
        expectedResponse = dns.message.make_response(query)
        expectedResponse.answer.append(dns.rrset.from_text(name,
                                                           60,
                                                           dns.rdataclass.IN,
                                                           dns.rdatatype.A,
                                                           '192.0.2.1', '192.0.2.2'))

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertFalse(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

    def testWithEDNSWithDO(self):
        """
        EDNS on Self-Generated: EDNS with DO=1
        """
        name = 'edns-do.rcode.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=True)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.REFUSED)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-do.tc.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=True)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.flags |= dns.flags.TC

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-do.lua.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=True)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.NXDOMAIN)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-do.spoof.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=True)
        # dnsdist set RA = RD for spoofed responses
        query.flags &= ~dns.flags.RD
        expectedResponse = dns.message.make_response(query)
        expectedResponse.answer.append(dns.rrset.from_text(name,
                                                           60,
                                                           dns.rdataclass.IN,
                                                           dns.rdatatype.A,
                                                           '192.0.2.1', '192.0.2.2'))

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

    def testWithEDNSNoOptions(self):
        """
        EDNS on Self-Generated: EDNS with options in the query
        """
        name = 'edns-options.rcode.edns-self.tests.powerdns.com.'
        ecso = clientsubnetoption.ClientSubnetOption('127.0.0.1', 24)
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, options=[ecso], payload=512, want_dnssec=True)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.REFUSED)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-options.tc.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, options=[ecso], payload=512, want_dnssec=True)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.flags |= dns.flags.TC

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-options.lua.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, options=[ecso], payload=512, want_dnssec=True)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.NXDOMAIN)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        name = 'edns-options.spoof.edns-self.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, options=[ecso], payload=512, want_dnssec=True)
        # dnsdist set RA = RD for spoofed responses
        query.flags &= ~dns.flags.RD
        expectedResponse = dns.message.make_response(query)
        expectedResponse.answer.append(dns.rrset.from_text(name,
                                                           60,
                                                           dns.rdataclass.IN,
                                                           dns.rdatatype.A,
                                                           '192.0.2.1', '192.0.2.2'))

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageEDNSWithoutOptions(expectedResponse, receivedResponse)
        self.assertTrue(receivedResponse.ednsflags & dns.flags.DO)
        self.assertEquals(receivedResponse.payload, 1042)


class TestEDNSSelfGeneratedDisabled(DNSDistTest):
    """
    Check that dnsdist does not send EDNS data on
    self-generated (RCodeAction(), TCAction(), Lua..) when disabled
    """

    _config_template = """
    setAddEDNSToSelfGeneratedResponses(false)

    addAction("rcode.edns-self-disabled.tests.powerdns.com.", RCodeAction(dnsdist.REFUSED))
    addAction("tc.edns-self-disabled.tests.powerdns.com.", TCAction())

    function luarule(dq)
      return DNSAction.Nxdomain, ""
    end

    addLuaAction("lua.edns-self-disabled.tests.powerdns.com.", luarule)

    addAction("spoof.edns-self-disabled.tests.powerdns.com.", SpoofAction({'192.0.2.1', '192.0.2.2'}))

    setPayloadSizeOnSelfGeneratedAnswers(1042)

    newServer{address="127.0.0.1:%s"}
    """

    def testWithEDNSNoDO(self):
        """
        EDNS on Self-Generated (disabled): EDNS with DO=0
        """
        name = 'edns-no-do.rcode.edns-self-disabled.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.REFUSED)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        name = 'edns-no-do.tc.edns-self-disabled.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.flags |= dns.flags.TC

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        name = 'edns-no-do.lua.edns-self-disabled.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        expectedResponse = dns.message.make_response(query)
        expectedResponse.set_rcode(dns.rcode.NXDOMAIN)

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        name = 'edns-no-do.spoof.edns-self-disabled.tests.powerdns.com.'
        query = dns.message.make_query(name, 'A', 'IN', use_edns=True, payload=4096, want_dnssec=False)
        # dnsdist set RA = RD for spoofed responses
        query.flags &= ~dns.flags.RD
        expectedResponse = dns.message.make_response(query)
        expectedResponse.answer.append(dns.rrset.from_text(name,
                                                           60,
                                                           dns.rdataclass.IN,
                                                           dns.rdatatype.A,
                                                           '192.0.2.1', '192.0.2.2'))

        (_, receivedResponse) = self.sendUDPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)

        (_, receivedResponse) = self.sendTCPQuery(query, response=None, useQueue=False)
        self.checkMessageNoEDNS(expectedResponse, receivedResponse)
