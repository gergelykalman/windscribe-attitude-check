#include <string>
#include <fstream>
#include <sstream>

#include <iostream>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>


#define UNUSED(x) (void)(x)

enum CmdDnsManager {
    kResolvConf,
    kSystemdResolved,
    kNetworkManager,
};

struct CMD_START_OPENVPN {
    std::string exePath;
    std::string executable;
    std::string config;
    std::string arguments;
    CmdDnsManager dnsManager; // Linux only
    bool isCustomConfig;
};

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        void serialize(Archive &ar, CMD_START_OPENVPN &a, const unsigned int version)
        {
            UNUSED(version);
            ar & a.exePath;
            ar & a.executable;
            ar & a.config;
            ar & a.arguments;
            ar & a.dnsManager;
            ar & a.isCustomConfig;
        }
    }
}


int main()
{
	CMD_START_OPENVPN cmd;
	cmd.exePath = "/Applications/Windscribe.app/Contents/Helpers/";
	cmd.executable = "windscribeopenvpn";
	cmd.config = "CCCC";
	cmd.arguments = "`/tmp/test.sh`";
	cmd.dnsManager = kResolvConf;
	cmd.isCustomConfig = 0;


	std::stringstream stream;
	boost::archive::text_oarchive oa(stream, boost::archive::no_header);
	oa << cmd;

	std::cout << stream.str();

	// verify in-place
/*	std::istringstream stream2(stream.str());
	boost::archive::text_iarchive ia(stream2, boost::archive::no_header);

	CMD_START_OPENVPN cmd2;
	ia >> cmd2;

	std::cout << "Starting\n";

	std::cout << cmd2.exePath + "\n";
	std::cout << cmd2.executable + "\n";
	std::cout << cmd2.config + "\n";
	std::cout << cmd2.arguments + "\n";
	std::cout << cmd2.dnsManager + "\n";
	std::cout << cmd2.isCustomConfig + "\n";

	std::cout << "Done\n";*/
}

