#include "hdrs/sample.h"

#include <string>

namespace factory
{

const static std::string& temp(int a, int b) 
{
    return std::string("a");
} 

int Run(int argc, char* argv[])
{
    utils::Log("sample");
    return 0;
}

} // namespace factory
