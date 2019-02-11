/*
 * CassandraBackend - a high performance Cassandra based backend for PowerDNS written by
 * Sumit Kumar, 2015
 *
 * The license will be the same as the ones used in powerdns authorative server
 */
/*
 * cassandrabackend.cc
 *
 *  Created on: 11-May-2015
 *      Author: sumit_kumar
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include "pdns/utility.hh"
#include "pdns/dnsbackend.hh"
#include "pdns/dns.hh"
#include "pdns/dnspacket.hh"
#include "pdns/pdnsexception.hh"
#include "pdns/logger.hh"
#include <signal.h>
#include "pdns/arguments.hh"
#include "pdns/base32.hh"
#include "pdns/lock.hh"
#include <iostream>
#include "cassandradbmanager.h"
#include <string.h>
#include <vector>
#include <boost/tokenizer.hpp>
#include <boost/foreach.hpp>
#include "backendutil.cc"

#if 0
#define DEBUGLOG(msg) g_log<<Logger::Error<<msg
#else
#define DEBUGLOG(msg) do {} while(0)
#endif

class CassandraBackend : public DNSBackend
{

private:
  vector<backendrecord> backendRecords;
  int recordIndex = 0;
  int totalSize = 0;
  domainlookuprecords record;
  std::string domain;
  std::string queryType;

  bool hasEnding (std::string const &fullString, std::string const &ending) {
      if (fullString.length() >= ending.length()) {
          return (0 == fullString.compare (fullString.length() - ending.length(), ending.length(), ending));
      } else {
          return false;
      }
  }
public:
  CassandraBackend(const string &suffix) {
	  g_log << Logger::Info << "[CassandraBackend] Launching CassandraBackend instance " << endl;
	  setArgPrefix("cassandra"+suffix);
	 try {
		std::string seed_nodes = getArg("seed-nodes");
		int port = getArgAsNum("port");
		std::string username = getArg("username");
		std::string password = getArg("password");
		std::string keyspace = getArg("keyspace");
		int core_connections = getArgAsNum("core-connections");
		int max_connections = getArgAsNum("max-connections");
		int max_concurrent_creations = getArgAsNum("max-concurrent-creations");
		int num_io_threads = getArgAsNum("num-io-threads");
		int protocol_version = getArgAsNum("protocol-version");
		int queue_size_io = getArgAsNum("queue-size-io");
		int queue_size_event = getArgAsNum("queue-size-event");
		int reconnect_wait_time = getArgAsNum("reconnect-wait-time");
		int concurrent_requests_threshold = getArgAsNum("concurrent-requests-threshold");
		int connect_timeout = getArgAsNum("connect-timeout");
		int request_timeout = getArgAsNum("request-timeout");
		int enable_load_balance_round_robin = getArgAsNum("enable-load-balance-round-robin");
		int enable_token_aware_routing = getArgAsNum("enable-token-aware-routing");
		int enable_latency_aware_routing = getArgAsNum("enable-latency-aware-routing");
		int enable_tcp_nodelay = getArgAsNum("enable-tcp-nodelay");
		int enable_tcp_keepalive = getArgAsNum("enable-tcp-keepalive");

//		g_log << Logger::Info << " cassandra-seed-nodes " << seed_nodes << " cassandra-keyspace " << keyspace << endl;
//		g_log << Logger::Info << " cassandra-username " << username << " cassandra-password " << password << endl;
//		g_log << Logger::Info << " cassandra-core-connections " << core_connections << " cassandra-max_connections " << max_connections << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-protocol-version " << protocol_version << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-max-concurrent-creations " << max_concurrent_creations << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-queue-size-io " << queue_size_io << " cassandra-queue-size-event " << queue_size_event << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-reconnect-wait-time " << reconnect_wait_time << " cassandra-concurrent-requests-threshold " << concurrent_requests_threshold << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-connect-timeout " << connect_timeout << " cassandra-request-timeout " << request_timeout << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-enable-load-balance-round-robin " << enable_load_balance_round_robin << " cassandra-enable-token-aware-routing " << enable_token_aware_routing << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-enable-latency-aware-routing " << enable_latency_aware_routing << endl;
//		g_log << Logger::Info << "[cassandradbmanager] cassandra-enable-tcp-nodelay " << enable_tcp_nodelay << " cassandra-enable-tcp-keepalive " << enable_tcp_keepalive << endl;
		cassandradbmanager::seed_nodes = seed_nodes;
		cassandradbmanager::port = port;
		cassandradbmanager::username = username;
		cassandradbmanager::password = password;
		cassandradbmanager::keyspace = keyspace;
		cassandradbmanager::core_connections = core_connections;
		cassandradbmanager::max_connections = max_connections;
		cassandradbmanager::max_concurrent_creations = max_concurrent_creations;
		cassandradbmanager::num_io_threads = num_io_threads;
		cassandradbmanager::protocol_version = protocol_version;
		cassandradbmanager::queue_size_io = queue_size_io;
		cassandradbmanager::queue_size_event = queue_size_event;
		cassandradbmanager::reconnect_wait_time = reconnect_wait_time;
		cassandradbmanager::concurrent_requests_threshold = concurrent_requests_threshold;
		cassandradbmanager::connect_timeout = connect_timeout;
		cassandradbmanager::request_timeout = request_timeout;
		cassandradbmanager::enable_load_balance_round_robin = enable_load_balance_round_robin;
		cassandradbmanager::enable_token_aware_routing = enable_token_aware_routing;
		cassandradbmanager::enable_latency_aware_routing = enable_latency_aware_routing;
		cassandradbmanager::enable_tcp_nodelay = enable_tcp_nodelay;
		cassandradbmanager::enable_tcp_keepalive = enable_tcp_keepalive;
		if(::arg().mustDo("query-logging")) {
			g_log << Logger::Info << "[CassandraBackend] Connecting to cassandra cluster " << endl;
		}
		cassandradbmanager::getInstance();
		if(::arg().mustDo("query-logging")) {
			g_log << Logger::Info << "[CassandraBackend] Connection to cassandra cluster successful " << endl;
		}

	 } catch (const ArgException &A) {
		g_log << Logger::Error << "[CassandraBackend]" << " Fatal argument error: "<< A.reason << endl;
		throw;
	 } catch (...) {
		throw;
	 }

  }

  bool list(const DNSName& target, int domain_id, bool include_disabled=false)
  {
		try {
			//Right now there is no disabled field in the domain field
			cassandradbmanager *sc1 = cassandradbmanager::getInstance();
			const char* query =
					"SELECT domain FROM pdns.domain_id_domain_relation WHERE domain_id = ?";
			if(::arg().mustDo("query-logging")) {
				g_log << Logger::Info << "[CassandraBackend] SELECT domain FROM pdns.domain_id_domain_relation WHERE domain_id = " << domain_id << endl;
			}
			string param = sc1->executeAxfrQuery(query, domain_id);
			if (param.size() > 0) {
				this->queryType = "ANY";
				fetchdata_multiple(param);
				return true;
			} else {
				return false;
			}
		} catch (const std::exception &exc) {
			g_log << Logger::Critical << "LIST exception " << exc.what() << endl;
			throw PDNSException("LIST exception");
		} catch (...) {
			g_log << Logger::Critical << "Unknown exception in LIST" << endl;
			throw PDNSException("Unknown exception in LIST");
		}
		return false;
	}


  bool getSOA(const DNSName &name, SOAData &soadata) {
		try {
			domain = name.toStringNoDot();
			if(::arg().mustDo("query-logging")) {
			g_log << Logger::Info << "[CassandraBackend] Recieved getSOA " << domain << endl;
			}
			fetchdata();
			vector<backendrecord>::const_iterator cii;
			for(cii=backendRecords.begin(); cii!=backendRecords.end(); cii++) {
			//for (int index = 0; index < totalSize; ++index) {
				backendrecord backendRecord = (*cii);//backendRecords[index];
				if (backendRecord.getType() == QType::SOA) {
					if(::arg().mustDo("query-logging")) {
						g_log << Logger::Info << "[CassandraBackend] SOA record found" << endl;
					}
					soadata.db = this;
					//Data format :: domain_id nameserver	hostname    serial refresh retry expiry default_ttl
					std::string data = backendRecord.getRecord();
					boost::char_separator<char> delimiter("#");
					boost::tokenizer<boost::char_separator<char> > tokens(data,
							delimiter);
					int rec_index = 0;
					BOOST_FOREACH(std::string const& token, tokens) {
						switch (rec_index) {
						case 0:
							soadata.domain_id = (uint32_t) atoi(token.c_str());
							break;
						case 1:
							soadata.nameserver = DNSName(token.c_str());
							break;
						case 2:
							soadata.hostmaster = DNSName(token.c_str());
							break;
						case 3:
							soadata.serial = (uint32_t) atoi(token.c_str());
							break;
						case 4:
							soadata.refresh = (uint32_t) atoi(token.c_str());
							break;
						case 5:
							soadata.retry = (uint32_t) atoi(token.c_str());
							break;
						case 6:
							soadata.expire = (uint32_t) atoi(token.c_str());
							break;
						case 7:
							soadata.default_ttl = (uint32_t) atoi(token.c_str());
							break;
						default:
							g_log << Logger::Info << "[CassandraBackend]Extra params while parsing" << endl;
						}
						soadata.ttl = backendRecord.getTtl();
						soadata.qname = DNSName(this->domain);
						rec_index++;
					}
					if(::arg().mustDo("query-logging")) {
						g_log << Logger::Info << "[CassandraBackend] SOA serial "
							<< soadata.serial << " refresh " << soadata.refresh
							<< " retry " << soadata.retry << " expire "
							<< soadata.expire << " default_ttl "
							<< soadata.default_ttl << " domain_id "
							<< soadata.domain_id << " ttl " << soadata.ttl
							<< " nameserver " << soadata.nameserver
							<< " hostmaster " << soadata.hostmaster << endl;
					}
					clear(false);
					return true;
				}
			}
			clear(false);
			return false;
		} catch (const std::exception &exc) {
			g_log << Logger::Critical << "[CassandraBackend] SOA exception " << exc.what() << endl;
			throw PDNSException("SOA exception");
		} catch (...) {
			g_log << Logger::Critical << "[CassandraBackend] Unknown exception in SOA" << endl;
			throw PDNSException("Unknown exception in SOA");
		}
		return false;
	}

  void lookup(const QType &type, const DNSName &qname, DNSPacket *pkt_p, int zoneId)
  {
		try {
			queryType = type.getName();
			domain = qname.toStringNoDot();
			recordIndex = 0;
			totalSize = 0;
			if(::arg().mustDo("query-logging")) {
				g_log << Logger::Info << "[CassandraBackend] Recieved lookup query for " << queryType << " " << domain << " " << endl;
			}
			fetchdata();
		} catch (const std::exception &exc) {
			g_log << Logger::Critical << "[CassandraBackend] lookup exception " << exc.what() << endl;
			throw PDNSException("lookup exception");
		} catch (...) {
			g_log << Logger::Critical << "[CassandraBackend] Unknown exception in lookup" << endl;
			throw PDNSException("Unknown exception in lookup");
		}
	}

  void fetchdata()
  {
	  cassandradbmanager *sc1 = cassandradbmanager::getInstance();
	  const char* query = "SELECT domain, recordmap, creation_time FROM pdns.domain_lookup_records WHERE domain = ?";
	  if(::arg().mustDo("query-logging")) {
		  g_log << Logger::Info << "[CassandraBackend] SELECT domain, recordmap, creation_time FROM pdns.domain_lookup_records WHERE domain = "<<domain<< endl;
	  }
	  sc1->executeQuery(query,&record,domain.c_str(),"ANY");
	  backendRecords = backendutil::parse(&record);
	  this->totalSize = record.size;
  }

  void fetchdata_multiple(string param)
  {
	  cassandradbmanager *sc1 = cassandradbmanager::getInstance();
	  string query = "SELECT domain, recordmap, creation_time FROM pdns.domain_lookup_records WHERE domain in (";
	  query.append(param);query.append(")");
	  if(::arg().mustDo("query-logging")) {
		  g_log << Logger::Info << "[CassandraBackend] "<<query<<endl;
	  }
	  sc1->executeQuery(query.c_str(),&record,"ANY");
	  backendRecords = backendutil::parse(&record);
	  this->totalSize = record.size;
  }

  bool get(DNSResourceRecord &rr)
  {
		try {
			if (this->totalSize == 0 || recordIndex >= this->totalSize) {
				clear();
				return false;
			}
			backendrecord backendRecord = backendRecords[recordIndex];
			if ((backendRecord.getType() != QType::SOA) && (backendRecord.getType().getName() == queryType || queryType == "ANY")) {
				rr.qname = DNSName(domain);
				rr.qtype = backendRecord.getType();
				rr.ttl = backendRecord.getTtl();
				rr.content = backendRecord.getRecord();
			} else {
				if(::arg().mustDo("query-logging")) {
					g_log << Logger::Info << "[CassandraBackend] Record skipped, Type requested " << queryType << " Record type " << backendRecord.getType().getName() << endl;
				}
			}
			if (recordIndex < this->totalSize) {
				recordIndex++;
				return true;
			} else {
				recordIndex++;
				return false;
			}
		} catch (const std::exception &exc) {
			g_log << Logger::Critical << "[CassandraBackend] GET exception " << exc.what() << endl;
			throw PDNSException("GET exception");
		} catch (...) {
			g_log << Logger::Critical << "[CassandraBackend] Unknown exception in GET" << endl;
			throw PDNSException("Unknown exception in GET");
		}
		return false;
	}

  void clear(bool all=true) {
	  recordIndex = 0;totalSize = 0;queryType.clear();backendRecords.clear();record.clear();
	  if(all) {
		  domain.clear();
	  }
  }

};

/* SECOND PART */

class CassandraBackendFactory : public BackendFactory
{
public:
  CassandraBackendFactory() : BackendFactory("cassandra") {}

  void declareArguments(const string &suffix="")
  {
	declare(suffix,"seed-nodes","seed nodes","myseeds");
	declare(suffix,"port","port","9042");
	declare(suffix,"username","user name","myusername");
	declare(suffix,"password","password","mypassword");
	declare(suffix,"keyspace","keyspace","mykeyspace");
	declare(suffix,"core-connections","core connections","40");
	declare(suffix,"max-connections","max connections","100");
	declare(suffix,"max-concurrent-creations","max concurrent creations","100");
	declare(suffix,"num-io-threads","num io threads","1");
	declare(suffix,"protocol-version","protocol version","3");
	declare(suffix,"queue-size-io","queue size io","4096");
	declare(suffix,"queue-size-event","queue size event","4096");
	declare(suffix,"reconnect-wait-time","reconnect wait time","2000");
	declare(suffix,"concurrent-requests-threshold","concurrent requests threshold","100");
	declare(suffix,"connect-timeout","connect timeout","5000");
	declare(suffix,"request-timeout","request timeout","12000");
	declare(suffix,"enable-load-balance-round-robin","enable load balance round robin","1");
	declare(suffix,"enable-token-aware-routing","enable token aware routing","0");
	declare(suffix,"enable-latency-aware-routing","enable latency aware routing","0");
	declare(suffix,"enable-tcp-nodelay","enable tcp nodelay","0");
	declare(suffix,"enable-tcp-keepalive","enable tcp keepalive","0");
  }

  DNSBackend *make(const string &suffix="")
  {
    return new CassandraBackend(suffix);
  }
};

/* THIRD PART */

class CassandraBackendLoader
{
public:
  CassandraBackendLoader()
  {
    BackendMakers().report(new CassandraBackendFactory);
    g_log << Logger::Info << "[cassandrabackendbackend] This is the cassandrabackend backend version  1" << endl;
  }
};

static CassandraBackendLoader cassandrabackendloader;
